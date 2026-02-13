"""
Drum Kit Mixer widget.

Provides 37 vertical sliders for controlling the master level and
all 36 drum partial levels.
"""

from typing import Dict, Optional, Iterator
from dataclasses import dataclass

from decologr import Decologr as log
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QGroupBox, QWidget, QVBoxLayout,
                               QHBoxLayout, QSizePolicy, QGridLayout, QLabel, QScrollArea, QSlider)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import (
    JDXiSysExAddress,
    JDXiSysExAddressStartMSB,
    JDXiSysExOffsetProgramLMB,
    JDXiSysExOffsetTemporaryToneUMB,
)
from jdxi_editor.midi.data.drum.data import DRUM_PARTIAL_NAMES
from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParam
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.display.digital import DigitalTitle
from jdxi_editor.ui.widgets.slider import Slider


@dataclass(frozen=True)
class DrumLane:
    name: str
    partials: list[str]
    colspan: int = 1


@dataclass(frozen=True)
class DrumLaneRow:
    title: str
    lanes: list[DrumLane]

    # iteration: for lane in row
    def __iter__(self) -> Iterator["DrumLane"]:
        return iter(self.lanes)

    # len(row)
    def __len__(self) -> int:
        return len(self.lanes)

    # row[index]
    def __getitem__(self, index: int) -> "DrumLane":
        return self.lanes[index]


DRUM_MIXER_LANE_ROWS: list[DrumLaneRow] = [
    DrumLaneRow(
        title="Low End",
        lanes=[
            DrumLane(name="Kick", partials=["BD1", "BD2", "BD3"]),
            DrumLane(name="Toms", partials=["TOM1", "TOM2", "TOM3"]),
        ],
    ),

    DrumLaneRow(
        title="Snares",
        lanes=[
            DrumLane(name="Snare", partials=["SD1", "SD2", "SD3", "SD4", "RIM", "CLAP"], colspan=2),
        ],
    ),

    DrumLaneRow(
        title="Backbeat",
        lanes=[
            DrumLane(name="Hi-Hat", partials=["CHH", "PHH", "OHH"]),
            DrumLane(name="Cymbals", partials=["CYM1", "CYM2", "CYM3"]),
        ],
    ),

    DrumLaneRow(
        title="Time",
        lanes=[
            DrumLane(name="Percussion", partials=["PRC1", "PRC2", "PRC3", "PRC4", "PRC5"]),
            DrumLane(name="Other", partials=["HIT", "OTH1", "OTH2"]),
        ],
    ),

    DrumLaneRow(
        title="Notes",
        lanes=[
            DrumLane(
                name="Chromatic",
                partials=["D4", "Eb4", "E4", "F4", "F#4", "G4", "G#4", "A4", "Bb4", "B4", "C5", "C#5"],
                colspan=2,
            ),
        ],
    ),
]


class DrumLevelStrip(QWidget):
    STRIP_WIDTH = 46

    def __init__(self, label, param_index):
        super().__init__()

        self.setFixedWidth(self.STRIP_WIDTH)

        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(2, 2, 2, 2)

        self.name = QLabel(label)
        self.name.setAlignment(Qt.AlignHCenter)

        self.slider = QSlider(Qt.Vertical)
        self.slider.setMinimumHeight(140)

        self.value = QLabel("0")
        self.value.setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.name)
        layout.addWidget(self.slider, 1)
        layout.addWidget(self.value)


class MasterLevelStrip(DrumLevelStrip):
    def __init__(self):
        super().__init__("KIT", 0)
        self.name.setText("MASTER")


class MixerLane(QGroupBox):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)

        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(6, 10, 6, 6)
        outer_layout.setSpacing(4)

        self._strip_container = QWidget(self)
        self._strip_layout = QHBoxLayout(self._strip_container)

        self._strip_layout.setContentsMargins(2, 2, 2, 2)
        self._strip_layout.setSpacing(3)

        outer_layout.addWidget(self._strip_container)

    # public API only
    def add_strip(self, widget: QWidget) -> None:
        self._strip_layout.addWidget(widget)


class DrumKitMixer(QWidget):
    """
    Drum Kit Mixer widget with 37 vertical sliders:
    - 1 Master slider (Kit Level)
    - 36 Partial sliders (one for each drum partial)
    """

    def __init__(
            self,
            midi_helper: Optional[MidiIOHelper] = None,
            parent: Optional[QWidget] = None,
    ):
        """
        Initialize the Drum Kit Mixer.

        :param midi_helper: Optional MIDI helper for sending messages
        :param parent: Optional parent widget
        """
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.mixer_sliders: Dict[str, Slider] = {}
        self.partial_addresses: Dict[int, JDXiSysExAddress] = {}

        # Base address for drum kit common area
        # Base address for drum kit common area (stored for reference, not currently used)
        # Match the address used by the editor (TEMPORARY_TONE, not TEMPORARY_PROGRAM)
        self.base_address = JDXiSysExAddress(
            JDXiSysExAddressStartMSB.TEMPORARY_TONE,
            JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT,
            JDXiSysExOffsetProgramLMB.COMMON,
            0x00,
        )

        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the mixer UI with 37 vertical sliders."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Title
        title_label = DigitalTitle("Drum Kit Mixer")
        self.setStyleSheet(JDXi.UI.Style.ADSR)
        main_layout.addWidget(title_label)

        # Scroll area for sliders
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Container widget for sliders
        sliders_widget = QWidget()

        sliders_layout = QGridLayout()  # the actual mixer grid

        sliders_hlayout = QHBoxLayout(sliders_widget)  # install on widget
        sliders_hlayout.addStretch(1)
        sliders_hlayout.addLayout(sliders_layout)
        sliders_hlayout.addStretch(1)

        sliders_layout.setSpacing(15)
        sliders_layout.setContentsMargins(10, 10, 10, 10)

        col = 0

        # --- MASTER BUS ---
        master_lane = self._create_lane_group("Master")
        sliders_layout.addWidget(master_lane, 0, 0)

        master_strip = self._build_master_strip()
        master_lane.add_strip(master_strip)

        # --- DRUM GROUP MATRIX ---
        for row, lane_row in enumerate(DRUM_MIXER_LANE_ROWS, start=1):

            grid_col = 0

            for lane in lane_row:
                group = self._create_lane_group(lane.name)

                sliders_layout.addWidget(group, row, grid_col, 1, lane.colspan)

                for partial in lane.partials:
                    idx = DRUM_PARTIAL_NAMES.index(partial)
                    strip = self._build_partial_strip(partial, idx)
                    if strip:
                        group.add_strip(strip)

                grid_col += lane.colspan

        max_cols = max(len(r) for r in DRUM_MIXER_LANE_ROWS)
        for c in range(max_cols):
            sliders_layout.setColumnStretch(c, 1)

        sliders_layout.setRowStretch(len(DRUM_MIXER_LANE_ROWS) + 1, 1)

        scroll_area.setWidget(sliders_widget)
        main_layout.addWidget(scroll_area)

    def _build_partial_strip(self, partial_name: str, partial_index: int) -> DrumLevelStrip:

        if not (1 <= partial_index <= 36):
            log.warning(f"Invalid partial index: {partial_index}", scope=self.__class__.__name__)
            return None

        from jdxi_editor.midi.data.address.address import JDXiSysExOffsetDrumKitLMB

        lmb_attr = f"DRUM_KIT_PART_{partial_index}"
        if not hasattr(JDXiSysExOffsetDrumKitLMB, lmb_attr):
            log.warning(f"No LMB found for partial {partial_index}")
            return None

        lmb_value = getattr(JDXiSysExOffsetDrumKitLMB, lmb_attr)

        address = JDXiSysExAddress(
            JDXiSysExAddressStartMSB.TEMPORARY_TONE,
            JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT,
            JDXiSysExOffsetProgramLMB(lmb_value),
            0x00,
        )

        self.partial_addresses[partial_index] = address

        strip = DrumLevelStrip(partial_name, partial_index)

        strip.slider.setRange(0, 127)

        strip.slider.valueChanged.connect(
            lambda v, addr=address, pidx=partial_index:
            self._on_partial_level_changed(v, addr, pidx)
        )

        self.mixer_sliders[partial_name] = strip.slider

        return strip

    def _build_master_strip(self) -> MasterLevelStrip:
        address = JDXiSysExAddress(
            JDXiSysExAddressStartMSB.TEMPORARY_TONE,
            JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT,
            JDXiSysExOffsetProgramLMB.COMMON,
            0x00,
        )

        strip = MasterLevelStrip()
        strip.slider.setRange(0, 127)

        strip.slider.valueChanged.connect(
            lambda v, addr=address: self._on_master_level_changed(v, addr)
        )

        self.mixer_sliders["Master"] = strip.slider
        return strip

    def _create_lane_group(self, title: str) -> MixerLane:
        return MixerLane(title, self)

    def _create_master_slider(self, layout: QGridLayout, row: int, col: int) -> None:
        """Create the master (Kit Level) slider."""
        # Use common address for master level
        # Match the address used by the editor (TEMPORARY_TONE, not TEMPORARY_PROGRAM)
        address = JDXiSysExAddress(
            JDXiSysExAddressStartMSB.TEMPORARY_TONE,
            JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT,
            JDXiSysExOffsetProgramLMB.COMMON,
            0x00,
        )

        slider = Slider(
            "Master",
            min_value=0,
            max_value=127,
            midi_helper=self.midi_helper,
            vertical=True,
            show_value_label=True,
            tooltip="Master level for the entire drum kit",
        )

        # Connect slider to send MIDI messages
        slider.valueChanged.connect(lambda v: self._on_master_level_changed(v, address))

        self.mixer_sliders["Master"] = slider

        # Add slider and label to layout
        label = QLabel("Master")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 12px;
                color: {JDXi.UI.Style.FOREGROUND};
                padding: 2px;
            }}
        """
        )
        layout.addWidget(label, row, col)
        layout.addWidget(slider, row + 1, col, 2, 1)  # Span 2 rows for slider

    def _create_partial_slider(
            self,
            layout: QGridLayout,
            row: int,
            col: int,
            partial_name: str,
            partial_index: int,
    ) -> None:
        """
        Create a slider for a drum partial.

        :param layout: Grid layout to add slider to
        :param row: Row position in grid
        :param col: Column position in grid
        :param partial_name: Name of the partial (e.g., "BD1", "SD1")
        :param partial_index: Index of the partial (1-36, corresponds to DRUM_ADDRESSES index)
        """
        # Get address for this partial from DRUM_ADDRESSES
        # partial_index is 1-based (1-36), but DRUM_ADDRESSES[0] is common
        # So we use DRUM_ADDRESSES[partial_index] where partial_index is 1-36
        if partial_index < 1 or partial_index > 36:
            log.warning(
                f"Invalid partial index: {partial_index}", scope=self.__class__.__name__
            )
            return

        # Get the LMB for this partial from AddressOffsetDrumKitLMB
        from jdxi_editor.midi.data.address.address import JDXiSysExOffsetDrumKitLMB

        # Map partial_index (1-36) to DRUM_KIT_PART_X
        lmb_attr = f"DRUM_KIT_PART_{partial_index}"
        if not hasattr(JDXiSysExOffsetDrumKitLMB, lmb_attr):
            log.warning(f"No LMB found for partial {partial_index}")
            return

        lmb_value = getattr(JDXiSysExOffsetDrumKitLMB, lmb_attr)

        # Create address for this partial
        # Match the address used by the editor (TEMPORARY_TONE, not TEMPORARY_PROGRAM)
        address = JDXiSysExAddress(
            JDXiSysExAddressStartMSB.TEMPORARY_TONE,
            JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT,
            JDXiSysExOffsetProgramLMB(lmb_value),
            0x00,
        )

        self.partial_addresses[partial_index] = address

        # Create slider
        slider = Slider(
            partial_name,
            min_value=0,
            max_value=127,
            midi_helper=self.midi_helper,
            vertical=True,
            show_value_label=True,
            tooltip=f"Level for {partial_name}",
        )

        # Connect slider to send MIDI messages
        slider.valueChanged.connect(
            lambda v, addr=address, pidx=partial_index: self._on_partial_level_changed(
                v, addr, pidx
            )
        )

        self.mixer_sliders[partial_name] = slider

        # Add slider and label to layout
        label = QLabel(partial_name)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 11px;
                color: {JDXi.UI.Style.FOREGROUND};
                padding: 2px;
            }}
        """
        )
        # row is already the label row (0, 3, 6, etc.)
        layout.addWidget(label, row, col)
        layout.addWidget(slider, row + 1, col, 2, 1)  # Sliders span 2 rows

    def _create_partial_slider_hlayout(
            self,
            layout: QHBoxLayout,
            partial_name: str,
            partial_index: int,
    ) -> None:
        """
        Create a slider for a drum partial.

        :param layout: Grid layout to add slider to
        :param row: Row position in grid
        :param col: Column position in grid
        :param partial_name: Name of the partial (e.g., "BD1", "SD1")
        :param partial_index: Index of the partial (1-36, corresponds to DRUM_ADDRESSES index)
        """
        # Get address for this partial from DRUM_ADDRESSES
        # partial_index is 1-based (1-36), but DRUM_ADDRESSES[0] is common
        # So we use DRUM_ADDRESSES[partial_index] where partial_index is 1-36
        if partial_index < 1 or partial_index > 36:
            log.warning(
                f"Invalid partial index: {partial_index}", scope=self.__class__.__name__
            )
            return

        # Get the LMB for this partial from AddressOffsetDrumKitLMB
        from jdxi_editor.midi.data.address.address import JDXiSysExOffsetDrumKitLMB

        # Map partial_index (1-36) to DRUM_KIT_PART_X
        lmb_attr = f"DRUM_KIT_PART_{partial_index}"
        if not hasattr(JDXiSysExOffsetDrumKitLMB, lmb_attr):
            log.warning(f"No LMB found for partial {partial_index}")
            return

        lmb_value = getattr(JDXiSysExOffsetDrumKitLMB, lmb_attr)

        # Create address for this partial
        # Match the address used by the editor (TEMPORARY_TONE, not TEMPORARY_PROGRAM)
        address = JDXiSysExAddress(
            JDXiSysExAddressStartMSB.TEMPORARY_TONE,
            JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT,
            JDXiSysExOffsetProgramLMB(lmb_value),
            0x00,
        )

        self.partial_addresses[partial_index] = address

        # Create slider
        slider = Slider(
            partial_name,
            min_value=0,
            max_value=127,
            midi_helper=self.midi_helper,
            vertical=True,
            show_value_label=True,
            tooltip=f"Level for {partial_name}",
        )

        # Connect slider to send MIDI messages
        slider.valueChanged.connect(
            lambda v, addr=address, pidx=partial_index: self._on_partial_level_changed(
                v, addr, pidx
            )
        )

        self.mixer_sliders[partial_name] = slider

        # Add slider and label to layout
        label = QLabel(partial_name)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 11px;
                color: {JDXi.UI.Style.FOREGROUND};
                padding: 2px;
            }}
        """
        )
        # row is already the label row (0, 3, 6, etc.)
        layout.addWidget(label)
        layout.addWidget(slider)  # Sliders span 2 rows

    def _lane_layout(self, group: MixerLane):
        return group._strip_layout

    def _on_master_level_changed(self, value: int, address: JDXiSysExAddress) -> None:
        """Handle master level change."""
        if not self.midi_helper:
            return

        try:
            from jdxi_editor.midi.sysex.composer import JDXiSysExComposer

            composer = JDXiSysExComposer()
            message = composer.compose_message(
                address=address,
                param=DrumCommonParam.KIT_LEVEL,
                value=value,
            )
            self.midi_helper.send_midi_message(message)
            log.message(f"Master level changed to {value}")
        except Exception as ex:
            log.error(f"Error setting master level: {ex}")

    def _on_partial_level_changed(
            self, value: int, address: JDXiSysExAddress, partial_index: int
    ) -> None:
        """Handle partial level change."""
        if not self.midi_helper:
            return

        try:
            from jdxi_editor.midi.sysex.composer import JDXiSysExComposer

            composer = JDXiSysExComposer()
            # PARTIAL_OUTPUT_LEVEL address offset is 0x16 within the partial's address space
            # This matches what the Partial Tabs use (not PARTIAL_LEVEL which is 0x0E)
            # Note: compose_message will automatically add the parameter's offset (0x16) via apply_address_offset
            # So we set LSB to 0x00 and let compose_message add the offset
            partial_address = JDXiSysExAddress(
                address.msb,
                address.umb,
                address.lmb,
                0x00,  # Base LSB - compose_message will add PARTIAL_OUTPUT_LEVEL offset (0x16)
            )

            message = composer.compose_message(
                address=partial_address,
                param=DrumPartialParam.PARTIAL_OUTPUT_LEVEL,
                value=value,
            )
            self.midi_helper.send_midi_message(message)
            log.message(f"Partial {partial_index} level changed to {value}")
        except Exception as ex:
            log.error(f"Error setting partial {partial_index} level: {ex}")
