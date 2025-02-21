"""
Digital Editor
"""

import os
import json
import re
import logging
from gc import DEBUG_STATS
from http.cookiejar import debug
from typing import Dict, Optional, Union
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QTabWidget,
    QScrollArea,
    QLabel,
    QPushButton, QCheckBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QShortcut, QKeySequence
import qtawesome as qta

from jdxi_manager.data.preset_data import DIGITAL_PRESETS
from jdxi_manager.data.preset_type import PresetType
from jdxi_manager.midi import MIDIHelper
from jdxi_manager.midi.conversions import midi_cc_to_ms, midi_cc_to_frac
from jdxi_manager.midi.preset_loader import PresetLoader
from jdxi_manager.ui.editors.base import BaseEditor
from jdxi_manager.ui.editors.digital_partial import DigitalPartialEditor
from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets.preset.combo_box import PresetComboBox
from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.data.digital import (
    OscWave,
    DigitalPartial,
    set_partial_state,
    get_digital_parameter_by_address,
)
from jdxi_manager.data.parameter.digital_common import DigitalCommonParameter
from jdxi_manager.data.parameter.digital import DigitalParameter
from jdxi_manager.midi.constants import (
    DIGITAL_SYNTH_AREA,
    PART_1,
    PART_2,
    PART_3,
    DIGITAL_SYNTH_1_AREA,
    DIGITAL_SYNTH_2_AREA,
    Waveform,
)
from jdxi_manager.ui.widgets.switch.partial import PartialsPanel
from jdxi_manager.ui.widgets.switch.switch import Switch


instrument_icon_folder = "digital_synths"


class DigitalSynthEditor(BaseEditor):
    """class for Digital Synth Editor containing 3 partials"""

    preset_changed = Signal(int, str, int)

    def __init__(
        self,
        midi_helper: Optional[MIDIHelper] = None,
        synth_num=1,
        parent=None,
        preset_handler=None,
    ):
        super().__init__(parent)
        # Image display
        self.partial_num = None
        self.current_data = None
        self.preset_type = (
            PresetType.DIGITAL_1 if synth_num == 1 else PresetType.DIGITAL_2
        )
        self.presets = DIGITAL_PRESETS
        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image

        self.midi_helper = midi_helper
        self.preset_loader = PresetLoader(self.midi_helper)
        self.midi_requests = [
            "F0 41 10 00 00 00 0E 11 19 01 00 00 00 00 00 40 26 F7",  # common controls
            "F0 41 10 00 00 00 0E 11 19 01 20 00 00 00 00 3D 09 F7",  # partial 1 request
            "F0 41 10 00 00 00 0E 11 19 01 21 00 00 00 00 3D 08 F7",  # partial 2 request
            "F0 41 10 00 00 00 0E 11 19 01 22 00 00 00 00 3D 07 F7",  # partial 3 request
            "F0 41 10 00 00 00 0E 11 19 01 50 00 00 00 00 25 71 F7",  # modify request
        ]
        if preset_handler:
            self.preset_handler = preset_handler
        else:
            if self.preset_type == PresetType.DIGITAL_1:
                self.preset_handler = parent.digital_1_preset_handler
            else:
                self.preset_handler = parent.digital_2_preset_handler
        self.synth_num = synth_num
        self.part = PART_1 if synth_num == 1 else PART_2
        self.setWindowTitle(f"Digital Synth {synth_num}")
        self.main_window = parent

        # Store parameter controls for easy access
        self.controls: Dict[
            Union[DigitalParameter, DigitalCommonParameter], QWidget
        ] = {}

        # Allow resizing
        self.setMinimumSize(800, 400)
        self.resize(1000, 600)

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.setStyleSheet(Style.JDXI_TABS_STYLE + Style.EDITOR_STYLE)
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Create container widget
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        upper_layout = QHBoxLayout()
        container_layout.addLayout(upper_layout)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # Title and instrument selection
        instrument_preset_group = QGroupBox("Digital Synth")
        self.instrument_title_label = QLabel(
            f"Digital Synth:\n {self.presets[0]}" if self.presets else "Digital Synth"
        )
        instrument_preset_group.setStyleSheet(
            """
            QGroupBox {
            width: 300px;
            }
        """
        )
        self.instrument_title_label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
        """
        )
        instrument_title_group_layout = QVBoxLayout()
        instrument_preset_group.setLayout(instrument_title_group_layout)
        instrument_title_group_layout.addWidget(self.instrument_title_label)

        self.instrument_selection_label = QLabel("Select a digital synth:")
        instrument_title_group_layout.addWidget(self.instrument_selection_label)
        # Synth selection
        upper_layout = QHBoxLayout()
        container_layout.addLayout(upper_layout)

        # Title and drum kit selection
        instrument_preset_group = QGroupBox("Digital Synth")
        self.instrument_title_label = QLabel(
            f"Digital Synth:\n {self.presets[0]}" if self.presets else "Digital Synth"
        )
        instrument_preset_group.setStyleSheet(
            """
            QGroupBox {
            width: 300px;
            }
        """
        )
        self.instrument_title_label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
        """
        )
        instrument_title_group_layout = QVBoxLayout()
        instrument_preset_group.setLayout(instrument_title_group_layout)
        instrument_title_group_layout.addWidget(self.instrument_title_label)

        # Add the "Read Request" button
        self.read_request_button = QPushButton("Send Read Request to Synth")
        self.read_request_button.clicked.connect(self.data_request)
        instrument_title_group_layout.addWidget(self.read_request_button)

        self.instrument_selection_label = QLabel("Select a Digital synth:")
        instrument_title_group_layout.addWidget(self.instrument_selection_label)
        # Synth selection
        # Preset ComboBox
        self.instrument_selection_combo = PresetComboBox(DIGITAL_PRESETS)
        self.instrument_selection_combo.combo_box.setEditable(True)  # Allow text search
        self.instrument_selection_combo.combo_box.setCurrentIndex(
            self.preset_handler.current_preset_index
        )

        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_image
        )
        # Connect QComboBox signal to PresetHandler
        self.preset_handler.preset_changed.connect(self.update_combo_box_index)
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_title
        )
        self.instrument_selection_combo.load_button.clicked.connect(
            self.update_instrument_preset
        )
        instrument_title_group_layout.addWidget(self.instrument_selection_combo)
        upper_layout.addWidget(instrument_preset_group)
        upper_layout.addWidget(self.image_label)
        container_layout.addLayout(upper_layout)
        self.update_instrument_image()

        # Add performance section
        # container_layout.addWidget(self._create_performance_section())

        # Add partials panel at the top
        self.partials_panel = PartialsPanel()
        container_layout.addWidget(self.partials_panel)
        self.partials_panel.setStyleSheet(Style.JDXI_TABS_STYLE)

        # Create tab widget for partials
        self.partial_tab_widget = QTabWidget()
        self.partial_tab_widget.setStyleSheet(Style.JDXI_TABS_STYLE)
        self.partial_editors = {}

        # Create editor for each partial
        for i in range(1, 4):
            editor = DigitalPartialEditor(midi_helper, i, self.part)
            self.partial_editors[i] = editor
            self.partial_tab_widget.addTab(editor, f"Partial {i}")
        self.partial_tab_widget.addTab(self._create_common_controls_section(), "Common Controls")

        container_layout.addWidget(self.partial_tab_widget)

        # Add container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # Connect partial switches to enable/disable tabs
        for switch in self.partials_panel.switches.values():
            switch.stateChanged.connect(self._on_partial_state_changed)
        self.midi_helper.midi_parameter_received.connect(self._on_parameter_received)
        # Initialize with default states
        self.initialize_partial_states()
        self.data_request()

        # Register the callback for incoming MIDI messages
        if self.midi_helper:
            logging.info("MIDI helper initialized")
            if hasattr(self.midi_helper, "set_callback"):
                self.midi_helper.set_callback(self.midi_helper.midi_callback)
                logging.info("MIDI callback set")
            else:
                logging.error("MIDI set_callback method not found")
        else:
            logging.error("MIDI helper not initialized")

        self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
        print(f"self.controls: {self.controls}")
        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)
        if self.midi_helper:
            self.midi_helper.midi_program_changed.connect(self._handle_program_change)

    def update_combo_box_index(self, preset_number):
        """Updates the QComboBox to reflect the loaded preset."""
        logging.info(f"Updating combo to preset {preset_number}")
        self.instrument_selection_combo.combo_box.setCurrentIndex(preset_number)

    def _create_common_controls_section(self):
        """Create common controls section"""
        group = QWidget()
        # group = QGroupBox("Common Controls")
        layout = QVBoxLayout()
        group.setLayout(layout)
        # prettify with icons

        icons_hlayout = QHBoxLayout()
        for icon in [
            "ph.bell-ringing-bold",
            "mdi.call-merge",
            "mdi.account-voice",
            "ri.voiceprint-fill",
            "mdi.piano",
        ]:
            icon_label = QLabel()
            icon = qta.icon(icon, color='#666666')
            pixmap = icon.pixmap(
                Style.ICON_SIZE, Style.ICON_SIZE
            )  # Set the desired size
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        layout.addLayout(icons_hlayout)

        mono_row = QHBoxLayout()
        
        self.mono_switch = Switch("Mono", ["OFF", "ON"])
        self.mono_switch.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalCommonParameter.MONO_SWITCH, v)
        )
        mono_row.addWidget(self.mono_switch)
        self.controls[DigitalCommonParameter.MONO_SWITCH] = self.mono_switch
        layout.addLayout(mono_row)

        self.pitch_bend_row = QHBoxLayout()
        self.pitch_bend_up = self._create_parameter_slider(DigitalCommonParameter.PITCH_BEND_UP, "Pitch Bend Up")   
        self.pitch_bend_down = self._create_parameter_slider(DigitalCommonParameter.PITCH_BEND_DOWN, "Pitch Bend Down")
        self.pitch_bend_row.addWidget(self.pitch_bend_up)
        self.pitch_bend_row.addWidget(self.pitch_bend_down)
        layout.addLayout(self.pitch_bend_row)

        # Create tone level row
        self.tone_level_row = QHBoxLayout()
        self.tone_level = self._create_parameter_slider(DigitalCommonParameter.TONE_LEVEL, "Tone Level")
        self.tone_level_row.addWidget(self.tone_level)
        layout.addLayout(self.tone_level_row)

        # Ring Modulator switch
        self.ring_row = QHBoxLayout()
        self.ring_switch = Switch("Ring", ["OFF", "---", "ON"])
        self.ring_switch.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalCommonParameter.RING_SWITCH, v)
        )
        self.controls[DigitalCommonParameter.RING_SWITCH] = self.ring_switch
        self.ring_row.addWidget(self.ring_switch)
        layout.addLayout(self.ring_row)

        # Unison switch and size
        self.unison_row = QHBoxLayout()
        self.unison_switch = Switch("Unison", ["OFF", "ON"])
        self.unison_switch.valueChanged.connect(
            lambda v: self._on_parameter_changed(
                DigitalCommonParameter.UNISON_SWITCH, v
            )
        )
        self.controls[DigitalCommonParameter.UNISON_SWITCH] = self.unison_switch
        self.unison_row.addWidget(self.unison_switch)
        layout.addLayout(self.unison_row)

        self.unison_size = Switch("Size", ["2 VOICE", "3 VOICE", "4 VOICE", "5 VOICE"])
        self.unison_size.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalCommonParameter.UNISON_SIZE, v)
        )
        self.unison_row.addWidget(self.unison_size)
        self.controls[DigitalCommonParameter.UNISON_SIZE] = self.unison_size
        layout.addLayout(self.unison_row)

        self.portamento_row = QHBoxLayout()
        self.portamento_switch = Switch("Portamento", ["OFF", "ON"])
        self.portamento_switch.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalCommonParameter.PORTAMENTO_SWITCH, v)
        )
        self.controls[DigitalCommonParameter.PORTAMENTO_SWITCH] = self.portamento_switch
        self.portamento_row.addWidget(self.portamento_switch)
        layout.addLayout(self.portamento_row)

        self.portamento_time_row = QHBoxLayout()
        self.portamento_time = self._create_parameter_slider(DigitalCommonParameter.PORTAMENTO_TIME, "Portamento Time")
        self.portamento_time_row.addWidget(self.portamento_time)
        self.controls[DigitalCommonParameter.PORTAMENTO_TIME] = self.portamento_time
        layout.addLayout(self.portamento_time_row)

        # Portamento mode and legato
        self.portamento_mode = Switch("Portamento Mode", ["NORMAL", "LEGATO"])
        self.portamento_mode.valueChanged.connect(
            lambda v: self._on_parameter_changed(
                DigitalCommonParameter.PORTAMENTO_MODE, v
            )
        )
        self.controls[DigitalCommonParameter.PORTAMENTO_MODE] = self.portamento_mode
        self.portamento_row.addWidget(self.portamento_mode)

        self.legato_row = QHBoxLayout()
        self.legato_switch = Switch("Legato", ["OFF", "ON"])
        self.legato_switch.valueChanged.connect(
            lambda v: self._on_parameter_changed(
                DigitalCommonParameter.LEGATO_SWITCH, v
            )
        )
        self.controls[DigitalCommonParameter.LEGATO_SWITCH] = self.legato_switch
        self.legato_row.addWidget(self.legato_switch)

        # Analog Feel and Wave Shape
        self.analog_feel = self._create_parameter_slider(
            DigitalCommonParameter.ANALOG_FEEL, "Analog Feel"
        )
        self.wave_shape = self._create_parameter_slider(
            DigitalCommonParameter.WAVE_SHAPE, "Wave Shape"
        )
        self.controls[DigitalCommonParameter.ANALOG_FEEL] = self.analog_feel
        self.controls[DigitalCommonParameter.WAVE_SHAPE] = self.wave_shape
        # Add all controls to layout
        layout.addLayout(mono_row)
        layout.addLayout(self.tone_level_row)
        layout.addLayout(self.ring_row)
        layout.addLayout(self.unison_row)
        layout.addLayout(self.legato_row)
        layout.addWidget(self.analog_feel)
        layout.addWidget(self.wave_shape)
        self.update_instrument_image()
        return group

    def _create_parameter_slider(
        self, param: Union[DigitalParameter, DigitalCommonParameter], label: str
    ) -> Slider:
        """Create a slider for a parameter with proper display conversion"""
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val

        # Create horizontal slider (removed vertical ADSR check)
        slider = Slider(label, display_min, display_max)

        # Connect value changed signal
        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))

        # Store control reference
        self.controls[param] = slider
        return slider

    def update_instrument_title(self):
        selected_synth_text = self.instrument_selection_combo.combo_box.currentText()
        logging.info(f"selected_synth_text: {selected_synth_text}")
        self.instrument_title_label.setText(f"Digital Synth:\n {selected_synth_text}")

    def update_instrument_preset(self):
        selected_synth_text = self.instrument_selection_combo.combo_box.currentText()
        if synth_matches := re.search(
            r"(\d{3}): (\S+).+", selected_synth_text, re.IGNORECASE
        ):
            selected_synth_padded_number = (
                synth_matches.group(1).lower().replace("&", "_").split("_")[0]
            )
            preset_index = int(selected_synth_padded_number)
            logging.info(f"preset_index: {preset_index}")
            self.load_preset(preset_index)

    def update_instrument_image(self):
        def load_and_set_image(image_path, secondary_image_path):
            """Helper function to load and set the image on the label."""
            file_to_load = ""
            if os.path.exists(image_path):
                file_to_load = image_path
            elif os.path.exists(secondary_image_path):
                file_to_load = secondary_image_path
            else:
                file_to_load = os.path.join(
                    "resources", instrument_icon_folder, "jdxi_vector.png"
                )
            pixmap = QPixmap(file_to_load)
            scaled_pixmap = pixmap.scaledToHeight(
                250, Qt.TransformationMode.SmoothTransformation
            )  # Resize to 250px height
            self.image_label.setPixmap(scaled_pixmap)
            return True

        default_image_path = os.path.join(
            "resources", instrument_icon_folder, "jdxi_vector.png"
        )
        selected_instrument_text = (
            self.instrument_selection_combo.combo_box.currentText()
        )

        # Try to extract synth name from the selected text
        image_loaded = False
        if instrument_matches := re.search(
            r"(\d{3}): (\S+)\s(\S+)+", selected_instrument_text, re.IGNORECASE
        ):
            selected_instrument_name = (
                instrument_matches.group(2).lower().replace("&", "_").split("_")[0]
            )
            selected_instrument_type = (
                instrument_matches.group(3).lower().replace("&", "_").split("_")[0]
            )
            logging.info(f"selected_instrument_type: {selected_instrument_type}")
            specific_image_path = os.path.join(
                "resources",
                instrument_icon_folder,
                f"{selected_instrument_name}.png",
            )
            generic_image_path = os.path.join(
                "resources",
                instrument_icon_folder,
                f"{selected_instrument_type}.png",
            )
            image_loaded = load_and_set_image(specific_image_path, generic_image_path)

        # Fallback to default image if no specific image is found
        if not image_loaded:
            if not load_and_set_image(default_image_path):
                self.image_label.clear()  # Clear label if default image is also missing

    def load_preset(self, preset_index):
        preset_data = {
            "type": self.preset_type,  # Ensure this is a valid type
            "selpreset": preset_index,  # Convert to 1-based index
            "modified": 0,  # or 1, depending on your logic
        }
        if not self.preset_loader:
            self.preset_loader = PresetLoader(self.midi_helper)
        if self.preset_loader:
            self.preset_loader.load_preset(preset_data)

    def _on_parameter_changed(
        self, param: Union[DigitalParameter, DigitalCommonParameter], display_value: int
    ):
        """Handle parameter value changes from UI controls"""
        try:
            # Convert display value to MIDI value if needed
            if hasattr(param, "convert_from_display"):
                midi_value = param.convert_from_display(display_value)
            else:
                midi_value = param.validate_value(display_value)
            logging.info(f"parameter from widget midi_value: {midi_value}")
            # Send MIDI message
            if not self.send_midi_parameter(param, midi_value):
                logging.warning(f"Failed to send parameter {param.name}")

        except Exception as e:
            logging.error(f"Error handling parameter {param.name}: {str(e)}")

    def _on_partial_state_changed(
        self, partial: DigitalPartial, enabled: bool, selected: bool
    ):
        """Handle partial state changes"""
        if self.midi_helper:
            set_partial_state(self.midi_helper, partial, enabled, selected)

        # Enable/disable corresponding tab
        partial_num = partial.value
        self.partial_tab_widget.setTabEnabled(partial_num - 1, enabled)

        # Switch to selected partial's tab
        if selected:
            self.partial_tab_widget.setCurrentIndex(partial_num - 1)

    def initialize_partial_states(self):
        """Initialize partial states with defaults"""
        # Default: Partial 1 enabled and selected, others disabled
        for partial in DigitalPartial.get_partials():
            enabled = partial == DigitalPartial.PARTIAL_1
            selected = enabled
            self.partials_panel.switches[partial].setState(enabled, selected)
            self.partial_tab_widget.setTabEnabled(partial.value - 1, enabled)

        # Show first tab
        self.partial_tab_widget.setCurrentIndex(0)

    def send_midi_parameter(self, param, value) -> bool:
        """Send MIDI parameter with error handling"""
        if not self.midi_helper:
            logging.debug("No MIDI helper available - parameter change ignored")
            return False

        try:
            # Get parameter group and address with partial offset
            if isinstance(param, DigitalParameter):
                group, param_address = param.get_address_for_partial(self.partial_num)
            else:
                group = 0x00  # Common parameters group
                param_address = param.address

            # Ensure value is included in the MIDI message
            return self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=self.part,
                group=group,
                param=param_address,
                value=value,  # Make sure this value is being sent
            )
        except Exception as e:
            logging.error(f"MIDI error setting {param}: {str(e)}")
            return False

    def _update_ui(self, parameters: Dict[str, int]):
        """Update UI with new parameter values"""
        try:
            # Emit the signal to update the UI
            self.ui_update_requested.emit(parameters)

        except Exception as e:
            logging.error(f"Error updating UI: {str(e)}", exc_info=True)

    def handle_midi_message(self, message):
        """Callback for handling incoming MIDI messages"""
        try:
            logging.info(f"SysEx message: {message}")
            if message[7] == 0x12:  # DT1 command
                self._handle_dt1_message(message[8:])
        except Exception as e:
            logging.error(f"Error handling MIDI message: {str(e)}", exc_info=True)

    def _handle_dt1_message(self, data):
        """Handle Data Set 1 (DT1) messages

        Format: aa bb cc dd ... where:
        aa bb cc = Address
        dd ... = Data
        """
        if len(data) < 4:  # Need at least address and one data byte
            return

        address = data[0:3]
        logging.info(f"DT1 message Address: {address}")
        value = data[3]
        logging.info(f"DT1 message Value: {value}")
        # Emit signal with parameter data
        self.parameter_received.emit(address, value)

    def send_message(self, message):
        """Send a SysEx message using the MIDI helper"""
        if self.midi_helper:
            self.midi_helper.send_message(message)
        else:
            logging.error("MIDI helper not initialized")

    def _on_parameter_received(self, address, value):
        """Handle parameter updates from MIDI messages."""
        area_code = address[0]
        if address[0] in [DIGITAL_SYNTH_1_AREA, DIGITAL_SYNTH_2_AREA]:
            # Extract the actual parameter address (80, 0) from [25, 1, 80, 0]
            parameter_address = tuple(address[2:])  # (80, 0)

            # Retrieve the corresponding DigitalParameter
            param = get_digital_parameter_by_address(parameter_address)
            partial_no = address[1]
            if param:
                logging.info(
                    f"param: \t{param} \taddress=\t{address}, Value=\t{value}"
                )

                # Update the corresponding slider
                if param in self.partial_editors[partial_no].controls:
                    slider_value = param.convert_from_midi(value)
                    logging.info(f"midi value {value} converted to slider value {slider_value}")
                    slider = self.partial_editors[partial_no].controls[param]
                    slider.blockSignals(True)  # Prevent feedback loop
                    slider.setValue(slider_value)
                    slider.blockSignals(False)

                # Handle OSC_WAVE parameter to update waveform buttons
                if param == DigitalParameter.OSC_WAVE:
                    self._update_waveform_buttons(partial_no, value)
                    logging.debug(
                        "updating waveform buttons for param {param} with {value}"
                    )

    def _update_partial_sliders_from_sysex(self, json_sysex_data: str):
        """Update sliders and combo boxes based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")
        debug_param_updates = True
        debug_stats = True

        try:
            sysex_data = json.loads(json_sysex_data)
            self.previous_data = self.current_data
            self.current_data = sysex_data
            self._log_changes(self.previous_data, sysex_data)
        except json.JSONDecodeError as ex:
            logging.error(f"Invalid JSON format: {ex}")
            return

        def _is_valid_sysex_area(sysex_data):
            """Check if SysEx data belongs to a supported digital synth area."""
            return sysex_data.get("TEMPORARY_AREA") in ["DIGITAL_SYNTH_1_AREA", "DIGITAL_SYNTH_2_AREA"]

        def _get_partial_number(synth_tone):
            """Retrieve partial number from synth tone mapping."""
            return {
                "PARTIAL_1": 1,
                "PARTIAL_2": 2,
                "PARTIAL_3": 3
            }.get(synth_tone, None)


        def update_adsr_widget(param, value):
            """Helper function to update ADSR widgets."""
            new_value = midi_cc_to_frac(value) if param in [
                DigitalParameter.AMP_ENV_SUSTAIN_LEVEL,
                DigitalParameter.FILTER_ENV_SUSTAIN_LEVEL,
            ] else midi_cc_to_ms(value)

            adsr_mapping = {
                DigitalParameter.AMP_ENV_ATTACK_TIME: self.partial_editors[partial_no].amp_env_adsr_widget.attack_sb,
                DigitalParameter.AMP_ENV_DECAY_TIME: self.partial_editors[partial_no].amp_env_adsr_widget.decay_sb,
                DigitalParameter.AMP_ENV_SUSTAIN_LEVEL: self.partial_editors[partial_no].amp_env_adsr_widget.sustain_sb,
                DigitalParameter.AMP_ENV_RELEASE_TIME: self.partial_editors[partial_no].amp_env_adsr_widget.release_sb,
                DigitalParameter.FILTER_ENV_ATTACK_TIME: self.partial_editors[partial_no].filter_adsr_widget.attack_sb,
                DigitalParameter.FILTER_ENV_DECAY_TIME: self.partial_editors[partial_no].filter_adsr_widget.decay_sb,
                DigitalParameter.FILTER_ENV_SUSTAIN_LEVEL: self.partial_editors[partial_no].filter_adsr_widget.sustain_sb,
                DigitalParameter.FILTER_ENV_RELEASE_TIME: self.partial_editors[partial_no].filter_adsr_widget.release_sb,
            }

            if param in adsr_mapping:
                spinbox = adsr_mapping[param]
                spinbox.setValue(new_value)

        if not _is_valid_sysex_area(sysex_data):
            logging.warning(
                "SysEx data does not belong to DIGITAL_SYNTH_1_AREA or DIGITAL_SYNTH_2_AREA. Skipping update.")
            return

        synth_tone = sysex_data.get("SYNTH_TONE")
        partial_no = _get_partial_number(synth_tone)

        ignored_keys = {"JD_XI_ID", "ADDRESS", "TEMPORARY_AREA", "TONE_NAME"}
        sysex_data = {k: v for k, v in sysex_data.items() if k not in ignored_keys}

        # osc_waveform_map = {wave.value: wave for wave in OscWave}

        failures, successes = [], []

        def _update_slider(param, value):
            """Helper function to update sliders safely."""
            slider = self.partial_editors[partial_no].controls.get(param)
            if slider:
                slider_value = param.convert_from_midi(value)
                logging.info(f"midi value {value} converted to slider value {slider_value}")
                slider.blockSignals(True)
                slider.setValue(slider_value)
                slider.blockSignals(False)
                successes.append(param.name)
                if debug_param_updates:
                    logging.info(f"Updated: {param.name:50} {value}")

        def _update_waveform(param_value):
            """Helper function to update waveform selection UI."""
            waveform = osc_waveform_map.get(param_value)
            if waveform and waveform in self.partial_editors[partial_no].wave_buttons:
                button = self.partial_editors[partial_no].wave_buttons[waveform]
                button.setChecked(True)
                self.partial_editors[partial_no]._on_waveform_selected(waveform)
                logging.debug(f"Updated waveform button for {waveform}")

        for param_name, param_value in sysex_data.items():
            param = DigitalParameter.get_by_name(param_name)

            if param:
                if param == DigitalParameter.OSC_WAVE:
                    self._update_waveform_buttons(partial_no, param_value)
                else:
                    _update_slider(param, param_value)
                    update_adsr_widget(param, param_value)
            else:
                failures.append(param_name)

        def _log_debug_info():
            """Helper function to log debugging statistics."""
            if debug_stats:
                success_rate = (len(successes) / len(sysex_data) * 100) if sysex_data else 0
                logging.info(f"Successes: {successes}")
                logging.info(f"Failures: {failures}")
                logging.info(f"Success Rate: {success_rate:.1f}%")
                logging.info("--------------------------------")

        _log_debug_info()

    def _update_sliders_from_sysex_hacked(self, json_sysex_data: str):
        """Update sliders and combo boxes based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")
        debug_param_updates = True
        debug_stats = True
        failures, successes = [], []

        def _parse_sysex_json(json_data):
            """Parse JSON safely and log changes."""
            try:
                sysex_data = json.loads(json_data)
                self.previous_data = self.current_data
                self.current_data = sysex_data
                self._log_changes(self.previous_data, sysex_data)
                return sysex_data
            except json.JSONDecodeError as ex:
                logging.error(f"Invalid JSON format: {ex}")
                return None

        def _is_valid_sysex_area(sysex_data):
            """Check if SysEx data belongs to a supported digital synth area."""
            return sysex_data.get("TEMPORARY_AREA") in ["DIGITAL_SYNTH_1_AREA", "DIGITAL_SYNTH_2_AREA"]

        def _get_partial_number(synth_tone):
            """Retrieve partial number from synth tone mapping."""
            return {
                "PARTIAL_1": 1,
                "PARTIAL_2": 2,
                "PARTIAL_3": 3
            }.get(synth_tone, None)

        def _update_common_slider(param, value):
            """Helper function to update sliders safely."""
            logging.info(f"param: {param}")
            slider = self.controls.get(param)
            logging.info(f"slider: {slider}")
            if slider:
                slider.blockSignals(True)
                slider.setValue(value)
                slider.blockSignals(False)
                successes.append(param.name)
                if debug_param_updates:
                    logging.info(f"Updated: {param.name:50} {value}")
            else:
                failures.append(param.name)

        # Parse SysEx data
        sysex_data = _parse_sysex_json(json_sysex_data)
        if not sysex_data:
            return

        if not _is_valid_sysex_area(sysex_data):
            logging.warning(
                "SysEx data does not belong to DIGITAL_SYNTH_1_AREA or DIGITAL_SYNTH_2_AREA. Skipping update.")
            return

        synth_tone = sysex_data.get("SYNTH_TONE")
        partial_no = _get_partial_number(synth_tone)

        ignored_keys = {"JD_XI_ID", "ADDRESS", "TEMPORARY_AREA", "TONE_NAME", "SYNTH_TONE"}
        sysex_data = {k: v for k, v in sysex_data.items() if k not in ignored_keys}

        def _update_slider(param, value):
            """Helper function to update sliders safely."""
            slider = self.partial_editors[partial_no].controls.get(param)
            logging.info(f"Updating slider for param {param}")
            if slider:
                slider.blockSignals(True)
                slider.setValue(value)
                slider.blockSignals(False)
                successes.append(param.name)
                if debug_param_updates:
                    logging.info(f"Updated: {param.name:50} {value}")
            else:
                failures.append(param.name)

        def update_adsr_widget(param, value):
            """Helper function to update ADSR widgets."""
            new_value = midi_cc_to_frac(value) if param in [
                DigitalParameter.AMP_ENV_SUSTAIN_LEVEL,
                DigitalParameter.FILTER_ENV_SUSTAIN_LEVEL,
            ] else midi_cc_to_ms(value)

            adsr_mapping = {
                DigitalParameter.AMP_ENV_ATTACK_TIME: self.partial_editors[partial_no].amp_env_adsr_widget.attack_sb,
                DigitalParameter.AMP_ENV_DECAY_TIME: self.partial_editors[partial_no].amp_env_adsr_widget.decay_sb,
                DigitalParameter.AMP_ENV_SUSTAIN_LEVEL: self.partial_editors[partial_no].amp_env_adsr_widget.sustain_sb,
                DigitalParameter.AMP_ENV_RELEASE_TIME: self.partial_editors[partial_no].amp_env_adsr_widget.release_sb,
                DigitalParameter.FILTER_ENV_ATTACK_TIME: self.partial_editors[partial_no].filter_adsr_widget.attack_sb,
                DigitalParameter.FILTER_ENV_DECAY_TIME: self.partial_editors[partial_no].filter_adsr_widget.decay_sb,
                DigitalParameter.FILTER_ENV_SUSTAIN_LEVEL: self.partial_editors[partial_no].filter_adsr_widget.sustain_sb,
                DigitalParameter.FILTER_ENV_RELEASE_TIME: self.partial_editors[partial_no].filter_adsr_widget.release_sb,
            }

            if param in adsr_mapping:
                spinbox = adsr_mapping[param]
                spinbox.setValue(new_value)

        for param_name, param_value in sysex_data.items():
            logging.info(f"param_name {param_name}")
            param = DigitalParameter.get_by_name(param_name)
            logging.info(f"param {param}")
            try:
                if param:
                    if param == DigitalParameter.OSC_WAVE:
                        self._update_waveform_buttons(partial_no, param_value)
                    else:
                        _update_slider(param, param_value)
                        update_adsr_widget(param, param_value)
                else:
                    failures.append(param_name)
            except Exception as ex:
                logging.info(f"Error {ex} occurred")

        def _log_debug_info():
            """Helper function to log debugging statistics."""
            if debug_stats:
                success_rate = (len(successes) / len(sysex_data) * 100) if sysex_data else 0
                logging.info(f"successes: \t{successes}")
                logging.info(f"failures: \t{failures}")
                logging.info(f"success rate: \t{success_rate:.1f}%")
                logging.info("--------------------------------")

        _log_debug_info()

    def _dispatch_sysex_to_area(self, json_sysex_data: str):
        """Update sliders and combo boxes based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")
        failures, successes = [], []

        def _parse_sysex_json(json_data):
            """Parse JSON safely and log changes."""
            try:
                sysex_data = json.loads(json_data)
                return sysex_data
            except json.JSONDecodeError as ex:
                logging.error(f"Invalid JSON format: {ex}")
                return None

        # Parse SysEx data
        sysex_data = _parse_sysex_json(json_sysex_data)
        if not sysex_data:
            return

        synth_tone = sysex_data.get("SYNTH_TONE")

        if synth_tone == "TONE_COMMON":
            logging.info(f"\nTone common")
            self._update_common_sliders_from_sysex(json_sysex_data)
        elif synth_tone == "TONE_MODIFY":
            pass  # not yet implemented
        else:
            self._update_partial_sliders_from_sysex(json_sysex_data)

    def _update_common_sliders_from_sysex(self, json_sysex_data: str):
        """Update sliders and combo boxes based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")
        debug_param_updates = True
        debug_stats = True
        failures, successes = [], []

        def _parse_sysex_json(json_data):
            """Parse JSON safely and log changes."""
            try:
                sysex_data = json.loads(json_data)
                self.previous_data = self.current_data
                self.current_data = sysex_data
                self._log_changes(self.previous_data, sysex_data)
                return sysex_data
            except json.JSONDecodeError as ex:
                logging.error(f"Invalid JSON format: {ex}")
                return None

        def _is_valid_sysex_area(sysex_data):
            """Check if SysEx data belongs to a supported digital synth area."""
            return sysex_data.get("TEMPORARY_AREA") in ["DIGITAL_SYNTH_1_AREA", "DIGITAL_SYNTH_2_AREA"]

        def _get_partial_number(synth_tone):
            """Retrieve partial number from synth tone mapping."""
            return {
                "PARTIAL_1": 1,
                "PARTIAL_2": 2,
                "PARTIAL_3": 3
            }.get(synth_tone, None)

        def _update_common_slider(param, value):
            """Helper function to update sliders safely."""
            logging.info(f"param: {param}")
            slider = self.controls.get(param)
            logging.info(f"slider: {slider}")
            if slider:
                slider.blockSignals(True)
                slider.setValue(value)
                slider.blockSignals(False)
                successes.append(param.name)
                if debug_param_updates:
                    logging.info(f"Updated: {param.name:50} {value}")
            else:
                failures.append(param.name)

        def _update_common_switch(param, value):
            """Helper function to update checkbox safely."""
            logging.info(f"checkbox param: {param} {value}")
            partial_switch_map = {"PARTIAL1_SWITCH": 1, "PARTIAL2_SWITCH": 2, "PARTIAL3_SWITCH": 3}
            partial_number = partial_switch_map.get(param_name)
            check_box = self.partials_panel.switches.get(partial_number)
            logging.info(f"check_box: {check_box}")
            if check_box: # and isinstance(check_box, QCheckBox):
                check_box.blockSignals(True)
                check_box.setState(bool(value), False)
                check_box.blockSignals(False)
                successes.append(param.name)
                if debug_param_updates:
                    logging.info(f"Updated: {param.name:50} {value}")
            else:
                failures.append(param.name)

        # Parse SysEx data
        sysex_data = _parse_sysex_json(json_sysex_data)
        if not sysex_data:
            return

        if not _is_valid_sysex_area(sysex_data):
            logging.warning(
                "SysEx data does not belong to DIGITAL_SYNTH_1_AREA or DIGITAL_SYNTH_2_AREA. Skipping update.")
            return

        synth_tone = sysex_data.get("SYNTH_TONE")
        partial_no = _get_partial_number(sysex_data.get("SYNTH_TONE"))

        common_ignored_keys = {'JD_XI_ID', 'ADDRESS', 'TEMPORARY_AREA', 'SYNTH_TONE', 'TONE_NAME', 'TONE_NAME_1', 'TONE_NAME_2', 'TONE_NAME_3', 'TONE_NAME_4', 'TONE_NAME_5', 'TONE_NAME_6', 'TONE_NAME_7', 'TONE_NAME_8', 'TONE_NAME_9', 'TONE_NAME_10', 'TONE_NAME_11', 'TONE_NAME_12',}
        sysex_data = {k: v for k, v in sysex_data.items() if k not in common_ignored_keys}

        if synth_tone == "TONE_COMMON":
            logging.info(f"\nTone common")
            for param_name, param_value in sysex_data.items():
                param = DigitalCommonParameter.get_by_name(param_name)
                logging.info(f"Tone common: param_name: {param} {param_value}")
                try:
                    if param:
                        if param_name in ['PARTIAL1_SWITCH', 'PARTIAL1_SELECT', 'PARTIAL2_SWITCH', 'PARTIAL2_SELECT', 'PARTIAL3_SWITCH', 'PARTIAL3_SELECT']:
                            _update_common_switch(param, param_value)
                        else:
                            _update_common_slider(param, param_value)
                    else:
                        failures.append(param_name)
                except Exception as ex:
                    logging.info(f"Error {ex} occurred")

        logging.info(f"Updating sliders for Partial {partial_no}")

        def _update_slider(param, value):
            """Helper function to update sliders safely."""
            slider = self.partial_editors[partial_no].controls.get(param)
            if slider:
                slider.blockSignals(True)
                slider.setValue(value)
                slider.blockSignals(False)
                successes.append(param.name)
                if debug_param_updates:
                    logging.info(f"Updated: {param.name:50} {value}")
            else:
                failures.append(param.name)

        def _log_debug_info():
            """Helper function to log debugging statistics."""
            if debug_stats:
                success_rate = (len(successes) / len(sysex_data) * 100) if sysex_data else 0
                logging.info(f"successes: \t{successes}")
                logging.info(f"failures: \t{failures}")
                logging.info(f"success rate: \t{success_rate:.1f}%")
                logging.info("--------------------------------")

        _log_debug_info()

    def _update_sliders_from_sysex_old(self, json_sysex_data: str):
        """Update sliders and combo boxes based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")
        debug_param_updates = True
        debug_stats = True
        try:
            sysex_data = json.loads(json_sysex_data)
            self.previous_data = self.current_data
            self.current_data = sysex_data
            self._log_changes(self.previous_data, sysex_data)
        except json.JSONDecodeError as ex:
            logging.error(f"Invalid JSON format: {ex}")
            return

        temporary_area = sysex_data.get("TEMPORARY_AREA", None)
        logging.info(f"In digital: TEMPORARY_AREA: {temporary_area}")

        if temporary_area not in ["DIGITAL_SYNTH_1_AREA", "DIGITAL_SYNTH_2_AREA"]:
            logging.warning(
                "SysEx data does not belong to DIGITAL_SYNTH_1_AREA or DIGITAL_SYNTH_2_AREA. Skipping update."
            )
            return
        partial_no = 1
        # Remove unnecessary keys
        for key in {"JD_XI_ID", "ADDRESS", "TEMPORARY_AREA", "TONE_NAME"}:
            sysex_data.pop(key, None)

        # Define mapping dictionaries
        lfo_shape_map = {0: "TRI", 1: "SIN", 2: "SAW", 3: "SQR", 4: "S&H", 5: "RND"}
        sub_osc_type_map = {0: 0, 1: 1, 2: 2}
        osc_waveform_map = {wave.value: wave for wave in OscWave}
        filter_switch_map = {0: 0, 1: 1}
        lfo_tempo_sync_switch_map = {0: "OFF", 1: "ON"}
        lfo_trigger_map = {0: "OFF", 1: "ON"}
        failures, successes = [], []

        for param_name, param_value in sysex_data.items():
            param = DigitalParameter.get_by_name(
                param_name
            )
            # logging.info(f"param_name: {param_name}: {param}")

            if param and param in self.partial_editors[partial_no].controls:
                slider = self.partial_editors[partial_no].controls[param]
                slider.blockSignals(True)
                if debug_param_updates:
                    logging.info(f"Updating: {param:50} {param_value}")
                slider.setValue(param_value)
                slider.blockSignals(False)
                successes.append(param_name)
                

            # Handle OSC_WAVE parameter to update waveform buttons
            if param == DigitalParameter.OSC_WAVE:
                self._update_waveform_buttons(partial_no, param_value)
                logging.debug(
                    "updating waveform buttons for param {param} with {value}"
                )
                

            elif param_name == "OSC_WAVE" and param_value in osc_waveform_map:
                waveform = osc_waveform_map[param_value]
                print(f"param_name: {param_name} waveform: {waveform}")
                if waveform in self.partial_editors[partial_no].wave_buttons:
                    button = self.partial_editors[partial_no].wave_buttons[waveform]
                    button.setChecked(True)
                    self.partial_editors[partial_no]._on_waveform_selected(waveform)
                    

            elif param_name == "LFO_TEMPO_SYNC_SWITCH" and param_value in lfo_tempo_sync_switch_map:
                index = lfo_tempo_sync_switch_map[param_value]
                self.partial_editors[partial_no].lfo_tempo_sync_switch.blockSignals(True)
                self.partial_editors[partial_no].lfo_tempo_sync_switch.setValue(index)
                self.partial_editors[partial_no].lfo_tempo_sync_switch.blockSignals(False)

            elif param_name == "LFO_SHAPE" and param_value in lfo_shape_map:
                index = lfo_shape_map[param_value]
                self.partial_editors[partial_no].lfo_shape.blockSignals(True)
                self.partial_editors[partial_no].lfo_shape.setValue(index)
                self.partial_editors[partial_no].lfo_shape.blockSignals(False)

            elif param_name == "LFO_KEY_TRIGGER" and param_value in lfo_trigger_map:
                index = lfo_trigger_map[param_value]
                self.partial_editors[partial_no].lfo_trigger.blockSignals(True)
                self.partial_editors[partial_no].lfo_trigger.setValue(index)
                self.partial_editors[partial_no].lfo_trigger.blockSignals(False)

            elif param_name == "MOD_LFO_SHAPE" and param_value in lfo_shape_map:
                index = lfo_shape_map[param_value]
                self.partial_editors[partial_no].mod_lfo_shape.blockSignals(True)
                self.partial_editors[partial_no].mod_lfo_shape.setValue(index)
                self.partial_editors[partial_no].mod_lfo_shape.blockSignals(False)

            elif param_name == "MOD_LFO_TEMPO_SYNC_SWITCH" and param_value in lfo_tempo_sync_switch_map:
                index = lfo_tempo_sync_switch_map[param_value]
                self.partial_editors[partial_no].mod_lfo_tempo_sync_switch.blockSignals(True)
                self.partial_editors[partial_no].mod_lfo_tempo_sync_switch.setValue(index)
                self.partial_editors[partial_no].mod_lfo_tempo_sync_switch.blockSignals(False)

            elif param_name == "MOD_LFO_KEY_TRIGGER" and param_value in lfo_trigger_map:
                index = lfo_trigger_map[param_value]
                self.partial_editors[partial_no].mod_lfo_key_trigger.blockSignals(True)
                self.partial_editors[partial_no].mod_lfo_key_trigger.setValue(index)
                self.partial_editors[partial_no].mod_lfo_key_trigger.blockSignals(False)


            else:
                failures.append(param_name)

        if debug_stats:
            # Logging success rate
            success_rate = (len(successes) / len(sysex_data) * 100) if sysex_data else 0
            logging.info(f"Successes: {successes}")
            logging.info(f"Failures: {failures}")
            logging.info(f"Success Rate: {success_rate:.1f}%")
            logging.info("--------------------------------")

    def _log_changes(self, previous_data, current_data):
        """Log changes between previous and current JSON data."""
        changes = []
        if not current_data or not previous_data:
            return
        for key, current_value in current_data.items():
            previous_value = previous_data.get(key)
            if previous_value != current_value:
                changes.append((key, previous_value, current_value))

        changes = [
            change for change in changes if change[0] not in ["JD_XI_ID", "ADDRESS", "TEMPORARY_AREA", "TONE_NAME"]
        ]

        if changes:
            logging.info("Changes detected:")
            for key, prev, curr in changes:
                logging.info(f"\n===> Changed Parameter: {key}, Previous: {prev}, Current: {curr}")
        else:
            logging.info("No changes detected.")

    def _update_waveform_buttons(self, partial_number, value):
        """Update the waveform buttons based on the OSC_WAVE value with visual feedback."""
        logging.debug(
            f"Updating waveform buttons for partial {partial_number} with value {value}"
        )

        waveform_map = {
            0: OscWave.SAW,
            1: OscWave.SQUARE,
            2: OscWave.PW_SQUARE,
            3: OscWave.TRIANGLE,
            4: OscWave.SINE,
            5: OscWave.NOISE,
            6: OscWave.SUPER_SAW,
            7: OscWave.PCM,
        }

        selected_waveform = waveform_map.get(value)

        if selected_waveform is None:
            logging.warning(f"Unknown waveform value: {value}")
            return

        logging.debug(f"Waveform value {value} found, selecting {selected_waveform}")

        # Retrieve waveform buttons for the given partial
        wave_buttons = self.partial_editors[partial_number].wave_buttons

        # Reset all buttons to default style
        for btn in wave_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(Style.BUTTON_DEFAULT)

        # Apply active style to the selected waveform button
        selected_btn = wave_buttons.get(selected_waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(Style.BUTTON_ACTIVE)
