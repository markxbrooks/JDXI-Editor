from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QComboBox, QCheckBox, QPushButton,
    QGroupBox, QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
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
    EFFECTS_AREA, EFFECTS_GROUP,
    EffectType,
    EffectGroup
)
from jdxi_manager.data.effects import (
    FX,
    EffectPatch
)
from jdxi_manager.ui.editors.base_editor import BaseEditor

class EffectsValidator:
    """Validator for JD-Xi effects parameters"""
    
    # Parameter ranges
    RANGES = {
        # Effect 1 & 2
        (0x50, 0x00): (0, 9),    # Effect type (10 types)
        (0x50, 0x01): (0, 127),  # Level
        (0x50, 0x02): (0, 127),  # Param 1
        (0x50, 0x03): (0, 127),  # Param 2
        (0x60, 0x00): (0, 9),    # Effect type
        (0x60, 0x01): (0, 127),  # Level
        (0x60, 0x02): (0, 127),  # Param 1
        (0x60, 0x03): (0, 127),  # Param 2
        
        # Reverb
        (0x10, 0x00): (0, 5),    # Type (6 types)
        (0x10, 0x01): (0, 127),  # Level
        (0x10, 0x02): (0, 127),  # Time
        (0x10, 0x03): (0, 127),  # Pre-delay
        
        # Delay
        (0x20, 0x00): (0, 1),    # Sync (bool)
        (0x20, 0x01): (0, 127),  # Time
        (0x20, 0x02): (0, 10),   # Note (11 values)
        (0x20, 0x03): (0, 127),  # Feedback
        (0x20, 0x04): (0, 127),  # HF Damp
        (0x20, 0x05): (0, 127),  # Level
        
        # Chorus
        (0x30, 0x00): (0, 127),  # Rate
        (0x30, 0x01): (0, 127),  # Depth
        (0x30, 0x02): (0, 127),  # Level
        
        # Master EQ
        (0x40, 0x00): (0, 24),   # Low (-12 to +12)
        (0x40, 0x01): (0, 24),   # Mid (-12 to +12)
        (0x40, 0x02): (0, 24),   # High (-12 to +12)
        (0x40, 0x03): (0, 127),  # Master Level
    }
    
    @classmethod
    def validate_parameter(cls, section, parameter, value):
        """Validate a parameter value"""
        # Check section range
        if section not in [0x50, 0x60, 0x10, 0x20, 0x30, 0x40]:
            raise ValueError(f"Invalid section: {hex(section)}")
            
        # Get parameter range
        param_range = cls.RANGES.get((section, parameter))
        if param_range is None:
            raise ValueError(f"Invalid parameter {hex(parameter)} for section {hex(section)}")
            
        # Check value range
        min_val, max_val = param_range
        if not min_val <= value <= max_val:
            raise ValueError(f"Value {value} out of range ({min_val}-{max_val})")
            
        return True

    @classmethod
    def validate_power_message(cls, section, value):
        """Validate effect power message"""
        # Check section is valid effect
        if section not in [0x08, 0x09, 0x0A]:  # Reverb, Delay, Chorus
            raise ValueError(f"Invalid effect section: {hex(section)}")
            
        # Check value is boolean
        if value not in [0, 1]:
            raise ValueError(f"Invalid power value: {value} (must be 0 or 1)")
            
        return True

class EffectsEditor(BaseEditor):
    """Editor for JD-Xi effects settings"""
    
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        
        # Set window properties
        self.setStyleSheet(Style.MAIN_STYLESHEET)
        self.setFixedWidth(1000)
        self.setMinimumHeight(600)
        self.setWindowTitle("Effects")
        
        # Create UI
        self._create_ui()
        
        # Request current patch data
        self._request_patch_data()
        
    def _request_patch_data(self):
        """Request current patch data from device"""
        try:
            self._send_sysex(
                bytes([0x16, 0x00, 0x00, 0x00]),  # Effects area
                bytes([0x00])  # Request all parameters
            )
        except Exception as e:
            logging.error(f"Error requesting patch data: {str(e)}")

    def _request_patch_name(self, preset_num: int):
        """Request patch name from device"""
        # Effects don't have patch names
        pass

    def _update_ui_from_sysex(self, addr: bytes, data: bytes):
        """Update UI based on received SysEx data"""
        # Check if it's for effects (0x16)
        if addr[0] != 0x16:
            return
            
        param = addr[3]
        value = data[0]
        
        # Update appropriate controls based on parameter
        self._update_parameter(param, value)
        
    def _create_ui(self):
        """Create the user interface"""
        # Create scroll area for main content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(scroll)
        
        # Create main widget
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create sections
        layout.addWidget(self._create_reverb_section())
        layout.addWidget(self._create_delay_section())
        layout.addWidget(self._create_chorus_section())
        layout.addWidget(self._create_master_eq_section())
        layout.addWidget(self._create_fx_section(1))  # Effect 1
        layout.addWidget(self._create_fx_section(2))  # Effect 2
        
        # Add stretch at bottom
        layout.addStretch()
        
        # Set the widget to scroll area
        scroll.setWidget(central)

    def _create_section_header(self, text: str) -> QLabel:
        """Create a section header"""
        header = QLabel(text)
        header.setStyleSheet(f"""
            background-color: {Style.HEADER_BG};
            color: white;
            padding: 5px;
            font-weight: bold;
            border-radius: 4px;
        """)
        return header
        
    def _create_reverb_section(self) -> QFrame:
        """Create reverb controls section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header("Reverb"))
        
        # Type selector
        self.reverb_type = QComboBox()
        self.reverb_type.addItems(["Room 1", "Room 2", "Stage 1", "Stage 2", "Hall 1", "Hall 2"])
        layout.addWidget(self.reverb_type)
        
        # Level control
        self.reverb_level = Slider("Level", 0, 127)
        layout.addWidget(self.reverb_level)
        
        # Time control
        self.reverb_time = Slider("Time", 0, 127)
        layout.addWidget(self.reverb_time)
        
        # Pre-delay control
        self.reverb_predelay = Slider("Pre-delay", 0, 127)
        layout.addWidget(self.reverb_predelay)
        
        return frame
        
    def _create_delay_section(self) -> QFrame:
        """Create delay controls section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header("Delay"))
        
        # Sync toggle
        self.delay_sync = QCheckBox("Sync to Tempo")
        layout.addWidget(self.delay_sync)
        
        # Time control
        self.delay_time = Slider("Time", 0, 127)
        layout.addWidget(self.delay_time)
        
        # Note selector (when synced)
        self.delay_note = QComboBox()
        self.delay_note.addItems(["1/32", "1/16", "1/8", "1/4", "1/2", "1/1"])
        self.delay_note.setVisible(False)
        layout.addWidget(self.delay_note)
        
        # Feedback control
        self.delay_feedback = Slider("Feedback", 0, 127)
        layout.addWidget(self.delay_feedback)
        
        # HF Damp control
        self.delay_hfdamp = Slider("HF Damp", 0, 127)
        layout.addWidget(self.delay_hfdamp)
        
        # Level control
        self.delay_level = Slider("Level", 0, 127)
        layout.addWidget(self.delay_level)
        
        return frame

    def _create_chorus_section(self) -> QFrame:
        """Create chorus controls section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header("Chorus"))
        
        # Rate control
        self.chorus_rate = Slider("Rate", 0, 127)
        layout.addWidget(self.chorus_rate)
        
        # Depth control
        self.chorus_depth = Slider("Depth", 0, 127)
        layout.addWidget(self.chorus_depth)
        
        # Level control
        self.chorus_level = Slider("Level", 0, 127)
        layout.addWidget(self.chorus_level)
        
        return frame
        
    def _create_master_eq_section(self) -> QFrame:
        """Create master EQ controls section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header("Master EQ"))
        
        # Low control (-12 to +12)
        self.eq_low = Slider("Low", -12, 12)
        layout.addWidget(self.eq_low)
        
        # Mid control (-12 to +12)
        self.eq_mid = Slider("Mid", -12, 12)
        layout.addWidget(self.eq_mid)
        
        # High control (-12 to +12)
        self.eq_high = Slider("High", -12, 12)
        layout.addWidget(self.eq_high)
        
        # Master Level control
        self.master_level = Slider("Master Level", 0, 127)
        layout.addWidget(self.master_level)
        
        return frame
        
    def _create_fx_section(self, fx_num: int) -> QFrame:
        """Create effect section controls"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header(f"Effect {fx_num}"))
        
        # Type selector
        type_selector = QComboBox()
        type_selector.addItems([
            "THRU", "DISTORTION", "FUZZ", "COMPRESSOR", "BITCRUSHER",
            "FLANGER", "PHASER", "RING MOD", "SLICER"
        ])
        layout.addWidget(type_selector)
        
        # Level control
        level = Slider("Level", 0, 127)
        layout.addWidget(level)
        
        # Parameter 1
        param1 = Slider("Parameter 1", 0, 127)
        layout.addWidget(param1)
        
        # Parameter 2
        param2 = Slider("Parameter 2", 0, 127)
        layout.addWidget(param2)
        
        # Store controls
        setattr(self, f'fx{fx_num}_type', type_selector)
        setattr(self, f'fx{fx_num}_level', level)
        setattr(self, f'fx{fx_num}_param1', param1)
        setattr(self, f'fx{fx_num}_param2', param2)
        
        return frame
        
    def _setup_parameter_bindings(self):
        """Set up MIDI parameter bindings"""
        # Reverb bindings
        self.reverb_type.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x10, 0x00, v))
        self.reverb_level.valueChanged.connect(
            lambda v: self._send_parameter(0x10, 0x01, v))
        self.reverb_time.valueChanged.connect(
            lambda v: self._send_parameter(0x10, 0x02, v))
        self.reverb_predelay.valueChanged.connect(
            lambda v: self._send_parameter(0x10, 0x03, v))
            
        # Delay bindings
        self.delay_sync.toggled.connect(
            lambda v: self._send_parameter(0x20, 0x00, int(v)))
        self.delay_time.valueChanged.connect(
            lambda v: self._send_parameter(0x20, 0x01, v))
        self.delay_note.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x20, 0x02, v))
        self.delay_feedback.valueChanged.connect(
            lambda v: self._send_parameter(0x20, 0x03, v))
        self.delay_hfdamp.valueChanged.connect(
            lambda v: self._send_parameter(0x20, 0x04, v))
        self.delay_level.valueChanged.connect(
            lambda v: self._send_parameter(0x20, 0x05, v))
            
        # Chorus bindings
        self.chorus_rate.valueChanged.connect(
            lambda v: self._send_parameter(0x30, 0x00, v))
        self.chorus_depth.valueChanged.connect(
            lambda v: self._send_parameter(0x30, 0x01, v))
        self.chorus_level.valueChanged.connect(
            lambda v: self._send_parameter(0x30, 0x02, v))
            
        # Master EQ bindings
        self.eq_low.valueChanged.connect(
            lambda v: self._send_parameter(0x40, 0x00, v + 12))  # Convert -12/+12 to 0-24
        self.eq_mid.valueChanged.connect(
            lambda v: self._send_parameter(0x40, 0x01, v + 12))
        self.eq_high.valueChanged.connect(
            lambda v: self._send_parameter(0x40, 0x02, v + 12))
        self.master_level.valueChanged.connect(
            lambda v: self._send_parameter(0x40, 0x03, v))
            
        # Effect 1 bindings
        self.fx1_type.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x50, 0x00, v))
        self.fx1_level.valueChanged.connect(
            lambda v: self._send_parameter(0x50, 0x01, v))
        self.fx1_param1.valueChanged.connect(
            lambda v: self._send_parameter(0x50, 0x02, v))
        self.fx1_param2.valueChanged.connect(
            lambda v: self._send_parameter(0x50, 0x03, v))
        
        # Effect 2 bindings
        self.fx2_type.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x60, 0x00, v))
        self.fx2_level.valueChanged.connect(
            lambda v: self._send_parameter(0x60, 0x01, v))
        self.fx2_param1.valueChanged.connect(
            lambda v: self._send_parameter(0x60, 0x02, v))
        self.fx2_param2.valueChanged.connect(
            lambda v: self._send_parameter(0x60, 0x03, v))
        
        # Handle delay sync state changes
        self.delay_sync.toggled.connect(self._handle_delay_sync)

    def _handle_delay_sync(self, sync_enabled: bool):
        """Handle delay sync mode changes"""
        self.delay_time.setVisible(not sync_enabled)
        self.delay_note.setVisible(sync_enabled)

    def _update_parameter(self, param: int, value: int):
        """Update UI control based on received parameter"""
        try:
            # Reverb parameters
            if param == 0x10:  # Reverb type
                self.reverb_type.setCurrentIndex(value)
            elif param == 0x11:  # Reverb level
                self.reverb_level.setValue(value)
            elif param == 0x12:  # Reverb time
                self.reverb_time.setValue(value)
            elif param == 0x13:  # Reverb pre-delay
                self.reverb_predelay.setValue(value)
            
            # Delay parameters
            elif param == 0x20:  # Delay sync
                self.delay_sync.setChecked(bool(value))
            elif param == 0x21:  # Delay time
                self.delay_time.setValue(value)
            elif param == 0x22:  # Delay note
                self.delay_note.setCurrentIndex(value)
            elif param == 0x23:  # Delay feedback
                self.delay_feedback.setValue(value)
            elif param == 0x24:  # Delay HF damp
                self.delay_hfdamp.setValue(value)
            elif param == 0x25:  # Delay level
                self.delay_level.setValue(value)
            
            # Chorus parameters
            elif param == 0x30:  # Chorus rate
                self.chorus_rate.setValue(value)
            elif param == 0x31:  # Chorus depth
                self.chorus_depth.setValue(value)
            elif param == 0x32:  # Chorus level
                self.chorus_level.setValue(value)
            
            # Master EQ parameters
            elif param == 0x40:  # EQ low
                self.eq_low.setValue(value - 12)  # Convert 0-24 to -12/+12
            elif param == 0x41:  # EQ mid
                self.eq_mid.setValue(value - 12)
            elif param == 0x42:  # EQ high
                self.eq_high.setValue(value - 12)
            elif param == 0x43:  # Master level
                self.master_level.setValue(value)
            
            # Effect 1 parameters
            elif param == 0x50:  # FX1 type
                self.fx1_type.setCurrentIndex(value)
            elif param == 0x51:  # FX1 level
                self.fx1_level.setValue(value)
            elif param == 0x52:  # FX1 param1
                self.fx1_param1.setValue(value)
            elif param == 0x53:  # FX1 param2
                self.fx1_param2.setValue(value)
            
            # Effect 2 parameters
            elif param == 0x60:  # FX2 type
                self.fx2_type.setCurrentIndex(value)
            elif param == 0x61:  # FX2 level
                self.fx2_level.setValue(value)
            elif param == 0x62:  # FX2 param1
                self.fx2_param1.setValue(value)
            elif param == 0x63:  # FX2 param2
                self.fx2_param2.setValue(value)
            
        except Exception as e:
            logging.error(f"Error updating parameter {hex(param)}: {str(e)}")

    def _send_parameter(self, section: int, param: int, value: int):
        """Send effect parameter change"""
        try:
            msg = JDXiSysEx.create_parameter_message(
                area=EFFECTS_AREA,
                part=section,
                group=0x00,
                param=param,
                value=value
            )
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                logging.debug(f"Sent effect parameter: section={hex(section)} param={hex(param)} value={value}")
        except Exception as e:
            logging.error(f"Error sending effect parameter: {str(e)}")