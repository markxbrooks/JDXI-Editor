from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QScrollArea
)
from PySide6.QtCore import Qt

from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.ui.widgets.waveform import WaveformButton
from jdxi_manager.midi.constants import (
    ANALOG_SYNTH_AREA,
    ANALOG_PART,
    AnalogToneCC,
    Waveform
)
from jdxi_manager.midi.constants.analog import (
    AnalogToneCC
)

class AnalogSynthEditor(BaseEditor):
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(midi_helper, parent)
        self.setWindowTitle("Analog Synth")
        
        # Allow resizing
        self.setMinimumSize(400, 300)  # Set minimum size
        self.resize(800, 600)  # Set default size
        
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create scroll area for resizable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create container widget for scroll area
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        """
        # Additional styling specific to analog editor
        #container.setStyleSheet(""
            QWidget {
                background-color: #2D2D2D;
                color: #CCCCCC;
            }
            QGroupBox {
                border: 1px solid #444444;
                border-radius: 3px;
                margin-top: 1.5ex;
                padding: 10px;
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                background-color: #2D2D2D;
            }
            QLabel {
                color: #CCCCCC;
                font-size: 11px;
            }
            QSlider::groove:vertical {
                background: #333333;
                width: 4px;
                border-radius: 2px;
            }
            QSlider::handle:vertical {
                background: #B22222;
                border: 1px solid #FF4444;
                height: 10px;
                margin: 0 -8px;
                border-radius: 5px;
            }
            QSlider::handle:vertical:hover {
                background: #FF4444;
            }
        "")"""
        
        # Add sections side by side
        container_layout.addWidget(self._create_oscillator_section())
        container_layout.addWidget(self._create_filter_section())
        container_layout.addWidget(self._create_amp_section())
        container_layout.addWidget(self._create_lfo_section())
        
        # Add container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        # Connect sliders to MIDI parameters
        self.coarse.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.OSC_PITCH, v + 64)  # Center at 0
        )
        self.fine.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.OSC_FINE, v + 64)   # Center at 0
        )
        
        self.cutoff.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.FILTER_CUTOFF, v)
        )
        self.resonance.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.FILTER_RESO, v)
        )
        
        # Connect envelope sliders
        for name, cc in [
            ('A', AnalogToneCC.FILTER_ENV_A),
            ('D', AnalogToneCC.FILTER_ENV_D),
            ('S', AnalogToneCC.FILTER_ENV_S),
            ('R', AnalogToneCC.FILTER_ENV_R)
        ]:
            self.filter_env[name].valueChanged.connect(
                lambda v, cc=cc: self._send_cc(cc, v)
            )
        
        for name, cc in [
            ('A', AnalogToneCC.AMP_ENV_A),
            ('D', AnalogToneCC.AMP_ENV_D),
            ('S', AnalogToneCC.AMP_ENV_S),
            ('R', AnalogToneCC.AMP_ENV_R)
        ]:
            self.amp_env[name].valueChanged.connect(
                lambda v, cc=cc: self._send_cc(cc, v)
            )
        
        self.level.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.AMP_LEVEL, v)
        )
        
        self.lfo_rate.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.LFO_RATE, v)
        )
        self.lfo_depth.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.LFO_DEPTH, v)
        )

    def _create_oscillator_section(self):
        group = QGroupBox("Oscillator")
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 15, 5, 5)
        group.setLayout(layout)
        
        # Waveform buttons
        wave_layout = QHBoxLayout()
        wave_layout.setSpacing(5)
        self.wave_buttons = {}
        for waveform in [Waveform.SAW, Waveform.SQUARE, Waveform.TRIANGLE]:
            btn = WaveformButton(waveform)
            btn.waveform_selected.connect(self._on_waveform_selected)
            self.wave_buttons[waveform] = btn
            wave_layout.addWidget(btn)
        layout.addLayout(wave_layout)
        
        # Add spacing
        layout.addSpacing(10)
        
        # Tuning controls
        self.coarse = Slider("Coarse", -24, 24)
        self.fine = Slider("Fine", -50, 50)
        layout.addWidget(self.coarse)
        layout.addWidget(self.fine)
        
        return group

    def _create_filter_section(self):
        group = QGroupBox("Filter")
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 15, 5, 5)
        group.setLayout(layout)
        
        # Filter controls
        self.cutoff = Slider("Cutoff", 0, 127)
        self.resonance = Slider("Resonance", 0, 127)
        layout.addWidget(self.cutoff)
        layout.addWidget(self.resonance)
        
        # Add spacing
        layout.addSpacing(10)
        
        # Filter envelope
        env_group = QGroupBox("Envelope")
        env_layout = QHBoxLayout()
        env_layout.setSpacing(5)
        env_layout.setContentsMargins(5, 15, 5, 5)
        env_group.setLayout(env_layout)
        
        self.filter_env = {
            'A': Slider("A", 0, 127),
            'D': Slider("D", 0, 127),
            'S': Slider("S", 0, 127),
            'R': Slider("R", 0, 127)
        }
        
        for slider in self.filter_env.values():
            env_layout.addWidget(slider)
            
        layout.addWidget(env_group)
        return group

    def _create_amp_section(self):
        group = QGroupBox("Amplifier")
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 15, 5, 5)
        group.setLayout(layout)
        
        # Level control
        self.level = Slider("Level", 0, 127)
        layout.addWidget(self.level)
        
        # Add spacing
        layout.addSpacing(10)
        
        # Amp envelope
        env_group = QGroupBox("Envelope")
        env_layout = QHBoxLayout()
        env_layout.setSpacing(5)
        env_layout.setContentsMargins(5, 15, 5, 5)
        env_group.setLayout(env_layout)
        
        self.amp_env = {
            'A': Slider("A", 0, 127),
            'D': Slider("D", 0, 127),
            'S': Slider("S", 0, 127),
            'R': Slider("R", 0, 127)
        }
        
        for slider in self.amp_env.values():
            env_layout.addWidget(slider)
            
        layout.addWidget(env_group)
        return group

    def _create_lfo_section(self):
        group = QGroupBox("LFO")
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 15, 5, 5)
        group.setLayout(layout)
        
        # LFO controls
        self.lfo_rate = Slider("Rate", 0, 127)
        self.lfo_depth = Slider("Depth", 0, 127)
        layout.addWidget(self.lfo_rate)
        layout.addWidget(self.lfo_depth)
        
        return group

    def _on_waveform_selected(self, waveform):
        # Uncheck other waveform buttons
        for btn in self.wave_buttons.values():
            if btn.waveform != waveform:
                btn.setChecked(False)
                
        # Send MIDI message if helper exists
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=0x00,
                param=AnalogToneCC.OSC_WAVE,
                value=waveform.midi_value
            ) 

    def _send_cc(self, cc: AnalogToneCC, value: int):
        """Send MIDI CC message"""
        if self.midi_helper:
            self.midi_helper.send_cc(cc, value, channel=ANALOG_PART) 