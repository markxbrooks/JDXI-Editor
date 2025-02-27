import re
import logging
from typing import Optional, Dict

from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QGroupBox,
    QScrollArea,
    QWidget,
    QTabWidget,
    QFormLayout,
    QSpinBox,
    QSlider,
    QPushButton
)
from PySide6.QtCore import Qt, Signal

from jdxi_manager.data.parameter.drums import DrumParameter
from jdxi_manager.data.presets.data import DRUM_PRESETS_ENUMERATED
from jdxi_manager.data.presets.type import PresetType
from jdxi_manager.midi.io import MIDIHelper
from jdxi_manager.midi.preset.loader import PresetLoader
from jdxi_manager.ui.editors.drum_partial import DrumPartialEditor
from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.ui.editors.base import BaseEditor
from jdxi_manager.midi.constants.sysex import (
    TEMPORARY_DIGITAL_SYNTH_1_AREA,
)
from jdxi_manager.ui.widgets.preset.combo_box import PresetComboBox


class DrumPadEditor(BaseEditor):
    """Drum pad editor"""

    preset_changed = Signal(int, str, int)

    def __init__(self, pad_number: int, parent=None):
        super().__init__(parent)

        # Set fixed width for the entire pad editor
        self.setFixedWidth(250)

        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)  # Remove spacing between widgets
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.setLayout(main_layout)

        # Create frame with red border
        group = QGroupBox(f"Pad {pad_number}")
        # frame.setFrameStyle(QFrame.Box | QFrame.Plain)
        frame_layout = QVBoxLayout()
        frame_layout.setSpacing(0)  # Remove spacing between widgets
        frame_layout.setContentsMargins(5, 5, 5, 5)  # Small internal margins
        group.setLayout(frame_layout)

        # Create pad label with string, not int
        # pad_label = QLabel(f"Pad {pad_number}")
        # frame_layout.addWidget(pad_label)

        # Set slider width to fit nicely in the 250px container
        slider_width = 220  # Leave some margin for the frame

        # Level control
        self.level = Slider("Level", 0, 127)
        self.level.setFixedWidth(slider_width)
        frame_layout.addWidget(self.level)

        # Pan control (-64 to +63)
        self.pan = Slider("Pan", -64, 63)
        self.pan.setFixedWidth(slider_width)
        frame_layout.addWidget(self.pan)

        # Tune control (-24 to +24 semitones)
        self.tune = Slider("Tune", -24, 24)
        self.tune.setFixedWidth(slider_width)
        frame_layout.addWidget(self.tune)

        # Decay control
        self.decay = Slider("Decay", 0, 127)
        self.decay.setFixedWidth(slider_width)
        frame_layout.addWidget(self.decay)

        # Effects sends
        self.reverb = Slider("Reverb", 0, 127)
        self.reverb.setFixedWidth(slider_width)
        self.delay = Slider("Delay", 0, 127)
        self.delay.setFixedWidth(slider_width)
        frame_layout.addWidget(self.reverb)
        frame_layout.addWidget(self.delay)

        # Add frame to main layout
        main_layout.addWidget(group)
        self.setStyleSheet(Style.JDXI_EDITOR)


class DrumEditor(BaseEditor):
    """Editor for JD-Xi Drum Kit parameters"""

    def __init__(self, midi_helper: Optional[MIDIHelper] = None, parent=None):
        super().__init__(midi_helper, parent)
        
        # Initialize class attributes
        self.partial_editors = {}
        self.partial_tab_widget = QTabWidget()
        self.partial_num = 1
        self.group = 0x00
        self.address = 0x00 # Initialize address to common area
        self.image_label = None
        self.instrument_icon_folder = "drum_kits"
        # Main layout
        self.controls: Dict[DrumParameter, QWidget] = {}
        self.preset_type = PresetType.DRUMS
        self.preset_loader = PresetLoader(self.midi_helper)
        self.partial_editors = {}
        self.main_window = parent

        # Create layouts
        main_layout = QVBoxLayout(self)
        upper_layout = QHBoxLayout()
        main_layout.addLayout(upper_layout)
        self.setMinimumSize(1000, 500)
        self.midi_requests = [
                                  "F0 41 10 00 00 00 0E 11 19 70 00 00 00 00 00 12 65 F7",
                                  "F0 41 10 00 00 00 0E 11 19 70 2E 00 00 00 01 43 05 F7",
                                  "F0 41 10 00 00 00 0E 11 19 70 30 00 00 00 01 43 03 F7",
                                  "F0 41 10 00 00 00 0E 11 19 70 32 00 00 00 01 43 01 F7",
                                  "F0 41 10 00 00 00 0E 11 19 70 34 00 00 00 01 43 7F F7",
                                  "F0 41 10 00 00 00 0E 11 19 70 36 00 00 00 01 43 7D F7"
                              ]
        # Title and drum kit selection
        drum_group = QGroupBox("Drum Kit")
        self.title_label = QLabel(
            f"Drum Kit:\n {DRUM_PRESETS_ENUMERATED[0]}" if DRUM_PRESETS_ENUMERATED else "Drum Kit"
        )
        drum_group.setStyleSheet(
            """
            QGroupBox {
            width: 300px;
            }
        """
        )
        self.title_label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
        """
        )
        drum_group_layout = QVBoxLayout()
        drum_group.setLayout(drum_group_layout)
        drum_group_layout.addWidget(self.title_label)

        # Add the "Read Request" button
        self.read_request_button = QPushButton("Send Read Request to Synth")
        self.read_request_button.clicked.connect(self.data_request)
        drum_group_layout.addWidget(self.read_request_button)

        self.selection_label = QLabel("Select a drum kit:")
        drum_group_layout.addWidget(self.selection_label)
        # Drum kit selection

        self.instrument_selection_combo = PresetComboBox(DRUM_PRESETS_ENUMERATED)
        self.instrument_selection_combo.combo_box.setEditable(True)  # Allow text search
        self.instrument_selection_combo.combo_box.setCurrentIndex(
            self.preset_loader.preset_number
        )
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_image
        )
        # Connect QComboBox signal to PresetHandler
        self.main_window.drums_preset_handler.preset_changed.connect(
            self.update_combo_box_index
        )

        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_image
        )
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_title
        )
        self.instrument_selection_combo.load_button.clicked.connect(
            self.update_instrument_preset
        )
        drum_group_layout.addWidget(self.instrument_selection_combo)
        upper_layout.addWidget(drum_group)

        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image
        upper_layout.addWidget(self.image_label)

        # Common controls
        common_group = QGroupBox("Common")
        common_layout = QFormLayout()

        # Assign Type control
        self.assign_type_combo = QComboBox()
        self.assign_type_combo.addItems(["MULTI", "SINGLE"])
        common_layout.addRow("Assign Type", self.assign_type_combo)

        # Mute Group control
        self.mute_group_spin = QSpinBox()
        self.mute_group_spin.setRange(0, 31)
        common_layout.addRow("Mute Group", self.mute_group_spin)

        # Kit Level control
        self.kit_level_slider = QSlider(Qt.Orientation.Horizontal)
        self.kit_level_slider.setRange(0, 127)
        self.kit_level_slider.valueChanged.connect(self.on_kit_level_changed)
        common_layout.addRow("Kit Level", self.kit_level_slider)

        # Partial Pitch Bend Range
        self.pitch_bend_range_slider = QSlider(Qt.Orientation.Horizontal)
        self.pitch_bend_range_slider.setRange(0, 48)
        self.pitch_bend_range_slider.valueChanged.connect(
            self.on_pitch_bend_range_changed
        )
        common_layout.addRow("Pitch Bend Range", self.pitch_bend_range_slider)

        # Partial Receive Expression
        self.receive_expression_combo = QComboBox()
        self.receive_expression_combo.addItems(["OFF", "ON"])
        common_layout.addRow("Receive Expression", self.receive_expression_combo)

        # Partial Receive Hold-1
        self.receive_hold_combo = QComboBox()
        self.receive_hold_combo.addItems(["OFF", "ON"])
        common_layout.addRow("Receive Hold-1", self.receive_hold_combo)

        # One Shot Mode
        self.one_shot_mode_combo = QComboBox()
        self.one_shot_mode_combo.addItems(["OFF", "ON"])
        common_layout.addRow("One Shot Mode", self.one_shot_mode_combo)

        common_group.setLayout(common_layout)
        upper_layout.addWidget(common_group)

        # Create scroll area for partials
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        main_layout.addWidget(scroll)
        
        # Setup tab widget
        self.partial_tab_widget.setStyleSheet(Style.JDXI_TABS_DRUMS)
        scroll.setWidget(self.partial_tab_widget)
        
        # Initialize partial editors
        self._setup_partial_editors()
        
        self.update_instrument_image()
        self.partial_tab_widget.currentChanged.connect(self.update_partial_num)
        self.data_request()

    def _setup_partial_editors(self):
        """Setup all partial editors and tabs"""
        # Map of partial names to their indices
        partial_mapping = {
            "BD1": 0, "RIM": 1, "BD2": 2, "CLAP": 3, "BD3": 4, "SD1": 5, 
            "CHH": 6, "SD2": 7, "PHH": 8, "SD3": 9, "OHH": 10, "SD4": 11,
            "TOM1": 12, "PRC1": 13, "TOM2": 14, "PRC2": 15, "TOM3": 16, 
            "PRC3": 17, "CYM1": 18, "PRC4": 19, "CYM2": 20, "PRC5": 21,
            "CYM3": 22, "HIT": 23, "OTH1": 24, "OTH2": 25
        }

        for partial_name, partial_index in partial_mapping.items():
            try:
                # Create editor with index instead of trying to get address directly
                editor = DrumPartialEditor(
                    midi_helper=self.midi_helper,
                    partial_num=partial_index,  # Pass the numerical index
                    address=partial_index,  # The address will be calculated in the editor
                    parent=self
                )
                self.partial_editors[partial_name] = editor
                self.partial_tab_widget.addTab(editor, partial_name)
                logging.info(f"Created editor for {partial_name} (index {partial_index})")
            except Exception as e:
                logging.error(f"Error creating editor for partial {partial_name}: {str(e)}")

    def update_partial_num(self, index: int):
        """Update the current partial number based on tab index"""
        try:
            partial_name = list(self.partial_editors.keys())[index]
            self.partial_num = index
            logging.info(f"Updated to partial {partial_name} (index {index})")
        except IndexError:
            logging.error(f"Invalid partial index: {index}")

    def on_kit_level_changed(self, value):
        """Handle kit level slider value change"""
        # Use the helper function to send the SysEx message
        # self.send_sysex_message(0x0C, value)
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
            part=0x70,
            group=0x00,  # 00 0C | 0aaa aaaa | Kit Level (0 - 127)
            param=0x0C,
            value=value,  # Make sure this value is being sent
        )

    def on_pitch_bend_range_changed(self, value):
        """Handle pitch bend range value change"""
        # Use the helper function to send the SysEx message
        # self.send_sysex_message(0x2E, value)
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
            part=0x70,
            group=0x2E,  # 00 0C | 0aaa aaaa | Kit Level (0 - 127)
            param=0x1C,
            value=value,  # Make sure this value is being sent
        )

