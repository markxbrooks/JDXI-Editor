"""
Drum Kit Mixer widget.

Provides 37 vertical sliders for controlling the master level and
all 36 drum partial levels.
"""

from typing import Dict, Optional

from decologr import Decologr as log
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import (
    JDXiSysExAddressStartMSB,
    JDXiSysExOffsetProgramLMB,
    JDXiSysExOffsetTemporaryToneUMB,
    RolandSysExAddress,
)
from jdxi_editor.midi.data.drum.data import DRUM_PARTIAL_NAMES
from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParam
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.display.digital import DigitalTitle
from jdxi_editor.ui.widgets.slider import Slider


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
        self.partial_addresses: Dict[int, RolandSysExAddress] = {}

        # Base address for drum kit common area
        # Base address for drum kit common area (stored for reference, not currently used)
        # Match the address used by the editor (TEMPORARY_TONE, not TEMPORARY_PROGRAM)
        self.base_address = RolandSysExAddress(
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
        sliders_layout = QGridLayout(sliders_widget)
        sliders_layout.setSpacing(15)
        sliders_layout.setContentsMargins(10, 10, 10, 10)

        # Create master slider (Kit Level)
        self._create_master_slider(sliders_layout, 0, 0)

        # Create 36 partial sliders
        # Use DRUM_PARTIAL_NAMES[1:] to skip "COM" and get the 36 partials
        partial_names = DRUM_PARTIAL_NAMES[1:]  # Skip COM, get 36 partials

        # Arrange sliders in a grid: 6 columns
        # Master slider already added at row 0, col 0
        # Then add 36 partials starting at row 0, col 1
        row = 0
        col = 1  # Start after master slider

        for idx, partial_name in enumerate(partial_names, start=1):
            # Calculate grid position
            if col >= 6:  # 6 columns
                col = 0
                row += 1

            # Create slider for this partial
            # Each slider takes 3 rows: label, slider (spanning 2 rows)
            slider_row = row * 3
            self._create_partial_slider(
                sliders_layout, slider_row, col, partial_name, idx
            )

            col += 1

        scroll_area.setWidget(sliders_widget)
        main_layout.addWidget(scroll_area)

    def _create_master_slider(self, layout: QGridLayout, row: int, col: int) -> None:
        """Create the master (Kit Level) slider."""
        # Use common address for master level
        # Match the address used by the editor (TEMPORARY_TONE, not TEMPORARY_PROGRAM)
        address = RolandSysExAddress(
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
            log.warning(f"Invalid partial index: {partial_index}")
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
        address = RolandSysExAddress(
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

    def _on_master_level_changed(self, value: int, address: RolandSysExAddress) -> None:
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
        self, value: int, address: RolandSysExAddress, partial_index: int
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
            partial_address = RolandSysExAddress(
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
