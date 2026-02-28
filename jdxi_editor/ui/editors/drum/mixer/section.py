"""
Drum Kit Mixer widget.

Provides 37 vertical sliders for controlling the master level and
all 36 drum partial levels. Uses ChannelStrip (slider + label + icon + mute)
for consistency with the program mixer.
"""

from typing import Callable, Dict, Optional

from decologr import Decologr as log
from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
)

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
from jdxi_editor.ui.common import JDXi, QVBoxLayout, QWidget
from jdxi_editor.ui.editors.drum.mixer.lane import MixerLane
from jdxi_editor.ui.editors.drum.mixer.spec import DRUM_MIXER_LANE_ROWS
from jdxi_editor.ui.editors.program.channel_strip import ChannelStrip
from jdxi_editor.ui.widgets.digital.title import DigitalTitle
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.slider import Slider


class DrumKitMixerSection(SectionBaseWidget):
    """
    Drum Kit Mixer widget with 37 vertical sliders:
    - 1 Master slider (Kit Level)
    - 36 Partial sliders (one for each drum partial)
    address: JDXiSysExAddress,
    """

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        create_parameter_slider: Callable = None,
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
        self._create_parameter_slider = create_parameter_slider
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

    def _setup_ui(self):
        """So as to not provide a Tab widget"""
        pass

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

        sliders_layout = QVBoxLayout()  # the actual mixer grid

        sliders_hlayout = QHBoxLayout(sliders_widget)  # install on widget
        sliders_hlayout.addStretch(1)
        sliders_hlayout.addLayout(sliders_layout)
        sliders_hlayout.addStretch(1)

        sliders_layout.setSpacing(15)
        sliders_layout.setContentsMargins(10, 10, 10, 10)

        # --- ROW 0: MASTER + KICK + TOMS (same row) ---
        row0_layout = QHBoxLayout()
        row0_layout.addStretch()
        master_lane = self._create_lane_group("Master")
        row0_layout.addWidget(master_lane)
        master_strip = self._build_master_strip()
        master_lane.add_strip(master_strip)
        sliders_layout.addLayout(row0_layout)

        first_row = DRUM_MIXER_LANE_ROWS[0]
        for lane in first_row:
            group = self._create_lane_group(lane.name)
            row0_layout.addWidget(group)
            for partial in lane.partials:
                idx = DRUM_PARTIAL_NAMES.index(partial)
                strip = self._build_partial_strip(partial, idx)
                if strip:
                    group.add_strip(strip)
            row0_layout.addStretch()

        # --- ROWS 1..n: remaining lane rows (Snares, Backbeat, Time, Notes) ---
        for row, lane_row in enumerate(DRUM_MIXER_LANE_ROWS[1:], start=1):
            row_layout = QHBoxLayout()
            row_layout.addStretch()
            for lane in lane_row:
                group = self._create_lane_group(lane.name)
                row_layout.addWidget(group)
                for partial in lane.partials:
                    idx = DRUM_PARTIAL_NAMES.index(partial)
                    strip = self._build_partial_strip(partial, idx)
                    if strip:
                        group.add_strip(strip)
            row_layout.addStretch()
            sliders_layout.addLayout(row_layout)
        scroll_area.setWidget(sliders_widget)
        main_layout.addWidget(scroll_area)

    def _send_drum_midi(
        self, param: AddressParameter, value: int, address: JDXiSysExAddress
    ) -> bool:
        """Callback for ChannelStrip mute/send. Composes and sends SysEx."""
        if not self.midi_helper:
            return False
        try:
            from jdxi_editor.midi.sysex.composer import JDXiSysExComposer

            composer = JDXiSysExComposer()
            if param == DrumPartialParam.PARTIAL_OUTPUT_LEVEL:
                address = JDXiSysExAddress(address.msb, address.umb, address.lmb, 0x00)
            message = composer.compose_message(
                address=address, param=param, value=value
            )
            self.midi_helper.send_midi_message(message)
            return True
        except Exception as ex:
            log.error(f"Error sending drum MIDI: {ex}")
            return False

    def _build_partial_strip(
        self, partial_name: str, partial_index: int
    ) -> Optional[ChannelStrip]:
        if not (1 <= partial_index <= 36):
            log.warning(
                f"Invalid partial index: {partial_index}", scope=self.__class__.__name__
            )
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
        slider = Slider(
            partial_name,
            min_value=0,
            max_value=127,
            initial_value=127,
            midi_helper=self.midi_helper,
            vertical=True,
            show_value_label=True,
            tooltip=f"Level for {partial_name} (0 to 127)",
        )
        slider.valueChanged.connect(
            lambda v, addr=address, pidx=partial_index: self._on_partial_level_changed(
                v, addr, pidx
            )
        )
        self.mixer_sliders[partial_name] = slider

        value_label = QLabel(partial_name)
        value_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        JDXi.UI.Theme.apply_mixer_label(value_label)

        icon_label = QLabel()
        if partial_name in ("CYM1", "CYM2", "CYM3", "CHH", "PHH", "OHH"):
            icon_name = JDXi.UI.Icon.CYMBAL
        elif partial_name in ("BD1", "BD2", "BD3"):
            icon_name = JDXi.UI.Icon.KICK_DRUM_2
        else:
            icon_name = JDXi.UI.Icon.DRUM
        icon = JDXi.UI.Icon.get_icon(icon_name, color=JDXi.UI.Style.FOREGROUND)
        if icon and not icon.isNull():
            pixmap = icon.pixmap(24, 24)
            if pixmap and not pixmap.isNull():
                icon_label.setPixmap(pixmap)

        strip = ChannelStrip(
            title=partial_name,
            slider=slider,
            value_label=value_label,
            icon=icon_label,
            param=DrumPartialParam.PARTIAL_OUTPUT_LEVEL,
            address=address,
            send_midi_callback=self._send_drum_midi,
        )
        strip.setFixedWidth(52)
        return strip

    def _build_master_strip(self) -> ChannelStrip:
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
            initial_value=127,
            midi_helper=self.midi_helper,
            vertical=True,
            show_value_label=True,
            tooltip="Master level for the entire drum kit",
        )
        slider.valueChanged.connect(
            lambda v, addr=address: self._on_master_level_changed(v, addr)
        )
        self.mixer_sliders["Master"] = slider

        value_label = QLabel("MASTER")
        value_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        JDXi.UI.Theme.apply_mixer_label(value_label)

        icon_label = QLabel()
        icon_label.setPixmap(
            JDXi.UI.Icon.get_icon(JDXi.UI.Icon.KEYBOARD).pixmap(24, 24)
        )

        strip = ChannelStrip(
            title="Master",
            slider=slider,
            value_label=value_label,
            icon=icon_label,
            param=DrumCommonParam.KIT_LEVEL,
            address=address,
            send_midi_callback=self._send_drum_midi,
        )
        strip.setFixedWidth(52)
        return strip

    def _create_lane_group(self, title: str) -> MixerLane:
        return MixerLane(title, self)

    def _on_master_level_changed(self, value: int, address: JDXiSysExAddress) -> None:
        """Handle master level change."""
        if not self.midi_helper:
            return

        try:
            from jdxi_editor.midi.sysex.composer import JDXiSysExComposer

            composer = JDXiSysExComposer()
            message = composer.compose_message(
                address=address, param=DrumCommonParam.KIT_LEVEL, value=value
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
