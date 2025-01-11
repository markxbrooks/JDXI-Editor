from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QFrame, QLabel, QComboBox, QCheckBox, QPushButton,
    QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
import logging

from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets import Slider
from jdxi_manager.midi.messages import (
    create_sysex_message,
    create_patch_load_message,
    create_patch_save_message,
    JDXiSysEx
)
from jdxi_manager.midi.constants import (
    START_OF_SYSEX, ROLAND_ID, DEVICE_ID, MODEL_ID_1, MODEL_ID_2,
    MODEL_ID, JD_XI_ID, DT1_COMMAND_12, END_OF_SYSEX,
    DRUM_KIT_AREA, SUBGROUP_ZERO, DrumPad, DRUM_SN_PRESETS as SN_PRESETS
)
from jdxi_manager.data.drums import (
    DR,  # Dictionary of drum parameters
    DrumKitPatch,  # Patch data structure
    DrumPadSettings,  # Individual pad settings
    DRUM_PARTS,  # Drum part categories
    MuteGroup,  # Mute group constants
    Note  # Note constants
)
from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.ui.widgets.preset_panel import PresetPanel
from jdxi_manager.data.drums import DrumKitPatch, SN_PRESETS

class DrumEditor(QMainWindow):
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.main_window = parent
        self.current_patch = DrumKitPatch()
        self.drum_buttons = []
        
        # Set window properties
        self.setStyleSheet(Style.MAIN_STYLESHEET)
        self.setFixedWidth(1000)
        self.setMinimumHeight(600)
        
        # Create UI
        self._create_ui()
        
        # Request current patch data
        self._request_patch_data()
        
    def _create_drum_pad(self, pad_number: int):
        """Create controls for a single drum pad"""
        try:
            frame = QFrame()
            frame.setFrameStyle(QFrame.StyledPanel)
            layout = QVBoxLayout(frame)
            
            # Get pad settings
            pad = self.current_patch.pads[pad_number]
            
            # Wave selector
            wave_combo = QComboBox()
            wave_names = []
            for category in DRUM_PARTS.values():
                wave_names.extend(category)
            wave_combo.addItems(wave_names)
            wave_combo.setCurrentIndex(pad.wave if pad.wave is not None else 0)
            wave_combo.currentIndexChanged.connect(
                lambda v: self._update_pad_parameter(pad_number, "wave", v)
            )
            layout.addWidget(wave_combo)
            
            # Level control
            level = Slider(
                "Level", 0, 127,
                lambda v: self._update_pad_parameter(pad_number, "level", v)
            )
            layout.addWidget(level)
            
            # Pan control
            pan = Slider(
                "Pan", -64, 63,
                lambda v: self._update_pad_parameter(pad_number, "pan", v + 64)
            )
            layout.addWidget(pan)
            
            # Mute group selector
            mute_group = QComboBox()
            mute_group.addItems([str(i) for i in range(32)])  # 0-31 mute groups
            mute_group.setCurrentIndex(pad.mute_group if pad.mute_group is not None else 0)
            mute_group.currentIndexChanged.connect(
                lambda v: self._update_pad_parameter(pad_number, "mute_group", v)
            )
            layout.addWidget(mute_group)
            
            return frame
            
        except Exception as e:
            logging.error(f"Error creating drum pad {pad_number}: {str(e)}")
            return QFrame()  # Return empty frame on error

    def _update_pad_parameter(self, pad_number: int, param_name: str, value: int):
        """Update a drum pad parameter"""
        try:
            # Get pad and parameter offset from DR dictionary
            param_info = DR['pad'].get(param_name)
            if not param_info:
                logging.error(f"Unknown parameter: {param_name}")
                return
                
            param_offset = param_info[0]  # Get offset from tuple
            
            # Calculate parameter address (each pad has 16 bytes)
            param_addr = (pad_number * 0x10) + param_offset
            
            # Send parameter change
            msg = JDXiSysEx.create_parameter_message(
                area=DRUM_KIT_AREA,
                part=pad_number,
                group=0x00,
                param=param_addr,
                value=value
            )
            
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                logging.debug(f"Updated pad {pad_number} {param_name}: {value}")
                
            # Update local patch data
            pad = self.current_patch.pads[pad_number]
            setattr(pad, param_name, value)
            
        except Exception as e:
            logging.error(f"Error updating pad {pad_number} {param_name}: {str(e)}")

    def _request_patch_data(self):
        """Request current patch data from synth"""
        try:
            msg = [
                START_OF_SYSEX, ROLAND_ID, DEVICE_ID, MODEL_ID_1, MODEL_ID_2,
                MODEL_ID, JD_XI_ID, DT1_COMMAND_12,
                DRUM_KIT_AREA, SUBGROUP_ZERO,
                0x00,  # Start address
                0x00,
                END_OF_SYSEX
            ]
            
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                
        except Exception as e:
            logging.error(f"Error requesting patch data: {str(e)}")

    def _handle_sysex_data(self, data: list):
        """Handle incoming SysEx data"""
        try:
            # Update current patch with received data
            address = data[8:10]  # Get address bytes
            value = data[11]      # Get value byte

            # Update common parameters
            if address[0] == 0x00:
                if address[1] == 0x00:
                    self.current_patch.level = value
                elif address[1] == 0x01:
                    self.current_patch.pan = value
                # ... handle other common parameters

            # Update pad parameters
            else:
                pad_num = address[0] // DrumPad.PARAM_OFFSET
                param_offset = address[0] % DrumPad.PARAM_OFFSET
                pad = self.current_patch.pads[pad_num]

                # Update pad parameter based on offset
                if param_offset == DrumPad.WAVE:
                    pad.wave = value
                elif param_offset == DrumPad.LEVEL:
                    pad.level = value
                # ... handle other pad parameters

            # Update UI to reflect changes
            self._update_ui_from_patch()

        except Exception as e:
            logging.error(f"Error handling SysEx data: {str(e)}") 
        
    def _create_ui(self):
        """Create the user interface"""
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(scroll)
        
        # Create main widget
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setSpacing(25)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Add preset panel with SuperNATURAL presets
        self.preset_panel = PresetPanel('drums', self)
        self.preset_panel.add_presets(SN_PRESETS)  # Add the SuperNATURAL presets
        layout.addWidget(self.preset_panel)
        
        # Create horizontal layout for main sections
        main_layout = QHBoxLayout()
        
        # Left column: Drum pads and common controls
        left_col = QVBoxLayout()
        
        # Add drum pad grid
        pads_frame = self._create_drum_pad_grid()
        left_col.addWidget(pads_frame)
        
        # Add common controls
        common = self._create_common_controls()
        left_col.addWidget(common)
        
        main_layout.addLayout(left_col)
        
        # Right column: Additional controls
        right_col = QVBoxLayout()
        
        # Add pattern section
        pattern = self._create_pattern_section()
        right_col.addWidget(pattern)
        
        # Add FX section
        fx = self._create_fx_section()
        right_col.addWidget(fx)
        
        main_layout.addLayout(right_col)
        
        # Add main layout to central layout
        layout.addLayout(main_layout)
        
        # Set the widget to scroll area
        scroll.setWidget(central)

    def _create_drum_pad_grid(self):
        """Create grid of drum pads"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        header = QLabel("Drum Pads")
        header.setStyleSheet(f"background-color: {Style.DRUM_PAD_BG}; color: white; padding: 5px;")
        layout.addWidget(header)
        
        # Create grid layout for pads
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # Create 4x4 grid of drum pads
        for row in range(4):
            for col in range(4):
                pad_num = row * 4 + col
                pad = self._create_drum_pad(pad_num)
                if pad:
                    grid.addWidget(pad, row, col)
        
        layout.addLayout(grid)
        return frame
        
    def _create_pattern_section(self):
        """Create pattern section controls"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        header = QLabel("Pattern")
        header.setStyleSheet(f"background-color: {Style.PATTERN_BG}; color: white; padding: 5px;")
        layout.addWidget(header)
        
        # Add pattern controls
        self.pattern_length = Slider("Length", 1, 16, 
            lambda v: self._update_pattern_parameter('length', v))
        self.pattern_velocity = Slider("Velocity", 0, 127,
            lambda v: self._update_pattern_parameter('velocity', v))
        self.pattern_swing = Slider("Swing", 0, 100,
            lambda v: self._update_pattern_parameter('swing', v))
        
        layout.addWidget(self.pattern_length)
        layout.addWidget(self.pattern_velocity)
        layout.addWidget(self.pattern_swing)
        
        # Add pattern buttons
        buttons = QHBoxLayout()
        self.pattern_clear = QPushButton("Clear")
        self.pattern_copy = QPushButton("Copy")
        self.pattern_paste = QPushButton("Paste")
        
        buttons.addWidget(self.pattern_clear)
        buttons.addWidget(self.pattern_copy)
        buttons.addWidget(self.pattern_paste)
        
        layout.addLayout(buttons)
        return frame
        
    def _create_fx_section(self):
        """Create FX section controls"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        header = QLabel("FX")
        header.setStyleSheet(f"background-color: {Style.FX_BG}; color: white; padding: 5px;")
        layout.addWidget(header)
        
        # Create FX type selector
        self.fx_type = QComboBox()
        self.fx_type.addItems([
            "None", "Distortion", "Compressor", "Bitcrusher",
            "Filter", "Phaser", "Delay"
        ])
        layout.addWidget(self.fx_type)
        
        # Create FX parameters
        self.fx_param1 = Slider("Param 1", 0, 127,
            lambda v: self._update_fx_parameter(1, v))
        self.fx_param2 = Slider("Param 2", 0, 127,
            lambda v: self._update_fx_parameter(2, v))
        self.fx_level = Slider("Level", 0, 127,
            lambda v: self._update_fx_parameter('level', v))
        
        layout.addWidget(self.fx_param1)
        layout.addWidget(self.fx_param2)
        layout.addWidget(self.fx_level)
        
        return frame

    def _update_pattern_parameter(self, param: str, value: int):
        """Update a pattern parameter"""
        try:
            # Send MIDI message for pattern parameter
            msg = JDXiSysEx.create_parameter_message(
                area=DRUM_KIT_AREA,
                part=0x70 + {'length': 0, 'velocity': 1, 'swing': 2}[param],
                group=0x00,
                param=value
            )
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                logging.debug(f"Sent pattern parameter: param={hex(0x70 + {'length': 0, 'velocity': 1, 'swing': 2}[param])} value={value}")
        except Exception as e:
            logging.error(f"Error updating pattern parameter {param}: {str(e)}")

    def _update_fx_parameter(self, param: str, value: int):
        """Update an FX parameter"""
        try:
            # Send MIDI message for FX parameter
            msg = JDXiSysEx.create_parameter_message(
                area=DRUM_KIT_AREA,
                part=0x60 + {'level': 0, 1: 1, 2: 2}[param],
                group=0x00,
                param=value
            )
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                logging.debug(f"Sent FX parameter: param={hex(0x60 + {'level': 0, 1: 1, 2: 2}[param])} value={value}")
        except Exception as e:
            logging.error(f"Error updating FX parameter {param}: {str(e)}")

    def _create_common_controls(self):
        """Create common drum kit controls"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        header = QLabel("Common")
        header.setStyleSheet(f"background-color: {Style.COMMON_BG}; color: white; padding: 5px;")
        layout.addWidget(header)
        
        # Create level control
        level = Slider(
            "Level", 0, 127,
            lambda v: self._update_common_parameter('level', v)
        )
        level.setValue(self.current_patch.level)
        
        # Create pan control
        pan = Slider(
            "Pan", -64, 63,
            lambda v: self._update_common_parameter('pan', v)
        )
        pan.setValue(self.current_patch.pan - 64)
        
        # Create send controls
        reverb = Slider(
            "Reverb Send", 0, 127,
            lambda v: self._update_common_parameter('reverb_send', v)
        )
        delay = Slider(
            "Delay Send", 0, 127,
            lambda v: self._update_common_parameter('delay_send', v)
        )
        fx = Slider(
            "FX Send", 0, 127,
            lambda v: self._update_common_parameter('fx_send', v)
        )
        
        reverb.setValue(self.current_patch.reverb_send)
        delay.setValue(self.current_patch.delay_send)
        fx.setValue(self.current_patch.fx_send)
        
        # Add controls to layout
        layout.addWidget(level)
        layout.addWidget(pan)
        layout.addWidget(reverb)
        layout.addWidget(delay)
        layout.addWidget(fx)
        
        return frame 

    def _update_common_parameter(self, param: str, value: int):
        """Update a common parameter"""
        try:
            # Update the data model
            setattr(self.current_patch, param, value)
            
            # Get parameter offset from DR dictionary
            param_offset = DR['common'][param][0]
            
            # Send MIDI message
            msg = JDXiSysEx.create_parameter_message(
                area=DRUM_KIT_AREA,
                part=param_offset,
                group=0x00,
                param=value
            )
            
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                logging.debug(f"Sent common parameter: param={hex(param_offset)} value={value}")
                
        except Exception as e:
            logging.error(f"Error updating common parameter {param}: {str(e)}") 

    def _send_parameter(self, pad_num: int, param: int, value: int):
        """Send drum pad parameter change"""
        try:
            msg = JDXiSysEx.create_parameter_message(
                area=DRUM_KIT_AREA,
                part=pad_num,  # Pad number
                group=0x00,    # Fixed group
                param=param,   # Parameter within pad
                value=value   # Parameter value
            )
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                logging.debug(f"Sent drum parameter: pad={pad_num} param={hex(param)} value={value}")
        except Exception as e:
            logging.error(f"Error sending drum parameter: {str(e)}") 

    def load_preset(self, preset_name: str):
        """Load a preset patch"""
        try:
            if preset_name in SN_PRESETS:
                # Extract program number from preset name (first 3 digits)
                program_num = int(preset_name.split(':')[0])
                # Send program change
                self._send_program_change(program_num)
                logging.info(f"Loaded drum preset: {preset_name}")
            else:
                logging.error(f"Preset not found: {preset_name}")
                
        except Exception as e:
            logging.error(f"Error loading preset {preset_name}: {str(e)}")

    def _send_program_change(self, program_num: int):
        """Send program change message"""
        try:
            msg = JDXiSysEx.create_program_change_message(
                area=DRUM_KIT_AREA,
                program=program_num
            )
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                logging.debug(f"Sent program change: {program_num}")
            
        except Exception as e:
            logging.error(f"Error sending program change: {str(e)}") 

    def _create_drum_pads(self):
        """Create drum pad grid"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header("DRUM PADS", Style.DRUM_BG))
        
        # Create grid for pads
        grid = QGridLayout()
        grid.setSpacing(5)
        
        # Create 4x4 grid of pads
        for i in range(16):
            row = i // 4
            col = i % 4
            
            # Create pad button
            pad = QPushButton()
            pad.setFixedSize(60, 60)
            pad.setCheckable(True)
            
            # Style the pad
            pad.setStyleSheet("""
                QPushButton {
                    background-color: #333;
                    border: 2px solid #555;
                    border-radius: 5px;
                }
                QPushButton:checked {
                    background-color: #666;
                    border-color: #888;
                }
            """)
            
            # Add note number label
            if hasattr(self, 'pad_notes') and i < len(self.pad_notes):
                note = self.pad_notes[i]
                if note:  # Only add if we have a valid note number
                    grid.addWidget(pad, row, col)
        
        layout.addLayout(grid)
        return frame 

    def _create_common_section(self):
        """Create common parameters section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header("COMMON", Style.DRUM_BG))
        
        # Pan control (-64 to +63 maps to 0-127)
        pan = Slider(
            "Pan", -64, 63,
            lambda v: self._send_common_parameter("pan", v + 64)  # Add offset for center
        )
        layout.addWidget(pan)
        
        return frame
        
    def _send_common_parameter(self, param_name: str, value: int):
        """Send drum kit common parameter change"""
        try:
            # Get parameter info from DR dictionary
            param_info = DR['common'].get(param_name)
            if not param_info:
                logging.error(f"Unknown common parameter: {param_name}")
                return
                
            param_addr = param_info[0]  # Get address from tuple
            
            # Create parameter message with value
            msg = JDXiSysEx.create_parameter_message(
                area=DRUM_KIT_AREA,
                part=0x00,  # Common parameters
                group=COMMON_GROUP,
                param=param_addr,
                value=value
            )
            
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                logging.debug(f"Sent drum common parameter {param_name}: {value}")
                
            # Update local patch data
            setattr(self.current_patch, param_name, value)
                
        except Exception as e:
            logging.error(f"Error updating common parameter {param_name}: {str(e)}") 