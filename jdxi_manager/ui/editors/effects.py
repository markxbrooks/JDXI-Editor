from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                              QLabel, QSlider, QGroupBox, QTabWidget, QScrollArea)
from PySide6.QtCore import Qt, Signal

from jdxi_manager.midi.constants import (Effect1, Effect2, Delay, Reverb,
                                       Effect1Message, Effect2Message, 
                                       DelayMessage, ReverbMessage)
from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.data.effects import (EFX1_PARAMS, EFX2_PARAMS, 
                                     MAIN_DELAY_PARAMS, MAIN_REVERB_PARAMS)

class ParameterWidget(QWidget):
    """Widget for a single effect parameter"""
    valueChanged = Signal(int)  # Signal when value changes
    
    def __init__(self, param, parent=None):
        super().__init__(parent)
        self.param = param
        self.setup_ui()
        
    def setup_ui(self):
        """Create the parameter UI"""
        layout = QHBoxLayout()
        
        # Parameter name
        name_label = QLabel(self.param.name)
        layout.addWidget(name_label)
        
        # Parameter slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(self.param.min_value, self.param.max_value)
        self.slider.setValue(self.param.default)
        layout.addWidget(self.slider)
        
        # Value display
        self.value_label = QLabel(f"{self.param.default}{self.param.unit}")
        layout.addWidget(self.value_label)
        
        # Update value display when slider moves
        self.slider.valueChanged.connect(self.update_value)
        
        self.setLayout(layout)
        
    def update_value(self, value):
        """Update the value display and emit signal"""
        self.value_label.setText(f"{value}{self.param.unit}")
        self.valueChanged.emit(value)

    def get_value(self) -> int:
        """Get current parameter value"""
        return self.slider.value()

    def set_value(self, value: int):
        """Set parameter value"""
        self.slider.setValue(value)

class BaseEffectPanel(QWidget):
    """Base class for effect panels"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor = parent
        self.param_widgets = []
        self.setup_ui()
        self.connect_signals()

    def connect_signals(self):
        """Connect parameter signals to MIDI updates"""
        # Connect level slider
        self.level_slider.valueChanged.connect(self.level_changed)
        
        # Connect send sliders if they exist
        if hasattr(self, 'delay_slider'):
            self.delay_slider.valueChanged.connect(self.delay_send_changed)
        if hasattr(self, 'reverb_slider'):
            self.reverb_slider.valueChanged.connect(self.reverb_send_changed)

    def level_changed(self, value):
        """Handle level parameter change"""
        self.send_parameter_update(self.get_level_param(), value)

    def delay_send_changed(self, value):
        """Handle delay send parameter change"""
        self.send_parameter_update(self.get_delay_send_param(), value)

    def reverb_send_changed(self, value):
        """Handle reverb send parameter change"""
        self.send_parameter_update(self.get_reverb_send_param(), value)

    def parameter_changed(self, param_num: int, value: int):
        """Handle effect parameter change"""
        param_offset = self.get_param_offset(param_num)
        self.send_parameter_update(param_offset, value)

    def send_parameter_update(self, param: int, value: int):
        """Send MIDI message for parameter update"""
        msg = self.create_message(param, value)
        if msg and self.editor and self.editor.midi:
            self.editor.midi.send_message(msg)

    # Abstract methods to be implemented by subclasses
    def get_level_param(self) -> int:
        """Get parameter number for level control"""
        raise NotImplementedError

    def get_delay_send_param(self) -> int:
        """Get parameter number for delay send"""
        raise NotImplementedError

    def get_reverb_send_param(self) -> int:
        """Get parameter number for reverb send"""
        raise NotImplementedError

    def get_param_offset(self, param_num: int) -> int:
        """Get parameter offset for numbered parameter"""
        raise NotImplementedError

    def create_message(self, param: int, value: int):
        """Create MIDI message for parameter update"""
        raise NotImplementedError

class Effect1Panel(BaseEffectPanel):
    """EFX1 panel implementation"""
    
    def get_level_param(self) -> int:
        return Effect1.LEVEL.value

    def get_delay_send_param(self) -> int:
        return Effect1.DELAY_SEND.value

    def get_reverb_send_param(self) -> int:
        return Effect1.REVERB_SEND.value

    def get_param_offset(self, param_num: int) -> int:
        return Effect1.get_param_offset(param_num)

    def create_message(self, param: int, value: int):
        return Effect1Message(param=param, value=value)

    def type_changed(self, index):
        """Handle effect type change"""
        self.send_parameter_update(Effect1.TYPE.value, index)
        self.update_parameters(EFX1_PARAMS[index])

class Effect2Panel(BaseEffectPanel):
    """EFX2 panel with phaser/flanger/delay/chorus controls"""
    
    def setup_ui(self):
        super().setup_ui()
        
        # Add effect type selector
        type_layout = QHBoxLayout()
        type_label = QLabel("Type")
        self.type_combo = QComboBox()
        self.type_combo.addItems(['OFF', 'PHASER', 'FLANGER', 'DELAY', 'CHORUS'])
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        self.layout().insertLayout(0, type_layout)
        
        # Update parameters when type changes
        self.type_combo.currentIndexChanged.connect(self.type_changed)
        self.type_changed(0)
        
    def type_changed(self, index):
        """Update parameters when effect type changes"""
        self.update_parameters(EFX2_PARAMS[index])

class DelayPanel(BaseEffectPanel):
    """Delay panel with delay-specific controls"""
    
    def setup_ui(self):
        super().setup_ui()
        # Remove delay send from base panel
        self.delay_slider.setParent(None)
        # Add delay parameters
        self.update_parameters(MAIN_DELAY_PARAMS)

class ReverbPanel(BaseEffectPanel):
    """Reverb panel with reverb-specific controls"""
    
    def setup_ui(self):
        super().setup_ui()
        # Remove reverb send from base panel
        self.reverb_slider.setParent(None)
        # Add reverb parameters
        self.update_parameters(MAIN_REVERB_PARAMS)

class EffectsEditor(BaseEditor):
    """Unified effects editor for EFX1, EFX2, Delay, and Reverb"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Create the effects editor UI"""
        layout = QVBoxLayout()
        
        # Create tabs for each effect section
        tabs = QTabWidget()
        tabs.addTab(Effect1Panel(self), "EFX 1")
        tabs.addTab(Effect2Panel(self), "EFX 2")
        tabs.addTab(DelayPanel(self), "Delay")
        tabs.addTab(ReverbPanel(self), "Reverb")
        
        layout.addWidget(tabs)
        self.setLayout(layout)

    def handle_midi_message(self, message):
        """Handle incoming MIDI messages"""
        # TODO: Update UI based on received messages
        pass