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
    DRUM_KIT_AREA, SUBGROUP_ZERO, DrumPad
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

    def _create_drum_pad(self, pad_number):
        """Initialize a drum pad's controls"""
        try:
            pad = self.current_patch.pads[pad_number]
            frame = QFrame()
            frame.setFrameStyle(QFrame.StyledPanel)
            layout = QVBoxLayout(frame)

            # Create wave selector
            wave_combo = QComboBox()
            wave_names = []
            for category in DRUM_PARTS.values():
                wave_names.extend(category)
            wave_combo.addItems(wave_names)
            wave_combo.setCurrentIndex(pad.wave)
            wave_combo.currentIndexChanged.connect(
                lambda v: self._update_pad_parameter(pad_number, 'wave', v)
            )

            # Create mute group selector
            mute_combo = QComboBox()
            mute_combo.addItems(["OFF"] + [str(i) for i in MuteGroup.GROUPS])
            mute_combo.setCurrentIndex(pad.mute_group)
            mute_combo.currentIndexChanged.connect(
                lambda v: self._update_pad_parameter(pad_number, 'mute_group', v)
            )

            # Create level control
            level = Slider(
                "Level", 0, 127,
                lambda v: self._update_pad_parameter(pad_number, 'level', v)
            )
            level.setValue(pad.level)

            # Create pan control
            pan = Slider(
                "Pan", -64, 63,
                lambda v: self._update_pad_parameter(pad_number, 'pan', v)
            )
            pan.setValue(pad.pan - 64)  # Convert from 0-127 to -64-63

            # Create tune control
            tune = Slider(
                "Tune", -50, 50,
                lambda v: self._update_pad_parameter(pad_number, 'tune', v)
            )
            tune.setValue(pad.tune)

            # Create decay control
            decay = Slider(
                "Decay", 0, 127,
                lambda v: self._update_pad_parameter(pad_number, 'decay', v)
            )
            decay.setValue(pad.decay)

            # Create sends section
            sends_frame = QFrame()
            sends_layout = QVBoxLayout(sends_frame)

            reverb_send = Slider(
                "Reverb", 0, 127,
                lambda v: self._update_pad_parameter(pad_number, 'reverb_send', v)
            )
            delay_send = Slider(
                "Delay", 0, 127,
                lambda v: self._update_pad_parameter(pad_number, 'delay_send', v)
            )
            fx_send = Slider(
                "FX", 0, 127,
                lambda v: self._update_pad_parameter(pad_number, 'fx_send', v)
            )

            reverb_send.setValue(pad.reverb_send)
            delay_send.setValue(pad.delay_send)
            fx_send.setValue(pad.fx_send)

            sends_layout.addWidget(reverb_send)
            sends_layout.addWidget(delay_send)
            sends_layout.addWidget(fx_send)

            # Add all controls to layout
            layout.addWidget(wave_combo)
            layout.addWidget(mute_combo)
            layout.addWidget(level)
            layout.addWidget(pan)
            layout.addWidget(tune)
            layout.addWidget(decay)
            layout.addWidget(sends_frame)

            return frame

        except Exception as e:
            logging.error(f"Error creating drum pad {pad_number}: {str(e)}")
            return None

    def _update_pad_parameter(self, pad_number: int, param: str, value: int):
        """Update a parameter for a specific pad"""
        try:
            # Update the data model
            pad = self.current_patch.pads[pad_number]
            setattr(pad, param, value)

            # Calculate parameter address
            param_offset = DR['pad'][param][0]  # Get parameter offset from DR dictionary
            address = pad_number * DrumPad.PARAM_OFFSET + param_offset

            # Send MIDI message
            msg = JDXiSysEx.create_parameter_message(
                area=DRUM_KIT_AREA,
                part=pad_number,  # Pad number
                group=0x00,    # Fixed group
                param=param_offset,   # Parameter within pad
                value=value   # Parameter value
            )
            
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                logging.debug(f"Sent drum parameter: pad={pad_number} param={hex(param_offset)} value={value}")

        except Exception as e:
            logging.error(f"Error updating pad {pad_number} {param}: {str(e)}")

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
        
        # Add preset panel
        self.preset_panel = PresetPanel('drums', self)
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