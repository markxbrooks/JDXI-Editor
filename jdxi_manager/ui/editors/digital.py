"""
Digital Editor
"""

import json
import os
import re
import logging
import time
from typing import Dict, Optional, Union
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QTabWidget,
    QScrollArea,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
import qtawesome as qta

from jdxi_manager.data.preset_data import DIGITAL_PRESETS
from jdxi_manager.data.preset_type import PresetType
from jdxi_manager.midi import MIDIHelper
from jdxi_manager.midi.preset_loader import PresetLoader
from jdxi_manager.ui.editors.base import BaseEditor
from jdxi_manager.ui.editors.digital_partial import DigitalPartialEditor
from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets.preset_combo_box import PresetComboBox
from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.data.digital import (
    DigitalParameter,
    DigitalCommonParameter,
    OscWave,
    DigitalPartial,
    set_partial_state,
    get_digital_parameter_by_address,
)
from jdxi_manager.midi.constants import (
    DIGITAL_SYNTH_AREA,
    PART_1,
    PART_2,
    DIGITAL_SYNTH_1_AREA,
    DIGITAL_SYNTH_2_AREA,
    Waveform,
)
from jdxi_manager.ui.widgets.partial_switch import PartialsPanel
from jdxi_manager.ui.widgets.switch import Switch


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
        self.midi_data_requests = [
            "F0 41 10 00 00 00 0E 11 19 01 00 00 00 00 00 40 26 F7",  # wave_type_request
            "F0 41 10 00 00 00 0E 11 19 01 20 00 00 00 00 3D 09 F7",  # oscillator_1_request
            "F0 41 10 00 00 00 0E 11 19 01 21 00 00 00 00 3D 08 F7",  # oscillator_2_request
            "F0 41 10 00 00 00 0E 11 19 01 22 00 00 00 00 3D 07 F7",  # oscillator_3_request
            "F0 41 10 00 00 00 0E 11 19 01 50 00 00 00 00 25 71 F7",  # effects_request
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
        container_layout.addWidget(self._create_performance_section())

        # Add partials panel at the top
        self.partials_panel = PartialsPanel()
        container_layout.addWidget(self.partials_panel)
        self.partials_panel.setStyleSheet(Style.JDXI_TABS_STYLE)

        # Create tab widget for partials
        self.partial_tab_widget = QTabWidget()
        self.partial_editors = {}

        # Create editor for each partial
        for i in range(1, 4):
            editor = DigitalPartialEditor(midi_helper, i, self.part)
            self.partial_editors[i] = editor
            self.partial_tab_widget.addTab(editor, f"Partial {i}")

        container_layout.addWidget(self.partial_tab_widget)

        # Add container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # Connect partial switches to enable/disable tabs
        for switch in self.partials_panel.switches.values():
            switch.stateChanged.connect(self._on_partial_state_changed)

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

        self.midi_helper.json_sysex.connect(self._update_sliders_from_sysex)
        # self.midi_helper.parameter_received.connect(self._on_parameter_received)

    def update_combo_box_index(self, preset_number):
        """Updates the QComboBox to reflect the loaded preset."""
        logging.info(f"Updating combo to preset {preset_number}")
        self.instrument_selection_combo.combo_box.setCurrentIndex(preset_number)

    def _create_performance_section(self):
        """Create performance controls section"""
        group = QGroupBox("Performance")
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
            icon = qta.icon(icon)
            pixmap = icon.pixmap(
                Style.ICON_SIZE, Style.ICON_SIZE
            )  # Set the desired size
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        layout.addLayout(icons_hlayout)

        # Create two rows of controls
        top_row = QHBoxLayout()
        bottom_row = QHBoxLayout()

        # Ring Modulator switch
        self.ring_switch = Switch("Ring", ["OFF", "---", "ON"])
        self.ring_switch.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalCommonParameter.RING_SWITCH, v)
        )
        top_row.addWidget(self.ring_switch)

        # Unison switch and size
        self.unison_switch = Switch("Unison", ["OFF", "ON"])
        self.unison_switch.valueChanged.connect(
            lambda v: self._on_parameter_changed(
                DigitalCommonParameter.UNISON_SWITCH, v
            )
        )
        top_row.addWidget(self.unison_switch)

        self.unison_size = Switch("Size", ["2 VOICE", "3 VOICE", "4 VOICE", "5 VOICE"])
        self.unison_size.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalCommonParameter.UNISON_SIZE, v)
        )
        top_row.addWidget(self.unison_size)

        # Portamento mode and legato
        self.porto_mode = Switch("Porto", ["NORMAL", "LEGATO"])
        self.porto_mode.valueChanged.connect(
            lambda v: self._on_parameter_changed(
                DigitalCommonParameter.PORTAMENTO_MODE, v
            )
        )
        bottom_row.addWidget(self.porto_mode)

        self.legato_switch = Switch("Legato", ["OFF", "ON"])
        self.legato_switch.valueChanged.connect(
            lambda v: self._on_parameter_changed(
                DigitalCommonParameter.LEGATO_SWITCH, v
            )
        )
        bottom_row.addWidget(self.legato_switch)

        # Analog Feel and Wave Shape
        analog_feel = self._create_parameter_slider(
            DigitalCommonParameter.ANALOG_FEEL, "Analog"
        )
        wave_shape = self._create_parameter_slider(
            DigitalCommonParameter.WAVE_SHAPE, "Shape"
        )

        # Add all controls to layout
        layout.addLayout(top_row)
        layout.addLayout(bottom_row)
        layout.addWidget(analog_feel)
        layout.addWidget(wave_shape)
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
                    f"Received parameter update: param: {param} address={address}, Value={value}"
                )

                # Update the corresponding slider
                if param in self.partial_editors[partial_no].controls:
                    slider = self.partial_editors[partial_no].controls[param]
                    slider.blockSignals(True)  # Prevent feedback loop
                    slider.setValue(value)
                    slider.blockSignals(False)

                # Handle OSC_WAVE parameter to update waveform buttons
                if param == DigitalParameter.OSC_WAVE:
                    self._update_waveform_buttons(partial_no, value)
                    logging.debug(
                        "updating waveform buttons for param {param} with {value}"
                    )
                if param == DigitalParameter.FILTER_MODE:
                    self.partial_editors[partial_no].filter_mode.valueChanged.connect(
                        lambda value: self._on_filter_mode_changed(value)
                    )

    def _update_sliders_from_sysex(self, json_sysex_data: str):
        """Update sliders and combo boxes based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")

        try:
            sysex_data = json.loads(json_sysex_data)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON format: {e}")
            return

        area = sysex_data.get("TEMPORARY_AREA", None)
        logging.info(f"In analog: TEMPORARY_AREA: {area}")

        if area not in [DIGITAL_SYNTH_1_AREA, DIGITAL_SYNTH_2_AREA]:
            logging.warning(
                "SysEx data does not belong to DIGITAL_SYNTH_1_AREA or DIGITAL_SYNTH_2_AREA. Skipping update."
            )
            return

        # Remove unnecessary keys
        for key in {"JD_XI_ID", "ADDRESS", "TEMPORARY_AREA", "TONE_NAME"}:
            sysex_data.pop(key, None)

        # Define mapping dictionaries
        lfo_shape_map = {0: "TRI", 1: "SIN", 2: "SAW", 3: "SQR", 4: "S&H", 5: "RND"}
        sub_osc_type_map = {0: 0, 1: 1, 2: 2}
        osc_waveform_map = {0: Waveform.SAW, 1: Waveform.TRIANGLE, 2: Waveform.PULSE}
        filter_switch_map = {0: 0, 1: 1}

        failures, successes = [], []

        for param_name, param_value in sysex_data.items():
            param = DigitalParameter.get_by_name(
                param_name
            )  # @@ FIXME: implement get_by_name

            if param and param in self.controls:
                slider = self.controls[param]
                slider.blockSignals(True)
                logging.info(f"Updating: {param:50} {param_value}")
                slider.setValue(param_value)
                slider.blockSignals(False)
                successes.append(param_name)

            elif param_name == "LFO_SHAPE" and param_value in lfo_shape_map:
                index = self.lfo_shape.findText(lfo_shape_map[param_value])
                if index != -1:
                    self.lfo_shape.blockSignals(True)
                    self.lfo_shape.setCurrentIndex(index)
                    self.lfo_shape.blockSignals(False)

            elif (
                param_name == "SUB_OSCILLATOR_TYPE" and param_value in sub_osc_type_map
            ):
                index = sub_osc_type_map[param_value]
                if isinstance(index, int):
                    self.sub_type.blockSignals(True)
                    self.sub_type.setValue(index)
                    self.sub_type.blockSignals(False)

            elif param_name == "OSC_WAVEFORM" and param_value in osc_waveform_map:
                waveform = osc_waveform_map[param_value]
                if waveform in self.wave_buttons:
                    button = self.wave_buttons[waveform]
                    button.setChecked(True)
                    self._on_waveform_selected(waveform)

            elif param_name == "FILTER_SWITCH" and param_value in filter_switch_map:
                index = filter_switch_map[param_value]
                self.filter_switch.blockSignals(True)
                self.filter_switch.setValue(index)
                self.filter_switch.blockSignals(False)

            else:
                failures.append(param_name)

        # Logging success rate
        success_rate = (len(successes) / len(sysex_data) * 100) if sysex_data else 0
        logging.info(f"Successes: {successes}")
        logging.info(f"Failures: {failures}")
        logging.info(f"Success Rate: {success_rate:.1f}%")
        logging.info("--------------------------------")

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
