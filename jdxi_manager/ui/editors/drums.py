from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QFrame, QGridLayout, QPushButton,
    QScrollArea, QGroupBox, QLineEdit
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPalette, QColor
import logging

from ..widgets.slider import Slider
from ..widgets.preset_panel import PresetPanel
from .base_editor import BaseEditor
from ...data.drums import DR, DRUM_PARTS, DrumPadSettings, Note, SN_PRESETS
from ...midi.constants import DRUM_KIT_AREA, DRUM_PART
from ..style import Style

class DrumPadWidget(QFrame):
    """Widget for editing a single drum pad"""
    def __init__(self, pad_num: int, send_parameter, parent=None):
        super().__init__(parent)
        self.pad_num = pad_num
        self.send_parameter = send_parameter
        
        self.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        
        # Style the pad widget
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Style.DRUM_PAD_BG};
                border-radius: 4px;
                padding: 4px;
            }}
            QLabel {{
                color: white;
                font-weight: bold;
            }}
        """)
        
        # Create sections
        self._create_header_section(layout)
        self._create_wave_section(layout)
        self._create_levels_section(layout)
        self._create_tune_section(layout)
        self._create_mute_section(layout)
        self._create_sends_section(layout)

    def _create_header_section(self, parent_layout):
        """Create pad header with name and trigger"""
        header_layout = QHBoxLayout()
        
        # Pad number label
        header = QLabel(f"Pad {self.pad_num + 1}")
        header.setAlignment(Qt.AlignLeft)
        header_layout.addWidget(header)
        
        # Name editor
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(12)
        self.name_edit.setPlaceholderText("Pad Name")
        self.name_edit.textChanged.connect(self._name_changed)
        header_layout.addWidget(self.name_edit)
        
        # Trigger button
        trigger_btn = QPushButton("▶")
        trigger_btn.setFixedSize(24, 24)
        trigger_btn.clicked.connect(self._trigger_pad)
        header_layout.addWidget(trigger_btn)
        
        parent_layout.addLayout(header_layout)

    def _create_wave_section(self, parent_layout):
        """Create wave selection section"""
        group = QGroupBox("Wave")
        layout = QVBoxLayout(group)
        
        self.wave_combo = QComboBox()
        self.wave_combo.addItems(self._get_wave_list())
        self.wave_combo.currentIndexChanged.connect(
            lambda v: self.send_parameter(self.pad_num, DR['pad']['wave'][0], v))
        layout.addWidget(self.wave_combo)
        
        parent_layout.addWidget(group)

    def _create_levels_section(self, parent_layout):
        """Create level and pan controls"""
        group = QGroupBox("Levels")
        layout = QVBoxLayout(group)
        
        self.level = Slider("Level", 0, 127,
            lambda v: self.send_parameter(self.pad_num, DR['pad']['level'][0], v))
        layout.addWidget(self.level)
        
        self.pan = Slider("Pan", -64, 63,
            lambda v: self.send_parameter(self.pad_num, DR['pad']['pan'][0], v + 64))
        layout.addWidget(self.pan)
        
        parent_layout.addWidget(group)

    def _create_tune_section(self, parent_layout):
        """Create tune and decay controls"""
        group = QGroupBox("Tuning")
        layout = QVBoxLayout(group)
        
        self.tune = Slider("Tune", -50, 50,
            lambda v: self.send_parameter(self.pad_num, DR['pad']['tune'][0], v + 64))
        layout.addWidget(self.tune)
        
        self.decay = Slider("Decay", 0, 127,
            lambda v: self.send_parameter(self.pad_num, DR['pad']['decay'][0], v))
        layout.addWidget(self.decay)
        
        parent_layout.addWidget(group)

    def _create_mute_section(self, parent_layout):
        """Create mute group selection"""
        group = QGroupBox("Mute Group")
        layout = QVBoxLayout(group)
        
        self.mute_combo = QComboBox()
        self.mute_combo.addItems(['OFF'] + [str(i) for i in range(1, 32)])
        self.mute_combo.currentIndexChanged.connect(
            lambda v: self.send_parameter(self.pad_num, DR['pad']['mute_group'][0], v))
        layout.addWidget(self.mute_combo)
        
        parent_layout.addWidget(group)

    def _create_sends_section(self, parent_layout):
        """Create send level controls"""
        group = QGroupBox("Send Levels")
        layout = QVBoxLayout(group)
        
        self.reverb = Slider("Reverb", 0, 127,
            lambda v: self.send_parameter(self.pad_num, DR['pad']['reverb_send'][0], v))
        layout.addWidget(self.reverb)
        
        self.delay = Slider("Delay", 0, 127,
            lambda v: self.send_parameter(self.pad_num, DR['pad']['delay_send'][0], v))
        layout.addWidget(self.delay)
        
        self.fx = Slider("FX", 0, 127,
            lambda v: self.send_parameter(self.pad_num, DR['pad']['fx_send'][0], v))
        layout.addWidget(self.fx)
        
        parent_layout.addWidget(group)

    def _get_wave_list(self):
        """Get list of available waves"""
        waves = []
        for category, wave_list in DRUM_PARTS.items():
            waves.extend(wave_list)
        return waves

    def _trigger_pad(self):
        """Trigger pad note"""
        note = 36 + self.pad_num  # Base note + pad number
        # Note on
        self.send_parameter(9, 0x90, note)
        # Note off after 100ms
        QTimer.singleShot(100, lambda: self.send_parameter(9, 0x80, note))

    def _name_changed(self):
        """Handle pad name changes"""
        try:
            name = self.name_edit.text()
            name = name.ljust(12)
            
            for i, char in enumerate(name):
                value = ord(char)
                if 32 <= value <= 127:
                    self.send_parameter(self.pad_num, i, value)
            
            logging.debug(f"Sent pad {self.pad_num + 1} name: {name}")
            
        except Exception as e:
            logging.error(f"Error sending pad name: {str(e)}")

    def update_control(self, param: int, value: int):
        """Update control value from MIDI message"""
        try:
            if 0 <= param <= 11:  # Name characters
                current_name = self.name_edit.text()
                name_list = list(current_name.ljust(12))
                name_list[param] = chr(value)
                new_name = ''.join(name_list).rstrip()
                
                self.name_edit.blockSignals(True)
                self.name_edit.setText(new_name)
                self.name_edit.blockSignals(False)
                
            elif param == DR['pad']['wave'][0]:
                self.wave_combo.setCurrentIndex(value)
            elif param == DR['pad']['mute_group'][0]:
                self.mute_combo.setCurrentIndex(value)
            elif param == DR['pad']['level'][0]:
                self.level.setValue(value)
            elif param == DR['pad']['pan'][0]:
                self.pan.setValue(value - 64)
            elif param == DR['pad']['tune'][0]:
                self.tune.setValue(value - 64)
            elif param == DR['pad']['decay'][0]:
                self.decay.setValue(value)
            elif param == DR['pad']['reverb_send'][0]:
                self.reverb.setValue(value)
            elif param == DR['pad']['delay_send'][0]:
                self.delay.setValue(value)
            elif param == DR['pad']['fx_send'][0]:
                self.fx.setValue(value)
            
            logging.debug(f"Updated pad {self.pad_num + 1} parameter {hex(param)}: {value}")
            
        except Exception as e:
            logging.error(f"Error updating pad control: {str(e)}")

class DrumKitEditor(BaseEditor):
    """Editor for drum kit settings"""
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(midi_helper, parent)
        
        # Create main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create sections
        self._create_preset_section(main_layout)
        self._create_name_section(main_layout)
        self._create_content_section(main_layout)

    def _create_preset_section(self, parent_layout):
        """Create preset management section"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.addWidget(QLabel("Drum Kit"))
        
        self.preset_panel = PresetPanel(frame)
        for preset in SN_PRESETS:
            self.preset_panel.preset_combo.addItem(preset)
        layout.addWidget(self.preset_panel)
        
        self.preset_panel.load_clicked.connect(self._load_preset)
        self.preset_panel.save_clicked.connect(self._save_preset)
        
        parent_layout.addWidget(frame)

    def _create_name_section(self, parent_layout):
        """Create kit name section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        layout.addWidget(QLabel("Kit Name"))
        
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(12)
        self.name_edit.textChanged.connect(self._name_changed)
        layout.addWidget(self.name_edit)
        
        parent_layout.addWidget(frame)

    def _create_content_section(self, parent_layout):
        """Create main content section"""
        content_layout = QHBoxLayout()
        
        # Common parameters
        self._create_common_section(content_layout)
        
        # Pads section
        self._create_pads_section(content_layout)
        
        parent_layout.addLayout(content_layout)

    def _create_common_section(self, parent_layout):
        """Create common parameters section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        layout.addWidget(QLabel("Common Parameters"))
        
        self.kit_level = Slider("Kit Level", 0, 127,
            lambda v: self._send_parameter(0x0C, v))
        self.kit_level.setObjectName("kit_level_control")
        layout.addWidget(self.kit_level)
        
        parent_layout.addWidget(frame)

    def _create_pads_section(self, parent_layout):
        """Create drum pads section"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        widget = QWidget()
        layout = QGridLayout(widget)
        
        self.pad_widgets = {}
        for i in range(16):
            row = i // 4
            col = i % 4
            pad = DrumPadWidget(i, self._send_pad_parameter)
            self.pad_widgets[i] = pad
            layout.addWidget(pad, row, col)
            
        scroll.setWidget(widget)
        parent_layout.addWidget(scroll, stretch=2)

    def _send_parameter(self, param: int, value: int):
        """Send common parameter change"""
        try:
            if self.midi_helper:
                self.midi_helper.send_parameter(
                    DRUM_KIT_AREA,
                    DRUM_PART,
                    param,
                    value
                )
                logging.debug(f"Sent drum parameter {hex(param)}: {value}")
                
        except Exception as e:
            logging.error(f"Error sending drum parameter: {str(e)}")

    def _send_pad_parameter(self, pad: int, param: int, value: int):
        """Send pad-specific parameter change"""
        try:
            if self.midi_helper:
                # Calculate parameter address for specific pad
                pad_param = param + (pad * 16)  # 16 parameters per pad
                self.midi_helper.send_parameter(
                    DRUM_KIT_AREA,
                    DRUM_PART,
                    pad_param,
                    value
                )
                logging.debug(f"Sent drum pad {pad} parameter {hex(param)}: {value}")
                
        except Exception as e:
            logging.error(f"Error sending drum pad parameter: {str(e)}")

    def _handle_midi_message(self, message):
        """Handle incoming MIDI message"""
        try:
            # Extract parameter and value
            param = message[3]  # Parameter number
            value = message[4]  # Parameter value
            
            # Update kit level if that's the parameter
            if param == 0x0C:  # Kit Level
                control = self.findChild(QWidget, "kit_level_control")
                if control:
                    control.setValue(value)
                    logging.debug(f"Updated kit level: {value}")
            # Check if it's a pad parameter
            pad_num = param // 16  # 16 parameters per pad
            pad_param = param % 16  # Parameter within pad
            
            if pad_num < 16:  # Pad parameter
                if pad_num in self.pad_widgets:
                    self.pad_widgets[pad_num].update_control(pad_param, value)
            
        except Exception as e:
            logging.error(f"Error handling drum MIDI message: {str(e)}")

    def _name_changed(self):
        """Handle kit name changes"""
        try:
            if not self.midi_helper:
                return
                
            name = self.name_edit.text()
            # Pad to 12 characters with spaces
            name = name.ljust(12)
            
            # Send each character as ASCII value
            for i, char in enumerate(name):
                value = ord(char)
                if 32 <= value <= 127:  # Valid ASCII range
                    self._send_parameter(i, value)
                    
            logging.debug(f"Sent drum kit name: {name}")
            
        except Exception as e:
            logging.error(f"Error sending drum kit name: {str(e)}")

    def _update_name(self, param: int, value: int):
        """Update kit name when receiving MIDI"""
        try:
            if 0 <= param <= 11:  # Name characters are at offsets 0-11
                current_name = self.name_edit.text()
                name_list = list(current_name.ljust(12))
                name_list[param] = chr(value)
                new_name = ''.join(name_list).rstrip()  # Remove trailing spaces
                
                # Block signals to prevent feedback loop
                self.name_edit.blockSignals(True)
                self.name_edit.setText(new_name)
                self.name_edit.blockSignals(False)
                
                logging.debug(f"Updated drum kit name: {new_name}")
                
        except Exception as e:
            logging.error(f"Error updating drum kit name: {str(e)}")

    def _load_preset(self, preset_num: int):
        """Load drum kit preset"""
        try:
            if self.midi_helper:
                self.midi_helper.load_drum_kit(preset_num)
                logging.debug(f"Loading drum kit preset {preset_num}")
        except Exception as e:
            logging.error(f"Error loading drum kit preset: {str(e)}")

    def _save_preset(self, preset_num: int):
        """Save current settings as preset"""
        try:
            if self.midi_helper:
                self.midi_helper.save_drum_kit(preset_num)
                logging.debug(f"Saving drum kit preset {preset_num}")
        except Exception as e:
            logging.error(f"Error saving drum kit preset: {str(e)}") 