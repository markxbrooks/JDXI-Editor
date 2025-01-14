from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox
)
from PySide6.QtCore import Qt

from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.ui.widgets.waveform import WaveformButton
from jdxi_manager.midi.constants import (
    DIGITAL_SYNTH_AREA,
    DIGITAL_1_PART,
    DIGITAL_2_PART,
    DigitalToneCC,
    Waveform
)

class DigitalSynthEditor(BaseEditor):
    def __init__(self, midi_helper=None, synth_num=1, parent=None):
        super().__init__(midi_helper, parent)
        self.synth_num = synth_num
        self.part = DIGITAL_1_PART if synth_num == 1 else DIGITAL_2_PART
        self.setWindowTitle(f"Digital Synth {synth_num}")
        
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)
        
        # Additional styling
        self.setStyleSheet("""
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
        """)
        
        # Add sections side by side
        main_layout.addWidget(self._create_oscillator_section())
        main_layout.addWidget(self._create_filter_section())
        main_layout.addWidget(self._create_amp_section())
        main_layout.addWidget(self._create_lfo_section())
        
        # Set fixed size
        self.setFixedSize(800, 400)

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

    def _on_waveform_selected(self, waveform):
        # Uncheck other waveform buttons
        for btn in self.wave_buttons.values():
            if btn.waveform != waveform:
                btn.setChecked(False)
                
        # Send MIDI message if helper exists
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=self.part,
                group=0x00,
                param=DigitalToneCC.OSC_WAVE,
                value=waveform.midi_value
            ) 

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

    def _on_slider_value_changed(self, param, value):
        """Handle slider value changes"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=self.part,
                group=0x00,
                param=param,
                value=value
            ) 