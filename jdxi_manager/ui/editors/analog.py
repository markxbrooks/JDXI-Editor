from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QFrame, QLabel, QPushButton, QComboBox, QScrollArea
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPalette, QColor
import logging

from ...data import AN
from ...midi import MIDIHelper, MIDIConnection
from ..style import Style
from ..widgets import Slider, WaveformButton
from ..widgets.preset_panel import PresetPanel

class AnalogSynthEditor(QMainWindow):
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.main_window = parent
        
        # Set window properties
        self.setStyleSheet(Style.DARK_THEME)
        self.setFixedWidth(1000)
        self.setMinimumHeight(600)
        
        # Create UI and set up bindings
        self._create_ui()
        self._setup_parameter_bindings()
        
        # Request initial patch data
        QTimer.singleShot(100, self._request_patch_data)
        
    def _create_separator(self):
        """Create a red separator line"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(2)
        separator.setStyleSheet(f"""
            QFrame {{
                background-color: {Style.RED};
                margin: 10px 0px;
            }}
        """)
        return separator

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
        
        # Create all sections
        common = self._create_common_section()  # Create common section first
        osc = self._create_oscillator_section()
        vcf = self._create_filter_section()
        amp = self._create_amplifier_section()
        mod = self._create_modulation_section()
        
        # Add sections to layout with spacing and separators
        layout.addWidget(common)  # Add common section
        layout.addWidget(self._create_separator())
        layout.addWidget(osc)
        layout.addWidget(self._create_separator())
        layout.addWidget(vcf)
        layout.addWidget(self._create_separator())
        layout.addWidget(amp)
        layout.addWidget(self._create_separator())
        layout.addWidget(mod)
        
        # Add stretch at the bottom
        layout.addStretch()
        
        # Set the widget to scroll area
        scroll.setWidget(central)
        
    def _create_section_header(self, title, color):
        """Create a colored header for a section"""
        header = QFrame()
        header.setFixedHeight(30)
        header.setAutoFillBackground(True)
        
        palette = header.palette()
        palette.setColor(QPalette.Window, QColor(color))
        header.setPalette(palette)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 0, 10, 0)
        
        label = QLabel(title)
        label.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        layout.addWidget(label)
        
        return header
        
    def _create_oscillator_section(self):
        """Create oscillator section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        
        # Create OSC 1 controls
        osc1_group = QFrame()
        osc1_layout = QVBoxLayout(osc1_group)
        osc1_layout.setSpacing(10)
        
        osc1_label = QLabel("OSC 1")
        osc1_label.setStyleSheet("font-weight: bold;")
        
        self.osc1_wave = WaveformButton()  # Create new WaveformButton instance
        self.osc1_range = Slider("Range", -24, 24)
        self.osc1_fine = Slider("Fine Tune", -50, 50)
        
        osc1_layout.addWidget(osc1_label)
        osc1_layout.addWidget(self.osc1_wave)
        osc1_layout.addWidget(self.osc1_range)
        osc1_layout.addWidget(self.osc1_fine)
        
        # Create OSC 2 controls
        osc2_group = QFrame()
        osc2_layout = QVBoxLayout(osc2_group)
        osc2_layout.setSpacing(10)
        
        osc2_label = QLabel("OSC 2")
        osc2_label.setStyleSheet("font-weight: bold;")
        
        self.osc2_wave = WaveformButton()  # Create new WaveformButton instance
        self.osc2_range = Slider("Range", -24, 24)
        self.osc2_fine = Slider("Fine Tune", -50, 50)
        self.osc2_sync = QPushButton("Sync")
        self.osc2_sync.setCheckable(True)
        
        osc2_layout.addWidget(osc2_label)
        osc2_layout.addWidget(self.osc2_wave)
        osc2_layout.addWidget(self.osc2_range)
        osc2_layout.addWidget(self.osc2_fine)
        osc2_layout.addWidget(self.osc2_sync)
        
        # Create mix controls
        mix_group = QFrame()
        mix_layout = QVBoxLayout(mix_group)
        mix_layout.setSpacing(10)
        
        mix_label = QLabel("MIX")
        mix_label.setStyleSheet("font-weight: bold;")
        
        self.osc_mix = Slider("OSC Mix", 0, 127)
        self.cross_mod = Slider("Cross Mod", 0, 127)
        
        mix_layout.addWidget(mix_label)
        mix_layout.addWidget(self.osc_mix)
        mix_layout.addWidget(self.cross_mod)
        
        # Add all groups to main layout
        layout.addWidget(osc1_group)
        layout.addWidget(osc2_group)
        layout.addWidget(mix_group)
        
        return section
        
    def _create_filter_section(self):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # Add header
        layout.addWidget(self._create_section_header("Filter", Style.VCF_BG))
        layout.addSpacing(10)
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # Filter parameters
        params_frame = QFrame()
        params_frame.setFrameStyle(QFrame.StyledPanel)
        params_layout = QVBoxLayout(params_frame)
        
        self.cutoff = Slider("Cutoff", 0, 127)
        self.resonance = Slider("Resonance", 0, 127)
        self.key_follow = Slider("Key Follow", -100, 100, center=True)
        
        params_layout.addWidget(self.cutoff)
        params_layout.addWidget(self.resonance)
        params_layout.addWidget(self.key_follow)
        controls.addWidget(params_frame)
        
        # Filter envelope
        env_frame = QFrame()
        env_frame.setFrameStyle(QFrame.StyledPanel)
        env_layout = QVBoxLayout(env_frame)
        env_layout.addWidget(QLabel("Envelope"))
        
        self.filter_attack = Slider("Attack", 0, 127)
        self.filter_decay = Slider("Decay", 0, 127)
        self.filter_sustain = Slider("Sustain", 0, 127)
        self.filter_release = Slider("Release", 0, 127)
        self.env_depth = Slider("Env Depth", -63, 63, center=True)
        
        env_layout.addWidget(self.filter_attack)
        env_layout.addWidget(self.filter_decay)
        env_layout.addWidget(self.filter_sustain)
        env_layout.addWidget(self.filter_release)
        env_layout.addWidget(self.env_depth)
        controls.addWidget(env_frame)
        
        layout.addLayout(controls)
        return frame

    def _create_amplifier_section(self):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # Add header
        layout.addWidget(self._create_section_header("Amplifier", Style.AMP_BG))
        layout.addSpacing(10)
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # Level controls
        level_frame = QFrame()
        level_frame.setFrameStyle(QFrame.StyledPanel)
        level_layout = QVBoxLayout(level_frame)
        level_layout.addWidget(QLabel("Level"))
        
        self.amp_level = Slider("Level", 0, 127)
        self.velocity_sens = Slider("Velocity Sens", -63, 63, center=True)
        
        level_layout.addWidget(self.amp_level)
        level_layout.addWidget(self.velocity_sens)
        controls.addWidget(level_frame)
        
        # Amp envelope
        env_frame = QFrame()
        env_frame.setFrameStyle(QFrame.StyledPanel)
        env_layout = QVBoxLayout(env_frame)
        env_layout.addWidget(QLabel("Envelope"))
        
        self.amp_attack = Slider("Attack", 0, 127)
        self.amp_decay = Slider("Decay", 0, 127)
        self.amp_sustain = Slider("Sustain", 0, 127)
        self.amp_release = Slider("Release", 0, 127)
        
        env_layout.addWidget(self.amp_attack)
        env_layout.addWidget(self.amp_decay)
        env_layout.addWidget(self.amp_sustain)
        env_layout.addWidget(self.amp_release)
        controls.addWidget(env_frame)
        
        layout.addLayout(controls)
        return frame
        
    def _create_modulation_section(self):
        """Create modulation section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        
        # Create LFO controls
        lfo_group = QFrame()
        lfo_layout = QVBoxLayout(lfo_group)
        lfo_layout.setSpacing(10)
        
        lfo_label = QLabel("LFO")
        lfo_label.setStyleSheet("font-weight: bold;")
        
        self.lfo_wave = WaveformButton()
        self.lfo_rate = Slider("Rate", 0, 127)
        self.lfo_fade = Slider("Fade Time", 0, 127)
        
        # Add LFO depth controls
        self.lfo_pitch = Slider("Pitch Depth", 0, 127)
        self.lfo_filter = Slider("Filter Depth", 0, 127)
        self.lfo_amp = Slider("Amp Depth", 0, 127)
        
        # Add modulation matrix controls
        self.mod_source = QComboBox()
        self.mod_source.addItems(["LFO", "Velocity", "Key Follow", "Mod Wheel"])
        
        self.mod_dest = QComboBox()
        self.mod_dest.addItems(["Pitch", "Filter", "Amp", "LFO Rate"])
        
        self.mod_depth = Slider("Mod Depth", -63, 63, center=True)
        
        # Add all controls to layout
        lfo_layout.addWidget(lfo_label)
        lfo_layout.addWidget(self.lfo_wave)
        lfo_layout.addWidget(self.lfo_rate)
        lfo_layout.addWidget(self.lfo_fade)
        
        # Add depth controls
        depths_label = QLabel("LFO Depths")
        depths_label.setStyleSheet("font-weight: bold;")
        lfo_layout.addWidget(depths_label)
        lfo_layout.addWidget(self.lfo_pitch)
        lfo_layout.addWidget(self.lfo_filter)
        lfo_layout.addWidget(self.lfo_amp)
        
        # Add modulation matrix
        matrix_label = QLabel("Modulation Matrix")
        matrix_label.setStyleSheet("font-weight: bold;")
        lfo_layout.addWidget(matrix_label)
        lfo_layout.addWidget(QLabel("Source:"))
        lfo_layout.addWidget(self.mod_source)
        lfo_layout.addWidget(QLabel("Destination:"))
        lfo_layout.addWidget(self.mod_dest)
        lfo_layout.addWidget(self.mod_depth)
        
        # Add all groups to main layout
        layout.addWidget(lfo_group)
        
        return section

    def _setup_parameter_bindings(self):
        """Set up MIDI parameter bindings for all controls"""
        try:
            # Common parameters
            self.volume.valueChanged.connect(
                lambda v: self._send_parameter(0x01, v))  # Volume
            self.pan.valueChanged.connect(
                lambda v: self._send_parameter(0x02, v + 64))  # Pan (center at 64)
            self.portamento.valueChanged.connect(
                lambda v: self._send_parameter(0x03, v))  # Portamento Time
            self.porta_mode.toggled.connect(
                lambda v: self._send_parameter(0x04, 1 if v else 0))  # Portamento Mode
            
            # OSC 1 parameters
            self.osc1_wave.waveformChanged.connect(
                lambda v: self._send_parameter(0x10, v))  # Wave Type
            self.osc1_range.valueChanged.connect(
                lambda v: self._send_parameter(0x11, v + 64))  # Range
            self.osc1_fine.valueChanged.connect(
                lambda v: self._send_parameter(0x12, v + 64))  # Fine Tune
            
            # OSC 2 parameters (0x20)
            self.osc2_wave.waveformChanged.connect(
                lambda v: self._send_parameter(0x20, v))  # Wave Type
            self.osc2_range.valueChanged.connect(
                lambda v: self._send_parameter(0x21, v + 64))  # Range
            self.osc2_fine.valueChanged.connect(
                lambda v: self._send_parameter(0x22, v + 64))  # Fine Tune
            self.osc2_sync.toggled.connect(
                lambda v: self._send_parameter(0x23, 1 if v else 0))  # Sync
            
            # Mix parameters (0x30)
            self.osc_mix.valueChanged.connect(
                lambda v: self._send_parameter(0x30, v))  # OSC Mix
            self.cross_mod.valueChanged.connect(
                lambda v: self._send_parameter(0x31, v))  # Cross Mod
            
            # Filter parameters (0x40)
            self.cutoff.valueChanged.connect(
                lambda v: self._send_parameter(0x40, v))  # Cutoff
            self.resonance.valueChanged.connect(
                lambda v: self._send_parameter(0x41, v))  # Resonance
            self.key_follow.valueChanged.connect(
                lambda v: self._send_parameter(0x42, v + 64))  # Key Follow
            
            # Filter Envelope
            self.filter_attack.valueChanged.connect(
                lambda v: self._send_parameter(0x43, v))  # Attack
            self.filter_decay.valueChanged.connect(
                lambda v: self._send_parameter(0x44, v))  # Decay
            self.filter_sustain.valueChanged.connect(
                lambda v: self._send_parameter(0x45, v))  # Sustain
            self.filter_release.valueChanged.connect(
                lambda v: self._send_parameter(0x46, v))  # Release
            self.env_depth.valueChanged.connect(
                lambda v: self._send_parameter(0x47, v + 64))  # Env Depth
            
            # LFO parameters
            self.lfo_wave.waveformChanged.connect(
                lambda v: self._send_parameter(0x50, v))  # LFO Wave
            self.lfo_rate.valueChanged.connect(
                lambda v: self._send_parameter(0x51, v))  # LFO Rate
            self.lfo_fade.valueChanged.connect(
                lambda v: self._send_parameter(0x52, v))  # LFO Fade Time
            
            # LFO Depths
            self.lfo_pitch.valueChanged.connect(
                lambda v: self._send_parameter(0x66, v))  # Pitch Depth
            self.lfo_filter.valueChanged.connect(
                lambda v: self._send_parameter(0x67, v))  # Filter Depth
            self.lfo_amp.valueChanged.connect(
                lambda v: self._send_parameter(0x68, v))  # Amp Depth
            
            # Modulation Matrix
            self.mod_source.currentIndexChanged.connect(
                lambda v: self._send_parameter(0x70, v))  # Mod Source
            self.mod_dest.currentIndexChanged.connect(
                lambda v: self._send_parameter(0x71, v))  # Mod Destination
            self.mod_depth.valueChanged.connect(
                lambda v: self._send_parameter(0x72, v + 64))  # Mod Depth
            
        except Exception as e:
            logging.error(f"Error setting up parameter bindings: {str(e)}")
            
    def _send_parameter(self, parameter, value):
        """Send parameter change to JD-Xi"""
        try:
            msg = MIDIHelper.create_parameter_message(
                0x17,        # Analog synth address
                0x00,        # No part number needed
                parameter,   # Parameter number
                value       # Parameter value (0-127)
            )
            if self.main_window and self.main_window.midi_out:
                self.main_window.midi_out.send_message(msg)
                if hasattr(self.main_window, 'midi_out_indicator'):
                    self.main_window.midi_out_indicator.blink()
                logging.debug(f"Sent MIDI message: {' '.join([hex(b)[2:].upper().zfill(2) for b in msg])}")
            
        except Exception as e:
            logging.error(f"Error sending parameter: {str(e)}")
            
    def _request_patch_data(self):
        """Request current patch data from JD-Xi"""
        try:
            msg = MIDIHelper.create_sysex_message(
                bytes([0x17, 0x00, 0x00, 0x00]),  # Analog synth address
                bytes([0x00])  # Data
            )
            if self.main_window and self.main_window.midi_out:
                self.main_window.midi_out.send_message(msg)
                if hasattr(self.main_window, 'midi_out_indicator'):
                    self.main_window.midi_out_indicator.blink()
            
        except Exception as e:
            logging.error(f"Error requesting patch data: {str(e)}")
            
    def set_midi_ports(self, midi_in, midi_out):
        """Update MIDI port connections"""
        self.midi_in = midi_in
        self.midi_out = midi_out
        
        if midi_in:
            midi_in.set_callback(self._handle_midi_input) 

    def _handle_midi_input(self, message, timestamp):
        """Handle incoming MIDI messages"""
        data = message[0]  # Get the raw MIDI data
        
        # Check if it's a SysEx message
        if data[0] == 0xF0 and len(data) > 8:
            # Verify it's a Roland message for JD-Xi
            if (data[1] == 0x41 and  # Roland ID
                data[4:8] == bytes([0x00, 0x00, 0x00, 0x0E])):  # JD-Xi ID
                
                # Get address and parameter data
                addr = data[8:12]  # 4-byte address
                param_data = data[12:-1]  # Parameter data (excluding F7)
                
                # Queue UI update on main thread
                QTimer.singleShot(0, lambda: self._update_ui_from_sysex(addr, param_data))

    def _update_ui_from_sysex(self, addr, data):
        """Update UI controls based on received SysEx data"""
        # Check if it's for analog synth (0x17)
        if addr[0] != 0x17:
            return
            
        section = addr[2]  # Section address
        param = addr[3]    # Parameter number
        value = data[0]    # Parameter value
        
        try:
            # Common parameters (0x00)
            if section == 0x00:
                if param == 0x01:
                    self.volume.setValue(value)
                elif param == 0x02:
                    self.pan.setValue(value - 64)  # Convert 0-127 to -64-+63
                elif param == 0x03:
                    self.portamento.setValue(value)
                elif param == 0x04:
                    self.porta_mode.setChecked(bool(value))
                    
            # OSC 1 parameters (0x10)
            elif section == 0x10:
                if param == 0x00:
                    self.osc1_wave.setCurrentIndex(value)
                elif param == 0x01:
                    self.osc1_range.setValue(value - 64)  # Convert 0-127 to -64-+63
                elif param == 0x02:
                    self.osc1_fine.setValue(value - 64)  # Convert 0-127 to -64-+63
                    
            # OSC 2 parameters (0x20)
            elif section == 0x20:
                if param == 0x00:
                    self.osc2_wave.setCurrentIndex(value)
                elif param == 0x01:
                    self.osc2_range.setValue(value - 64)  # Convert 0-127 to -64-+63
                elif param == 0x02:
                    self.osc2_fine.setValue(value - 64)  # Convert 0-127 to -64-+63
                elif param == 0x03:
                    self.osc2_sync.setChecked(bool(value))
                    
            # Mix parameters (0x30)
            elif section == 0x30:
                if param == 0x00:
                    self.osc_mix.setValue(value)
                elif param == 0x01:
                    self.cross_mod.setValue(value)
                    
            # Filter parameters (0x40)
            elif section == 0x40:
                if param == 0x00:
                    self.cutoff.setValue(value)
                elif param == 0x01:
                    self.resonance.setValue(value)
                elif param == 0x02:
                    self.key_follow.setValue(value - 64)  # Convert 0-127 to -64-+63
                elif param == 0x03:
                    self.filter_attack.setValue(value)
                elif param == 0x04:
                    self.filter_decay.setValue(value)
                elif param == 0x05:
                    self.filter_sustain.setValue(value)
                elif param == 0x06:
                    self.filter_release.setValue(value)
                elif param == 0x07:
                    self.env_depth.setValue(value - 64)  # Convert 0-127 to -64-+63
                    
            # Amp parameters (0x50)
            elif section == 0x50:
                if param == 0x00:
                    self.amp_level.setValue(value)
                elif param == 0x01:
                    self.velocity_sens.setValue(value - 64)  # Convert 0-127 to -64-+63
                elif param == 0x02:
                    self.amp_attack.setValue(value)
                elif param == 0x03:
                    self.amp_decay.setValue(value)
                elif param == 0x04:
                    self.amp_sustain.setValue(value)
                elif param == 0x05:
                    self.amp_release.setValue(value)
                    
            # LFO parameters (0x60)
            elif section == 0x60:
                if param == 0x00:
                    self.lfo_wave.setCurrentIndex(value)
                elif param == 0x01:
                    self.lfo_sync.setChecked(bool(value))
                elif param == 0x02:
                    self.lfo_rate.setValue(value)
                elif param == 0x03:
                    self.lfo_note.setCurrentIndex(value)
                elif param == 0x04:
                    self.lfo_key_trigger.setChecked(bool(value))
                elif param == 0x05:
                    self.lfo_fade.setValue(value)
                elif param == 0x06:
                    self.lfo_pitch.setValue(value)
                elif param == 0x07:
                    self.lfo_filter.setValue(value)
                elif param == 0x08:
                    self.lfo_amp.setValue(value)
                    
            # Modulation Matrix (0x70)
            elif section == 0x70:
                if param == 0x00:
                    self.mod_source.setCurrentIndex(value)
                elif param == 0x01:
                    self.mod_dest.setCurrentIndex(value)
                elif param == 0x02:
                    self.mod_depth.setValue(value - 64)  # Convert 0-127 to -64-+63
                    
            logging.debug(f"Updated analog synth parameter - Section: {hex(section)}, Param: {hex(param)}, Value: {value}")
            
        except Exception as e:
            logging.error(f"Error updating UI from SysEx: {str(e)}") 

    def get_parameters(self):
        """Get current parameter values"""
        return {
            # Common parameters
            'volume': self.volume.value(),
            'pan': self.pan.value(),
            'portamento': self.portamento.value(),
            'porta_mode': self.porta_mode.isChecked(),
            
            # OSC 1
            'osc1_wave': self.osc1_wave.value(),
            'osc1_range': self.osc1_range.value(),
            'osc1_fine': self.osc1_fine.value(),
            
            # OSC 2
            'osc2_wave': self.osc2_wave.value(),
            'osc2_range': self.osc2_range.value(),
            'osc2_fine': self.osc2_fine.value(),
            'osc2_sync': self.osc2_sync.isChecked(),
            
            # Mix
            'osc_mix': self.osc_mix.value(),
            'cross_mod': self.cross_mod.value(),
            
            # Filter
            'cutoff': self.cutoff.value(),
            'resonance': self.resonance.value(),
            'key_follow': self.key_follow.value(),
            'filter_attack': self.filter_attack.value(),
            'filter_decay': self.filter_decay.value(),
            'filter_sustain': self.filter_sustain.value(),
            'filter_release': self.filter_release.value(),
            
            # Amp
            'amp_attack': self.amp_attack.value(),
            'amp_decay': self.amp_decay.value(),
            'amp_sustain': self.amp_sustain.value(),
            'amp_release': self.amp_release.value(),
            
            # LFO
            'lfo_wave': self.lfo_wave.value(),
            'lfo_rate': self.lfo_rate.value(),
            'lfo_fade': self.lfo_fade.value(),
            
            # Modulation
            'mod_source': self.mod_source.currentIndex(),
            'mod_dest': self.mod_dest.currentIndex(),
            'mod_depth': self.mod_depth.value()
        }
    
    def set_parameters(self, parameters):
        """Set parameters from preset"""
        # Common parameters
        self.volume.setValue(parameters['volume'])
        self.pan.setValue(parameters['pan'])
        self.portamento.setValue(parameters['portamento'])
        self.porta_mode.setChecked(parameters['porta_mode'])
        
        # OSC 1
        self.osc1_wave.setValue(parameters['osc1_wave'])
        self.osc1_range.setValue(parameters['osc1_range'])
        self.osc1_fine.setValue(parameters['osc1_fine'])
        
        # OSC 2
        self.osc2_wave.setValue(parameters['osc2_wave'])
        self.osc2_range.setValue(parameters['osc2_range'])
        self.osc2_fine.setValue(parameters['osc2_fine'])
        self.osc2_sync.setChecked(parameters['osc2_sync'])
        
        # Mix
        self.osc_mix.setValue(parameters['osc_mix'])
        self.cross_mod.setValue(parameters['cross_mod'])
        
        # Filter
        self.cutoff.setValue(parameters['cutoff'])
        self.resonance.setValue(parameters['resonance'])
        self.key_follow.setValue(parameters['key_follow'])
        self.filter_attack.setValue(parameters['filter_attack'])
        self.filter_decay.setValue(parameters['filter_decay'])
        self.filter_sustain.setValue(parameters['filter_sustain'])
        self.filter_release.setValue(parameters['filter_release'])
        
        # Amp
        self.amp_attack.setValue(parameters['amp_attack'])
        self.amp_decay.setValue(parameters['amp_decay'])
        self.amp_sustain.setValue(parameters['amp_sustain'])
        self.amp_release.setValue(parameters['amp_release'])
        
        # LFO
        self.lfo_wave.setValue(parameters['lfo_wave'])
        self.lfo_rate.setValue(parameters['lfo_rate'])
        self.lfo_fade.setValue(parameters['lfo_fade'])
        
        # Modulation
        self.mod_source.setCurrentIndex(parameters['mod_source'])
        self.mod_dest.setCurrentIndex(parameters['mod_dest'])
        self.mod_depth.setValue(parameters['mod_depth']) 

    def _create_common_section(self):
        """Create common parameters section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        
        # Create controls
        self.volume = Slider("Volume", 0, 127)
        self.pan = Slider("Pan", -64, 63)
        self.portamento = Slider("Portamento", 0, 127)
        self.porta_mode = QPushButton("Porta Mode")
        self.porta_mode.setCheckable(True)
        
        # Add to layout
        layout.addWidget(self.volume)
        layout.addWidget(self.pan)
        layout.addWidget(self.portamento)
        layout.addWidget(self.porta_mode)
        
        return section 

    def _handle_preset_load(self, preset_num, preset_name):
        """Handle preset being loaded"""
        try:
            # Update main window display
            self._update_main_window_preset(preset_num, preset_name)
            
            # Request patch data
            self._request_patch_data()
            
            logging.debug(f"Loaded Analog Synth preset {preset_num}: {preset_name}")
            
        except Exception as e:
            logging.error(f"Error handling preset load: {str(e)}") 