from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QComboBox, QCheckBox, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
import logging

from jdxi_manager.data.analog import (
    AnalogSynthPatch, AnalogParameter,
    AnalogOscillator, AnalogMixer, AnalogFilter,
    AnalogAmplifier, AnalogLFO, AnalogEnvelope
)
from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets import Slider, WaveformButton
from jdxi_manager.ui.widgets.preset_panel import PresetPanel
from jdxi_manager.midi.constants import (
    START_OF_SYSEX, ROLAND_ID, DEVICE_ID, MODEL_ID_1, MODEL_ID_2,
    MODEL_ID, JD_XI_ID, DT1_COMMAND_12, END_OF_SYSEX,
    ANALOG_SYNTH_AREA, SUBGROUP_ZERO, Waveform
)
from jdxi_manager.midi.messages import (
    create_parameter_message,
    create_sysex_message,
    create_patch_load_message,
    create_patch_save_message
)

class AnalogSynthEditor(QMainWindow):
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.main_window = parent
        self.current_patch = AnalogSynthPatch()
        
        # Set window properties
        self.setStyleSheet(Style.MAIN_STYLESHEET)
        self.setFixedWidth(1000)
        self.setMinimumHeight(600)
        
        # Create UI
        self._create_ui()
        
        # Request current patch data
        self._request_patch_data()

    def _create_section_header(self, text: str, bg_color: str) -> QLabel:
        """Create a section header label
        
        Args:
            text: Header text
            bg_color: Background color from Style class
            
        Returns:
            QLabel with styled header
        """
        header = QLabel(text)
        header.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: white;
                padding: 5px;
                font-weight: bold;
                border-radius: 4px;
            }}
        """)
        return header

    def _create_oscillator_section(self, osc_num: int):
        """Create oscillator section controls"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header(f"OSC {osc_num}", Style.OSC_BG))
        
        # Create controls
        param_base = AnalogParameter.OSC1_WAVE if osc_num == 1 else AnalogParameter.OSC2_WAVE
        
        # Waveform selector
        wave_selector = WaveformButton()
        wave_selector.waveform_changed.connect(
            lambda w: self._send_parameter(param_base.value, w.value)
        )
        
        # Range control (-24 to +24 semitones)
        range_slider = Slider(
            "Range", -24, 24,
            lambda v: self._send_parameter(param_base.value + 1, v + 64)
        )
        
        # Fine tune control (-50 to +50 cents)
        fine_slider = Slider(
            "Fine", -50, 50,
            lambda v: self._send_parameter(param_base.value + 2, v + 64)
        )
        
        # Detune control
        detune_slider = Slider(
            "Detune", 0, 127,
            lambda v: self._send_parameter(param_base.value + 3, v)
        )
        
        # Add controls to layout
        layout.addWidget(wave_selector)
        layout.addWidget(range_slider)
        layout.addWidget(fine_slider)
        layout.addWidget(detune_slider)
        
        # Add OSC2 sync if this is OSC2
        if osc_num == 2:
            sync_check = QCheckBox("Sync")
            sync_check.toggled.connect(
                lambda v: self._send_parameter(AnalogParameter.OSC2_SYNC.value, int(v))
            )
            layout.addWidget(sync_check)
        
        return frame

    def _create_mixer_section(self):
        """Create mixer section controls"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header("MIXER", Style.MIX_BG))
        
        # Create controls
        balance = Slider(
            "OSC Balance", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.OSC_BALANCE.value, v)
        )
        noise = Slider(
            "Noise Level", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.NOISE_LEVEL.value, v)
        )
        ring_mod = Slider(
            "Ring Mod", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.RING_MOD.value, v)
        )
        cross_mod = Slider(
            "Cross Mod", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.CROSS_MOD.value, v)
        )
        
        # Add controls to layout
        layout.addWidget(balance)
        layout.addWidget(noise)
        layout.addWidget(ring_mod)
        layout.addWidget(cross_mod)
        
        return frame

    def _send_parameter(self, parameter: int, value: int):
        """Send parameter change to JD-Xi"""
        try:
            msg = [
                START_OF_SYSEX, ROLAND_ID, DEVICE_ID, MODEL_ID_1, MODEL_ID_2,
                MODEL_ID, JD_XI_ID, DT1_COMMAND_12,
                ANALOG_SYNTH_AREA, SUBGROUP_ZERO,
                parameter, SUBGROUP_ZERO,
                value
            ]
            
            # Calculate checksum
            checksum = 0
            for byte in msg[8:]:
                checksum = (checksum + byte) & 0x7F
            checksum = (128 - checksum) & 0x7F
            
            msg.extend([checksum, END_OF_SYSEX])
            
            if self.midi_helper:
                self.midi_helper.send_message(bytes(msg))
                
        except Exception as e:
            logging.error(f"Error sending parameter: {str(e)}")

    def _update_ui_from_patch(self):
        """Update UI controls from current patch data"""
        try:
            # Update OSC1 controls
            self.osc1_wave.setWaveform(self.current_patch.osc1.wave)
            self.osc1_range.setValue(self.current_patch.osc1.range)
            self.osc1_fine.setValue(self.current_patch.osc1.fine)
            self.osc1_detune.setValue(self.current_patch.osc1.detune)
            
            # Update OSC2 controls
            self.osc2_wave.setWaveform(self.current_patch.osc2.wave)
            self.osc2_range.setValue(self.current_patch.osc2.range)
            self.osc2_fine.setValue(self.current_patch.osc2.fine)
            self.osc2_detune.setValue(self.current_patch.osc2.detune)
            self.osc2_sync.setChecked(self.current_patch.osc2.sync)
            
            # Update mixer controls
            self.mix_balance.setValue(self.current_patch.mixer.osc_balance)
            self.mix_noise.setValue(self.current_patch.mixer.noise_level)
            self.mix_ring.setValue(self.current_patch.mixer.ring_mod)
            self.mix_cross.setValue(self.current_patch.mixer.cross_mod)
            
            # Continue updating other sections...
            
        except Exception as e:
            logging.error(f"Error updating UI from patch: {str(e)}") 

    def _create_filter_section(self):
        """Create filter section controls"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header("FILTER", Style.VCF_BG))
        
        # Create controls
        cutoff = Slider(
            "Cutoff", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.CUTOFF.value, v)
        )
        resonance = Slider(
            "Resonance", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.RESONANCE.value, v)
        )
        key_follow = Slider(
            "Key Follow", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.KEY_FOLLOW.value, v)
        )
        env_depth = Slider(
            "Env Depth", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.ENV_DEPTH.value, v)
        )
        lfo_depth = Slider(
            "LFO Depth", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.LFO_DEPTH.value, v)
        )
        velocity = Slider(
            "Velocity", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.VELOCITY_SENS.value, v)
        )
        
        # Add controls to layout
        layout.addWidget(cutoff)
        layout.addWidget(resonance)
        layout.addWidget(key_follow)
        layout.addWidget(env_depth)
        layout.addWidget(lfo_depth)
        layout.addWidget(velocity)
        
        return frame

    def _create_amp_section(self):
        """Create amplifier section controls"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header("AMP", Style.VCA_BG))
        
        # Create controls
        level = Slider(
            "Level", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.LEVEL.value, v)
        )
        pan = Slider(
            "Pan", -64, 63,
            lambda v: self._send_parameter(AnalogParameter.PAN.value, v + 64)
        )
        portamento = Slider(
            "Portamento", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.PORTAMENTO.value, v)
        )
        legato = QCheckBox("Legato")
        legato.toggled.connect(
            lambda v: self._send_parameter(AnalogParameter.LEGATO.value, int(v))
        )
        
        # Add controls to layout
        layout.addWidget(level)
        layout.addWidget(pan)
        layout.addWidget(portamento)
        layout.addWidget(legato)
        
        return frame

    def _create_lfo_section(self):
        """Create LFO section controls"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header("LFO", Style.LFO_BG))
        
        # Create controls
        wave = WaveformButton()
        wave.waveform_changed.connect(
            lambda w: self._send_parameter(AnalogParameter.LFO_WAVE.value, w.value)
        )
        
        rate = Slider(
            "Rate", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.LFO_RATE.value, v)
        )
        
        sync = QCheckBox("Sync")
        sync.toggled.connect(
            lambda v: self._send_parameter(AnalogParameter.LFO_SYNC.value, int(v))
        )
        
        fade = Slider(
            "Fade Time", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.LFO_FADE.value, v)
        )
        
        delay = Slider(
            "Delay Time", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.LFO_DELAY.value, v)
        )
        
        # Add controls to layout
        layout.addWidget(wave)
        layout.addWidget(rate)
        layout.addWidget(sync)
        layout.addWidget(fade)
        layout.addWidget(delay)
        
        return frame

    def _create_envelope_section(self, env_type: str):
        """Create envelope section controls"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header with appropriate background color
        bg_color = {
            "PITCH": Style.PITCH_ENV_BG,
            "FILTER": Style.VCF_ENV_BG,
            "AMP": Style.VCA_ENV_BG
        }[env_type]
        layout.addWidget(self._create_section_header(f"{env_type} ENV", bg_color))
        
        # Create ADSR controls
        attack = Slider(
            "Attack", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.ENV_ATTACK.value, v)
        )
        decay = Slider(
            "Decay", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.ENV_DECAY.value, v)
        )
        sustain = Slider(
            "Sustain", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.ENV_SUSTAIN.value, v)
        )
        release = Slider(
            "Release", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.ENV_RELEASE.value, v)
        )
        
        # Add controls to layout
        layout.addWidget(attack)
        layout.addWidget(decay)
        layout.addWidget(sustain)
        layout.addWidget(release)
        
        return frame

    def _create_ui(self):
        """Create the complete user interface"""
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
        
        # Add preset panel at the top
        self.preset_panel = PresetPanel('analog', self)
        layout.addWidget(self.preset_panel)
        
        # Create sections container
        sections = QVBoxLayout()
        sections.setSpacing(20)
        
        # Add all sections vertically
        # Oscillators
        sections.addWidget(self._create_oscillator_section(1))
        sections.addWidget(self._create_oscillator_section(2))
        
        # Mixer
        sections.addWidget(self._create_mixer_section())
        
        # Filter
        sections.addWidget(self._create_filter_section())
        
        # Amplifier
        sections.addWidget(self._create_amp_section())
        
        # LFO
        sections.addWidget(self._create_lfo_section())
        
        # Envelopes
        sections.addWidget(self._create_envelope_section("PITCH"))
        sections.addWidget(self._create_envelope_section("FILTER"))
        sections.addWidget(self._create_envelope_section("AMP"))
        
        # Add sections to main layout
        layout.addLayout(sections)
        
        # Add stretch at the bottom
        layout.addStretch()
        
        # Set the widget to scroll area
        scroll.setWidget(central)

    def _request_patch_data(self):
        """Request current patch data from device"""
        try:
            logging.debug("Requesting Analog Synth patch data")
            
            # Calculate base address for analog synth
            base_addr = [
                ANALOG_SYNTH_AREA,  # Analog synth area
                SUBGROUP_ZERO,      # Part number (always 0 for analog)
                0x00,               # Start at first parameter
                0x00                # Parameter offset
            ]
            
            # Request common parameters
            common_msg = create_sysex_message(
                bytes(base_addr),
                bytes([0x20])  # Request 32 bytes of common parameters
            )
            
            # Request oscillator parameters
            osc_addr = base_addr.copy()
            osc_addr[2] = AnalogParameter.OSC1_WAVE.value
            osc_msg = create_sysex_message(
                bytes(osc_addr),
                bytes([0x40])  # Request 64 bytes of oscillator parameters
            )
            
            # Request filter parameters
            filter_addr = base_addr.copy()
            filter_addr[2] = AnalogParameter.CUTOFF.value
            filter_msg = create_sysex_message(
                bytes(filter_addr),
                bytes([0x20])  # Request 32 bytes of filter parameters
            )
            
            # Request amp parameters
            amp_addr = base_addr.copy()
            amp_addr[2] = AnalogParameter.LEVEL.value
            amp_msg = create_sysex_message(
                bytes(amp_addr),
                bytes([0x20])  # Request 32 bytes of amp parameters
            )
            
            # Request LFO parameters
            lfo_addr = base_addr.copy()
            lfo_addr[2] = AnalogParameter.LFO_WAVE.value
            lfo_msg = create_sysex_message(
                bytes(lfo_addr),
                bytes([0x20])  # Request 32 bytes of LFO parameters
            )
            
            # Send all requests if MIDI is available
            if self.midi_helper:
                # Send requests with slight delays between
                self.midi_helper.send_message(common_msg)
                logging.debug("Sent common parameters request")
                
                self.midi_helper.send_message(osc_msg)
                logging.debug("Sent oscillator parameters request")
                
                self.midi_helper.send_message(filter_msg)
                logging.debug("Sent filter parameters request")
                
                self.midi_helper.send_message(amp_msg)
                logging.debug("Sent amp parameters request")
                
                self.midi_helper.send_message(lfo_msg)
                logging.debug("Sent LFO parameters request")
                
            else:
                logging.warning("No MIDI helper available - cannot request patch data")
                
        except Exception as e:
            logging.error(f"Error requesting patch data: {str(e)}")

    def _handle_midi_input(self, msg):
        """Handle incoming MIDI messages"""
        try:
            # Check if it's a SysEx message
            if msg[0] == START_OF_SYSEX and msg[-1] == END_OF_SYSEX:
                # Extract address and data
                addr = msg[8:12]  # 4 bytes of address
                data = msg[12:-1]  # Data bytes (excluding end of sysex)
                
                # Update UI based on received data
                self._update_ui_from_sysex(addr, data)
                
        except Exception as e:
            logging.error(f"Error handling MIDI input: {str(e)}")

    def _update_ui_from_sysex(self, addr, data):
        """Update UI controls based on received SysEx data"""
        try:
            # Extract section from address
            section = addr[2]  # Third byte indicates parameter section
            
            # Update appropriate controls based on section
            if section == AnalogParameter.OSC1_WAVE.value:
                # Update oscillator controls
                self._update_oscillator_controls(data)
                
            elif section == AnalogParameter.CUTOFF.value:
                # Update filter controls
                self._update_filter_controls(data)
                
            elif section == AnalogParameter.LEVEL.value:
                # Update amp controls
                self._update_amp_controls(data)
                
            elif section == AnalogParameter.LFO_WAVE.value:
                # Update LFO controls
                self._update_lfo_controls(data)
                
        except Exception as e:
            logging.error(f"Error updating UI from SysEx: {str(e)}") 