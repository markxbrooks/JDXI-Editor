from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QComboBox, QScrollArea
)
from PySide6.QtCore import Qt
import logging

from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.midi.constants import EFFECTS_AREA

class EffectsEditor(BaseEditor):
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(midi_helper, parent)
        self.setWindowTitle("Effects")
        
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create container widget
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        
        # Add custom style for effects groups
        container.setStyleSheet("""
            QGroupBox {
                border: 1px solid #FF0000;  /* Red border */
                border-radius: 3px;
                margin-top: 1.5ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                color: #FFFFFF;
                background-color: #1A1A1A;
            }
        """)
        
        # Add sections
        container_layout.addWidget(self._create_effect1_section())
        container_layout.addWidget(self._create_effect2_section())
        container_layout.addWidget(self._create_delay_section())  # Add Delay section
        container_layout.addWidget(self._create_reverb_section())  # Add Reverb section
        
        # Add container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _create_effect1_section(self):
        """Create Effect 1 section"""
        group = QGroupBox("Effect 1")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Effect Type
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type"))
        self.efx1_type = QComboBox()
        self.efx1_type.addItems([
            "OFF", "DISTORTION", "FUZZ", "COMPRESSOR", "BIT CRUSHER"
        ])
        self.efx1_type.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x00, v)  # EFX1 Type
        )
        type_row.addWidget(self.efx1_type)
        layout.addLayout(type_row)
        
        # Level
        self.efx1_level = Slider("Level", 0, 127)
        self.efx1_level.valueChanged.connect(
            lambda v: self._send_parameter(0x01, v)  # EFX1 Level
        )
        layout.addWidget(self.efx1_level)
        
        # Send Levels
        self.efx1_delay_send = Slider("Delay Send", 0, 127)
        self.efx1_delay_send.valueChanged.connect(
            lambda v: self._send_parameter(0x02, v)  # EFX1 Delay Send
        )
        layout.addWidget(self.efx1_delay_send)
        
        self.efx1_reverb_send = Slider("Reverb Send", 0, 127)
        self.efx1_reverb_send.valueChanged.connect(
            lambda v: self._send_parameter(0x03, v)  # EFX1 Reverb Send
        )
        layout.addWidget(self.efx1_reverb_send)
        
        # Output Assign
        output_row = QHBoxLayout()
        output_row.addWidget(QLabel("Output"))
        self.efx1_output = QComboBox()
        self.efx1_output.addItems(["DIR", "EFX2"])
        self.efx1_output.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x04, v)  # EFX1 Output Assign
        )
        output_row.addWidget(self.efx1_output)
        layout.addLayout(output_row)
        
        # Effect Parameters (range -20000 to +20000)
        self.efx1_param1 = Slider("Parameter 1", -20000, 20000)
        self.efx1_param1.valueChanged.connect(
            lambda v: self._send_parameter(0x11, v + 32768)  # Center at 0
        )
        layout.addWidget(self.efx1_param1)
        
        self.efx1_param2 = Slider("Parameter 2", -20000, 20000)
        self.efx1_param2.valueChanged.connect(
            lambda v: self._send_parameter(0x15, v + 32768)  # Center at 0
        )
        layout.addWidget(self.efx1_param2)
        
        return group

    def _create_effect2_section(self):
        """Create Effect 2 section"""
        group = QGroupBox("Effect 2")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Effect Type
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type"))
        self.efx2_type = QComboBox()
        self.efx2_type.addItems([
            "OFF", "PHASER", "FLANGER", "DELAY", "CHORUS"  # Types 0, 5-8
        ])
        self.efx2_type.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x20, 0 if v == 0 else v + 4)  # Map to correct values
        )
        type_row.addWidget(self.efx2_type)
        layout.addLayout(type_row)
        
        # Level
        self.efx2_level = Slider("Level", 0, 127)
        self.efx2_level.valueChanged.connect(
            lambda v: self._send_parameter(0x21, v)  # EFX2 Level
        )
        layout.addWidget(self.efx2_level)
        
        # Send Levels
        self.efx2_delay_send = Slider("Delay Send", 0, 127)
        self.efx2_delay_send.valueChanged.connect(
            lambda v: self._send_parameter(0x22, v)  # EFX2 Delay Send
        )
        layout.addWidget(self.efx2_delay_send)
        
        self.efx2_reverb_send = Slider("Reverb Send", 0, 127)
        self.efx2_reverb_send.valueChanged.connect(
            lambda v: self._send_parameter(0x23, v)  # EFX2 Reverb Send
        )
        layout.addWidget(self.efx2_reverb_send)
        
        # Effect Parameters (range -20000 to +20000)
        self.efx2_param1 = Slider("Parameter 1", -20000, 20000)
        self.efx2_param1.valueChanged.connect(
            lambda v: self._send_parameter(0x31, v + 32768)  # Center at 0
        )
        layout.addWidget(self.efx2_param1)
        
        self.efx2_param2 = Slider("Parameter 2", -20000, 20000)
        self.efx2_param2.valueChanged.connect(
            lambda v: self._send_parameter(0x35, v + 32768)  # Center at 0
        )
        layout.addWidget(self.efx2_param2)
        
        # Additional parameters up to 32 can be added based on effect type
        # We can dynamically show/hide these based on the selected effect
        self.efx2_additional_params = []
        for i in range(3, 33):  # Parameters 3-32
            param = Slider(f"Parameter {i}", -20000, 20000)
            param.valueChanged.connect(
                lambda v, i=i: self._send_parameter(0x31 + (i-1)*4, v + 32768)
            )
            param.hide()  # Hide by default
            self.efx2_additional_params.append(param)
            layout.addWidget(param)
        
        return group

    def _create_delay_section(self):
        """Create Delay section"""
        group = QGroupBox("Delay")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Level
        self.delay_level = Slider("Level", 0, 127)
        self.delay_level.valueChanged.connect(
            lambda v: self._send_parameter(0x41, v)  # Delay Level
        )
        layout.addWidget(self.delay_level)
        
        # Reverb Send Level
        self.delay_reverb_send = Slider("Reverb Send", 0, 127)
        self.delay_reverb_send.valueChanged.connect(
            lambda v: self._send_parameter(0x43, v)  # Delay Reverb Send
        )
        layout.addWidget(self.delay_reverb_send)
        
        # Create parameter group for better organization
        param_group = QGroupBox("Parameters")
        param_layout = QVBoxLayout()
        param_group.setLayout(param_layout)
        
        # Effect Parameters (range -20000 to +20000)
        self.delay_params = []
        for i in range(1, 25):  # 24 parameters
            param = Slider(f"Parameter {i}", -20000, 20000)
            param.valueChanged.connect(
                lambda v, i=i: self._send_parameter(0x44 + (i-1)*4, v + 32768)  # Center at 0
            )
            param_layout.addWidget(param)
            self.delay_params.append(param)
        
        # Add parameter group to scrollable area
        param_scroll = QScrollArea()
        param_scroll.setWidget(param_group)
        param_scroll.setWidgetResizable(True)
        param_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        param_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        layout.addWidget(param_scroll)
        
        return group

    def _create_reverb_section(self):
        """Create Reverb section"""
        group = QGroupBox("Reverb")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Level control
        self.reverb_level = Slider("Level", 0, 127)
        self.reverb_level.valueChanged.connect(
            lambda v: self._send_parameter(0x61, v)  # Reverb Level
        )
        layout.addWidget(self.reverb_level)
        
        return group

    def _update_efx2_parameters(self, effect_type: int):
        """Show/hide parameters based on effect type"""
        # Number of parameters for each effect type
        param_counts = {
            0: 0,   # OFF
            5: 8,   # PHASER
            6: 6,   # FLANGER
            7: 4,   # DELAY
            8: 6    # CHORUS
        }
        
        # Get number of parameters for current effect
        count = param_counts.get(effect_type, 0)
        
        # Show/hide parameters
        for i, param in enumerate(self.efx2_additional_params):
            param.setVisible(i < count)

    def _update_delay_parameters(self, show_all: bool = False):
        """Show/hide delay parameters
        
        Args:
            show_all: If True, show all parameters, otherwise show commonly used ones
        """
        # Common parameter names and indices to show by default
        common_params = {
            0: "Time",
            1: "Feedback",
            2: "High Damp",
            3: "Low Damp",
            4: "Spread"
        }
        
        for i, param in enumerate(self.delay_params):
            if show_all:
                param.setVisible(True)
                if i in common_params:
                    param.setLabel(common_params[i])
            else:
                param.setVisible(i in common_params)
                if i in common_params:
                    param.setLabel(common_params[i])

    def _send_parameter(self, param: int, value: int):
        """Send parameter change to synth"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=EFFECTS_AREA,
                part=0x00,
                group=0x00,
                param=param,
                value=value
            )