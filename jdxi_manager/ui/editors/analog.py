from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QScrollArea, QComboBox
)
from PySide6.QtCore import Qt

from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.ui.widgets.waveform import WaveformButton
from jdxi_manager.ui.widgets.switch import Switch
from jdxi_manager.midi.constants.analog import (
    AnalogToneCC,
    Waveform,
    ANALOG_SYNTH_AREA,
    ANALOG_PART
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
        
        # Connect oscillator controls
        self.coarse.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.OSC_COARSE, v + 64)  # Center at 0
        )
        self.fine.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.OSC_FINE, v + 64)   # Center at 0
        )
        
        # Connect filter controls
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
        
        # Connect amp level
        self.level.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.AMP_LEVEL, v)
        )

    def _create_oscillator_section(self):
        group = QGroupBox("Oscillator")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Waveform buttons
        wave_layout = QHBoxLayout()
        self.wave_buttons = {}
        for waveform in [Waveform.SAW, Waveform.TRIANGLE, Waveform.PULSE]:
            btn = WaveformButton(waveform)
            btn.waveform_selected.connect(self._on_waveform_selected)
            self.wave_buttons[waveform] = btn
            wave_layout.addWidget(btn)
        layout.addLayout(wave_layout)
        
        # Tuning controls
        tuning_group = QGroupBox("Tuning")
        tuning_layout = QVBoxLayout()
        tuning_group.setLayout(tuning_layout)
        
        self.coarse = Slider("Coarse", -24, 24)  # Will be mapped to 40-88
        self.fine = Slider("Fine", -50, 50)      # Will be mapped to 14-114
        tuning_layout.addWidget(self.coarse)
        tuning_layout.addWidget(self.fine)
        layout.addWidget(tuning_group)
        
        # Pulse Width controls
        pw_group = QGroupBox("Pulse Width")
        pw_layout = QVBoxLayout()
        pw_group.setLayout(pw_layout)
        
        self.pw = Slider("Width", 0, 127)
        self.pw.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.OSC_PW, v)
        )
        
        self.pw_mod = Slider("Mod Depth", 0, 127)
        self.pw_mod.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.OSC_PWM, v)
        )
        
        pw_layout.addWidget(self.pw)
        pw_layout.addWidget(self.pw_mod)
        layout.addWidget(pw_group)
        
        # Pitch Envelope
        pitch_env_group = QGroupBox("Pitch Envelope")
        pitch_env_layout = QVBoxLayout()
        pitch_env_group.setLayout(pitch_env_layout)
        
        self.pitch_env_velo = Slider("Velocity", -63, 63)
        self.pitch_env_velo.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.OSC_PENV_VELO, v + 64)
        )
        
        self.pitch_env_attack = Slider("Attack", 0, 127)
        self.pitch_env_attack.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.OSC_PENV_A, v)
        )
        
        self.pitch_env_decay = Slider("Decay", 0, 127)
        self.pitch_env_decay.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.OSC_PENV_D, v)
        )
        
        self.pitch_env_depth = Slider("Depth", -63, 63)
        self.pitch_env_depth.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.OSC_PENV_DEPTH, v + 64)
        )
        
        pitch_env_layout.addWidget(self.pitch_env_velo)
        pitch_env_layout.addWidget(self.pitch_env_attack)
        pitch_env_layout.addWidget(self.pitch_env_decay)
        pitch_env_layout.addWidget(self.pitch_env_depth)
        layout.addWidget(pitch_env_group)
        
        # Sub Oscillator
        sub_group = QGroupBox("Sub Oscillator")
        sub_layout = QVBoxLayout()
        sub_group.setLayout(sub_layout)
        
        self.sub_type = Switch("Type", ["OFF", "-1 OCT", "-2 OCT"])
        self.sub_type.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.SUB_TYPE, v)
        )
        sub_layout.addWidget(self.sub_type)
        layout.addWidget(sub_group)
        
        # Update PW controls enabled state based on current waveform
        self._update_pw_controls_state(Waveform.SAW)  # Initial state
        
        return group

    def _update_pw_controls_state(self, waveform):
        """Enable/disable PW controls based on waveform"""
        pw_enabled = (waveform == Waveform.PULSE)
        self.pw.setEnabled(pw_enabled)
        self.pw_mod.setEnabled(pw_enabled)

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
        group.setLayout(layout)
        
        # LFO Shape selector
        shape_row = QHBoxLayout()
        shape_row.addWidget(QLabel("Shape"))
        self.lfo_shape = QComboBox()
        self.lfo_shape.addItems(["TRI", "SIN", "SAW", "SQR", "S&H", "RND"])
        self.lfo_shape.currentIndexChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.LFO_SHAPE, v)
        )
        shape_row.addWidget(self.lfo_shape)
        layout.addLayout(shape_row)
        
        # Rate and Fade Time
        self.lfo_rate = Slider("Rate", 0, 127)
        self.lfo_rate.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.LFO_RATE, v)
        )
        
        self.lfo_fade = Slider("Fade Time", 0, 127)
        self.lfo_fade.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.LFO_FADE, v)
        )
        
        # Tempo Sync controls
        sync_row = QHBoxLayout()
        self.lfo_sync = Switch("Tempo Sync", ["OFF", "ON"])
        self.lfo_sync.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.LFO_SYNC, v)
        )
        sync_row.addWidget(self.lfo_sync)
        
        self.sync_note = QComboBox()
        self.sync_note.addItems([
            "16", "12", "8", "4", "2", "1", "3/4", "2/3", "1/2",
            "3/8", "1/3", "1/4", "3/16", "1/6", "1/8", "3/32",
            "1/12", "1/16", "1/24", "1/32"
        ])
        self.sync_note.currentIndexChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.LFO_SYNC_NOTE, v)
        )
        sync_row.addWidget(self.sync_note)
        
        # Depth controls
        self.lfo_pitch = Slider("Pitch Depth", -63, 63)
        self.lfo_pitch.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.LFO_PITCH, v + 64)
        )
        
        self.lfo_filter = Slider("Filter Depth", -63, 63)
        self.lfo_filter.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.LFO_FILTER, v + 64)
        )
        
        self.lfo_amp = Slider("Amp Depth", -63, 63)
        self.lfo_amp.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.LFO_AMP, v + 64)
        )
        
        # Key Trigger switch
        self.key_trig = Switch("Key Trigger", ["OFF", "ON"])
        self.key_trig.valueChanged.connect(
            lambda v: self._send_cc(AnalogToneCC.LFO_KEY_TRIG, v)
        )
        
        # Add all controls to layout
        layout.addWidget(self.lfo_rate)
        layout.addWidget(self.lfo_fade)
        layout.addLayout(sync_row)
        layout.addWidget(self.lfo_pitch)
        layout.addWidget(self.lfo_filter)
        layout.addWidget(self.lfo_amp)
        layout.addWidget(self.key_trig)
        
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