import logging
import os
import re
from functools import partial
from typing import Optional, Dict, Union

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QScrollArea,
    QComboBox, QGridLayout, QPushButton,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
import qtawesome as qta

from jdxi_manager.data.digital import DigitalCommonParameter
from jdxi_manager.data.preset_data import ANALOG_PRESETS, DIGITAL_PRESETS
from jdxi_manager.data.preset_type import PresetType
from jdxi_manager.data.analog import (
    AnalogParameter, AnalogCommonParameter
)
from jdxi_manager.midi import MIDIHelper
from jdxi_manager.midi.preset_loader import PresetLoader
from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.ui.editors.digital import base64_to_pixmap, ms_to_midi_cc, midi_cc_to_ms, frac_to_midi_cc, \
    midi_cc_to_frac
from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets.adsr_widget import ADSRWidget
from jdxi_manager.ui.widgets.preset_combo_box import PresetComboBox
from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.ui.widgets.waveform import (
    WaveformButton,
    upsaw_png,
    triangle_png,
    pwsqu_png,
    adsr_waveform_icon,
)
from jdxi_manager.ui.widgets.switch import Switch
from jdxi_manager.midi.constants.analog import (
    AnalogToneCC,
    Waveform,
    SubOscType,
    ANALOG_SYNTH_AREA,
    ANALOG_PART,
    ANALOG_OSC_GROUP,
)
import base64

instrument_icon_folder = "patterns"


class PatternSequencer(BaseEditor):
    """Pattern Sequencer with MIDI Integration"""

    def __init__(self, midi_helper: Optional[MIDIHelper], parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.buttons = []
        self.setStyleSheet(Style.EDITOR_STYLE)
        self.note_to_index = {
            60: 0,  # C4
            61: 1,  # C#4
            62: 2,  # D4
            63: 3,  # D#4
            64: 4,  # E4
            65: 5,  # F4
            66: 6,  # F#4
            67: 7,  # G4
            68: 8,  # G#4
            69: 9,  # A4
            70: 10,  # A#4
            71: 11,  # B4
            72: 12,  # C5
            73: 13,  # C#5
            74: 14,  # D5
            75: 15  # D#5
        }
        self._setup_ui()
        if self.midi_helper:
            self.midi_helper.midi_note_received.connect(self._handle_midi_note)

    def _setup_ui(self):
        layout = QVBoxLayout()
        row_labels = ["Digital Synth 1", "Digital Synth 2", "Analog Synth", "Drums"]
        self.buttons = [[] for _ in range(4)]

        for row_idx, label_text in enumerate(row_labels):
            row_layout = QVBoxLayout()
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignCenter)
            row_layout.addWidget(label)
            button_layout = QHBoxLayout()

            for i in range(16):  # 4 buttons per row, total 16
                button = QPushButton()
                button.setCheckable(True)
                button.setFixedSize(40, 40)
                button.setStyleSheet(self._button_style(False))
                button.clicked.connect(partial(self.toggle_button, row_idx, i))
                self.buttons[row_idx].append(button)
                button_layout.addWidget(button)

            row_layout.addLayout(button_layout)
            layout.addLayout(row_layout)

        self.setLayout(layout)

    def _button_style(self, active):
        return f'''
            QPushButton {{
                background-color: {'#ff6666' if active else 'black'};
                border: 4px solid #666666;
                border-radius: 15px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: #1A1A1A;
                border-color: #ff4d4d;
            }}
            QPushButton:pressed {{
                background-color: #333333;
                border-color: #ff6666;
            }}
        '''

    def toggle_button(self, row, index):
        button = self.buttons[row][index]
        button.setChecked(not button.isChecked())
        button.setStyleSheet(self._button_style(button.isChecked()))

    def select_buttons(self, indices):
        for row, index in indices:
            if 0 <= row < len(self.buttons) and 0 <= index < len(self.buttons[row]):
                self.toggle_button(row, index)

    def _handle_midi_note(self, note, velocity):
        if note in self.note_to_index and velocity > 0:  # Note-on event
            row = self.note_to_index[note] // 4
            index = self.note_to_index[note] % 4
            self.toggle_button(row, index)


class PatternEditorOld(BaseEditor):
    """A 16-step pattern sequencer with MIDI integration."""
    step_triggered = Signal(int, bool)  # Step index and state

    def __init__(self, midi_helper=None, parent=None):
        super().__init__(parent)
        self.buttons = None
        self.midi_helper = midi_helper
        self.steps = []
        self.init_ui()
        # Example usage of the buttons
        #
        # Referencing a Specific Button
        # 1) By Index
        # Each button is stored in a list, allowing access by index:
        # button = self.buttons[step_index]  # step_index is 0-15
        # 2) By Iteration
        # If you need to loop through all buttons:
        # for index, button in enumerate(self.buttons):
        #     print(f"Button {index} is {'ON' if button.isChecked() else 'OFF'}")
        # 3) By Direct Connection
        # Each button emits a signal when clicked, allowing you to connect a method to handle individual button presses:
        # self.buttons[i].clicked.connect(lambda checked, i=i: self.on_step_toggled(i, checked))
        #
        # 4) Accessing Button State
        # To check if a specific step is active:
        # if self.buttons[5].isChecked():
        #     print("Step 5 is active!")

        # Usage Example
        # button_5 = self.get_button(5)  # Get the button at index 5
        # if button_5.isChecked():
        #     print("Step 5 is active!")
        # Indices to select (1, 5, 9, 13) - Adjust to zero-based indexing (0, 4, 8, 12)
        # indices_to_select = [0, 4, 8, 12]
        # for index in indices_to_select:
        #    self.set_button_state(index, True)  # Select (turn on) the buttons
        # # Indices to toggle (1, 5, 9, 13) - Adjusted to zero-based (0, 4, 8, 12)
        # indices_to_toggle = [0, 4, 8, 12]
        # for index in indices_to_toggle:
        #     self.toggle_button_state(index)  # Toggle the button state

    def get_button(self, index: int):
        """Retrieve a button by its index (0-15)."""
        if 0 <= index < len(self.buttons):
            return self.buttons[index]
        else:
            raise IndexError("Button index out of range (0-15).")

    def set_button_state(self, index: int, checked: bool):
        """Set the state of a button by index (0-15)."""
        if 0 <= index < len(self.buttons):
            self.buttons[index].setChecked(checked)
        else:
            raise IndexError("Button index out of range (0-15).")

    def init_ui(self):
        """Initialize the UI with 16 buttons."""
        layout = QGridLayout()
        for i in range(16):
            btn = QPushButton(str(i + 1))
            btn.setCheckable(True)
            btn.setFixedSize(40, 40)
            btn.clicked.connect(lambda checked, step=i: self.on_step_clicked(step, checked))
            layout.addWidget(btn, 0, i)
            self.steps.append(btn)
        self.setLayout(layout)

    def on_step_clicked(self, step, checked):
        """Handle step button click, sending MIDI if enabled."""
        self.step_triggered.emit(step, checked)
        if self.midi_helper:
            midi_value = 127 if checked else 0  # MIDI velocity or control value
            self.midi_helper.send_cc(64 + step, midi_value)  # Example CC mapping

    def set_pattern(self, pattern):
        """Load a pattern (list of 16 boolean values)."""
        for i, active in enumerate(pattern):
            self.steps[i].setChecked(active)

    def get_pattern(self):
        """Return the current pattern as a list of 16 boolean values."""
        return [btn.isChecked() for btn in self.steps]

    def toggle_button_state(self, index: int):
        """Toggle the state of a button by index (0-15)."""
        if 0 <= index < len(self.buttons):
            current_state = self.buttons[index].isChecked()
            self.buttons[index].setChecked(not current_state)
        else:
            raise IndexError("Button index out of range (0-15).")



    def update_combo_box_index(self, preset_number):
        """Updates the QComboBox to reflect the loaded preset."""
        print(f"Updating combo to preset {preset_number}")
        self.instrument_selection_combo.combo_box.setCurrentIndex(preset_number)

    def update_instrument_title(self):
        selected_synth_text = self.instrument_selection_combo.combo_box.currentText()
        print(f"selected_synth_text: {selected_synth_text}")
        self.instrument_title_label.setText(f"Analog Synth:\n {selected_synth_text}")

    def update_instrument_preset(self):
        selected_synth_text = self.instrument_selection_combo.combo_box.currentText()
        if synth_matches := re.search(
            r"(\d{3}): (\S+).+", selected_synth_text, re.IGNORECASE
        ):
            selected_synth_padded_number = (
                synth_matches.group(1).lower().replace("&", "_").split("_")[0]
            )
            preset_index = int(selected_synth_padded_number)
            print(f"preset_index: {preset_index}")
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
                    "resources", instrument_icon_folder, "analog.png"
                )
            pixmap = QPixmap(file_to_load)
            scaled_pixmap = pixmap.scaledToHeight(
                250, Qt.TransformationMode.SmoothTransformation
            )  # Resize to 250px height
            self.image_label.setPixmap(scaled_pixmap)
            return True

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
            print(f"selected_instrument_type: {selected_instrument_type}")
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

    def send_midi_parameter(self, param, value) -> bool:
        """Send MIDI parameter with error handling"""
        if not self.midi_helper:
            logging.debug("No MIDI helper available - parameter change ignored")
            return False

        try:
            # Get parameter group and address with partial offset
            #if isinstance(param, AnalogParameter):
            #    group, param_address = param.get_address_for_partial(self.partial_num)
            #else:
            group = ANALOG_OSC_GROUP  # Common parameters group
            param_address = param.address

            # Ensure value is included in the MIDI message
            return self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=self.part,
                group=group,
                param=param_address,
                value=value,  # Make sure this value is being sent
            )
        except Exception as e:
            logging.error(f"MIDI error setting {param}: {str(e)}")
            return False

    def _on_parameter_changed(
        self, param: Union[AnalogParameter, AnalogCommonParameter], display_value: int
    ):
        """Handle parameter value changes from UI controls"""
        try:
            # Convert display value to MIDI value if needed
            if hasattr(param, "convert_from_display"):
                midi_value = param.convert_from_display(display_value)
            else:
                midi_value = param.validate_value(display_value)

            # Send MIDI message
            if not self.send_midi_parameter(param, midi_value):
                logging.warning(f"Failed to send parameter {param.name}")

        except Exception as e:
            logging.error(f"Error handling parameter {param.name}: {str(e)}")

    def _create_parameter_slider(
        self, param: Union[AnalogParameter, AnalogCommonParameter], label: str
    , vertical=False) -> Slider:
        """Create a slider for a parameter with proper display conversion"""
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val

        # Create horizontal slider (removed vertical ADSR check)
        slider = Slider(label, display_min, display_max, vertical)

        # Connect value changed signal
        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))

        # Store control reference
        self.controls[param] = slider
        return slider

    def update_filter_adsr_spinbox_from_param(self, control_map, param, value):
        """Updates an ADSR parameter from an external control, avoiding feedback loops."""
        spinbox = control_map[param]
        if param in [AnalogParameter.AMP_ENV_SUSTAIN_LEVEL, AnalogParameter.FILTER_ENV_SUSTAIN_LEVEL]:
            new_value = midi_cc_to_frac(value)
        else:
            new_value = midi_cc_to_ms(value)
        if spinbox.value() != new_value:
            spinbox.blockSignals(True)
            spinbox.setValue(new_value)
            spinbox.blockSignals(False)
            self.filter_adsr_widget.valueChanged()

    def update_adsr_spinbox_from_param(self, control_map, param, value):
        """Updates an ADSR parameter from an external control, avoiding feedback loops."""
        spinbox = control_map[param]
        if param in [AnalogParameter.AMP_ENV_SUSTAIN_LEVEL, AnalogParameter.FILTER_ENV_SUSTAIN_LEVEL]:
            new_value = midi_cc_to_frac(value)
        else:
            new_value = midi_cc_to_ms(value)
        if spinbox.value() != new_value:
            spinbox.blockSignals(True)
            spinbox.setValue(new_value)
            spinbox.blockSignals(False)
            self.amp_env_adsr_widget.valueChanged()

    def update_slider_from_adsr(self, param, value):
        """Updates external control from ADSR widget, avoiding infinite loops."""
        control = self.controls[param]
        if param in [AnalogParameter.AMP_ENV_SUSTAIN_LEVEL, AnalogParameter.FILTER_ENV_SUSTAIN_LEVEL]:
            new_value = frac_to_midi_cc(value)
        else:
            new_value = ms_to_midi_cc(value)
        if control.value() != new_value:
            control.blockSignals(True)
            control.setValue(new_value)
            control.blockSignals(False)

    def _send_cc(self, cc: AnalogToneCC, value: int):
        """Send MIDI CC message"""
        if self.midi_helper:
            # Convert enum to int if needed
            cc_number = cc.value if isinstance(cc, AnalogToneCC) else cc
            self.midi_helper.send_cc(cc_number, value, channel=ANALOG_PART)

    def data_request(self):
        """Send data request SysEx messages to the JD-Xi"""
        # Define SysEx messages as byte arrays
        wave_type_request = bytes.fromhex(
            "F0 41 10 00 00 00 0E 11 19 42 00 00 00 00 00 40 65 F7"
        )
        # Send each SysEx message
        self.send_message(wave_type_request)

    def send_message(self, message):
        """Send a SysEx message using the MIDI helper"""
        if self.midi_helper:
            self.midi_helper.send_message(message)
        else:
            logging.error("MIDI helper not initialized")

    def _base64_to_pixmap(self, base64_str):
        """Convert base64 string to QPixmap"""
        image_data = base64.b64decode(base64_str)
        image = QPixmap()
        image.loadFromData(image_data)
        return image
