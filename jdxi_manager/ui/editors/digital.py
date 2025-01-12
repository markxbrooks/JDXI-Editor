from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QLineEdit, QPushButton,
    QScrollArea, QSlider, QCheckBox, QComboBox
)
from PySide6.QtCore import Qt
import logging
from typing import Optional

from jdxi_manager.midi import MIDIHelper
from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.midi.constants import (
    START_OF_SYSEX, END_OF_SYSEX,
    DIGITAL_SYNTH_1, DIGITAL_SYNTH_2,
    DigitalParameter
)
from jdxi_manager.midi.messages import JDXiSysEx
from jdxi_manager.ui.widgets import Slider


class DigitalSynthEditor(BaseEditor):
    """Digital synth patch editor window"""
    
    def __init__(self, synth_num: int, midi_helper: Optional[MIDIHelper] = None, parent: Optional[QWidget] = None):
        """Initialize digital synth editor
        
        Args:
            synth_num: Synth number (1 or 2)
            midi_helper: MIDI helper instance
            parent: Parent widget
        """
        super().__init__(midi_helper, parent)
        self.synth_num = synth_num
        self.setWindowTitle(f"Digital Synth {synth_num} Editor")
        
        # Set up area and part for parameter requests
        self.area = DIGITAL_SYNTH_1 if synth_num == 1 else DIGITAL_SYNTH_2
        self.part = 0x01  # Digital synth part
        self.group = 0x00  # Common group
        self.start_param = 0x00  # Start from first tone name character
        self.param_size = 0x0C  # Request 12 bytes for tone name
        
        # Create scroll area
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
        
        # Add sections
        layout.addWidget(self._create_tone_name_section())
        layout.addWidget(self._create_common_section())
        layout.addWidget(self._create_partial_switches_section())  # Add partial switches
        layout.addWidget(self._create_modify_section())  # Add modify parameters
        layout.addWidget(self._create_partial_osc_section())  # Add partial oscillator
        layout.addWidget(self._create_partial_filter_section())  # Add filter section
        layout.addWidget(self._create_partial_amp_section())  # Add amp section
        layout.addWidget(self._create_partial_lfo_section())  # Add LFO section
        layout.addWidget(self._create_partial_mod_lfo_section())  # Add mod LFO section
        
        # Set the widget to scroll area
        scroll.setWidget(central)
        
        # Request current patch data
        self._request_patch_data()
        
    def _create_tone_name_section(self) -> QFrame:
        """Create tone name editor section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(QLabel("Tone Name"))
        
        # Create tone name editor
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(12)  # Maximum 12 characters
        self.name_edit.textChanged.connect(self._handle_name_change)
        layout.addWidget(self.name_edit)
        
        return frame
        
    def _handle_name_change(self, text: str):
        """Handle tone name changes"""
        try:
            # Pad name to 12 characters
            name = text.ljust(12)
            
            # Send each character
            for i, char in enumerate(name):
                value = ord(char)
                if 32 <= value <= 127:  # Valid ASCII range
                    param = getattr(DigitalParameter, f'TONE_NAME_{i+1}').value
                    self._send_parameter(param, value)
                    
        except Exception as e:
            logging.error(f"Error handling tone name change: {str(e)}")
            
    def _send_parameter(self, param: int, value: int):
        """Send digital synth parameter change"""
        try:
            # Validate parameter value
            if not DigitalParameter.validate_value(param, value):
                logging.error(f"Parameter value {value} out of range for param {hex(param)}")
                return
                
            # Get correct area based on synth number
            area = DIGITAL_SYNTH_1 if self.synth_num == 1 else DIGITAL_SYNTH_2
            
            # Create and send message
            msg = JDXiSysEx.create_parameter_message(
                area=area,
                part=0x01,  # Digital synth part
                group=0x00,  # Common group
                param=param,
                value=value
            )
            
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                display_value = DigitalParameter.get_display_value(param, value)
                logging.debug(f"Sent digital parameter: {hex(param)}={display_value}")
                
        except Exception as e:
            logging.error(f"Error sending digital parameter: {str(e)}") 
        
    def _request_patch_data(self):
        """Request current patch data from synth"""
        try:
            # Get correct area based on synth number
            area = DIGITAL_SYNTH_1 if self.synth_num == 1 else DIGITAL_SYNTH_2
            
            # Request tone name parameters (0x00-0x0B)
            msg = JDXiSysEx.create_parameter_request(
                area=area,
                part=0x01,      # Digital synth part
                group=0x00,     # Common group
                param=0x00,     # Start from first tone name character
                size=0x0C       # Request 12 bytes for tone name
            )
            
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                logging.debug(f"Requested digital synth {self.synth_num} tone name data")
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
                data = msg[12:-2]  # Data bytes (excluding checksum and end of sysex)
                
                # Update UI based on received data
                self._update_ui_from_sysex(addr, data)
                logging.debug(f"Received patch data: addr={[hex(b) for b in addr]}, data={[hex(b) for b in data]}")
                
        except Exception as e:
            logging.error(f"Error handling MIDI input: {str(e)}")
            
    def _update_ui_from_sysex(self, addr, data):
        """Update UI controls based on received SysEx data"""
        try:
            group = addr[2]  # Third byte indicates parameter group
            param = addr[3]  # Fourth byte is parameter number
            value = data[0]  # First data byte is value
            
            # Update appropriate section based on group
            if group == 0x00:  # Common group
                if 0x00 <= param <= 0x0B:  # Tone name
                    # Convert data bytes to characters
                    name = ''.join(chr(b) for b in data if 32 <= b <= 127)
                    self.name_edit.setText(name)
                    logging.debug(f"Updated tone name: {name}")
                else:
                    # Other common parameters
                    self._update_common_controls(param, value)
                    
            elif group == 0x01:  # Modify group
                self._update_modify_controls(param, value)
                
            elif group == 0x20:  # Partial group
                if 0x00 <= param <= 0x09:  # Oscillator parameters
                    self._update_partial_osc_controls(param, value)
                elif 0x0A <= param <= 0x14:  # Filter parameters
                    self._update_partial_filter_controls(param, value)
                elif 0x15 <= param <= 0x1B:  # Amp parameters
                    self._update_partial_amp_controls(param, value)
                
            logging.debug(f"Updated UI from SysEx: group={hex(group)} param={hex(param)} value={value}")
            
        except Exception as e:
            logging.error(f"Error updating UI from SysEx: {str(e)}") 
        
    def _create_common_section(self) -> QFrame:
        """Create common parameters section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(QLabel("Common Parameters"))
        
        # Level control
        level = Slider("Level", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.TONE_LEVEL.value, v))
        level.setObjectName("tone_level_control")
        layout.addWidget(level)
        
        # Portamento controls
        porta_frame = QFrame()
        porta_layout = QHBoxLayout(porta_frame)
        
        porta_sw = QCheckBox("Portamento")
        porta_sw.setObjectName("portamento_sw_control")
        porta_sw.toggled.connect(
            lambda v: self._send_parameter(DigitalParameter.PORTAMENTO_SW.value, int(v)))
        porta_layout.addWidget(porta_sw)
        
        porta_time = Slider("Time", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.PORTAMENTO_TIME.value, v))
        porta_time.setObjectName("portamento_time_control")
        porta_layout.addWidget(porta_time)
        
        layout.addWidget(porta_frame)
        
        # Mono switch
        mono_sw = QCheckBox("Mono Mode")
        mono_sw.setObjectName("mono_sw_control")
        mono_sw.toggled.connect(
            lambda v: self._send_parameter(DigitalParameter.MONO_SW.value, int(v)))
        layout.addWidget(mono_sw)
        
        # Octave shift
        octave = Slider("Octave Shift", -3, 3,
            lambda v: self._send_parameter(DigitalParameter.OCTAVE_SHIFT.value, v + 64))
        octave.setObjectName("octave_shift_control")
        layout.addWidget(octave)
        
        # Pitch bend range
        bend_frame = QFrame()
        bend_layout = QHBoxLayout(bend_frame)
        
        bend_up = Slider("Bend Up", 0, 24,
            lambda v: self._send_parameter(DigitalParameter.BEND_RANGE_UP.value, v))
        bend_up.setObjectName("bend_range_up_control")
        bend_layout.addWidget(bend_up)
        
        bend_down = Slider("Bend Down", 0, 24,
            lambda v: self._send_parameter(DigitalParameter.BEND_RANGE_DOWN.value, v))
        bend_down.setObjectName("bend_range_down_control")
        bend_layout.addWidget(bend_down)
        
        layout.addWidget(bend_frame)
        
        # Ring switch
        ring_combo = QComboBox()
        ring_combo.setObjectName("ring_sw_control")
        ring_combo.addItems(['OFF', '---', 'ON'])
        ring_combo.currentIndexChanged.connect(
            lambda v: self._send_parameter(DigitalParameter.RING_SW.value, v))
        layout.addWidget(ring_combo)
        
        # Unison controls
        unison_frame = QFrame()
        unison_layout = QHBoxLayout(unison_frame)
        
        unison_sw = QCheckBox("Unison")
        unison_sw.setObjectName("unison_sw_control")
        unison_sw.toggled.connect(
            lambda v: self._send_parameter(DigitalParameter.UNISON_SW.value, int(v)))
        unison_layout.addWidget(unison_sw)
        
        unison_size = QComboBox()
        unison_size.setObjectName("unison_size_control")
        unison_size.addItems(['2', '4', '6', '8'])
        unison_size.currentIndexChanged.connect(
            lambda v: self._send_parameter(DigitalParameter.UNISON_SIZE.value, v))
        unison_layout.addWidget(unison_size)
        
        layout.addWidget(unison_frame)
        
        # Portamento mode and legato
        porta_mode_frame = QFrame()
        porta_mode_layout = QHBoxLayout(porta_mode_frame)
        
        porta_mode = QComboBox()
        porta_mode.setObjectName("portamento_mode_control")
        porta_mode.addItems(['NORMAL', 'LEGATO'])
        porta_mode.currentIndexChanged.connect(
            lambda v: self._send_parameter(DigitalParameter.PORTAMENTO_MODE.value, v))
        porta_mode_layout.addWidget(porta_mode)
        
        legato_sw = QCheckBox("Legato")
        legato_sw.setObjectName("legato_sw_control")
        legato_sw.toggled.connect(
            lambda v: self._send_parameter(DigitalParameter.LEGATO_SW.value, int(v)))
        porta_mode_layout.addWidget(legato_sw)
        
        layout.addWidget(porta_mode_frame)
        
        # Analog feel and wave shape
        analog_frame = QFrame()
        analog_layout = QHBoxLayout(analog_frame)
        
        analog_feel = Slider("Analog Feel", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.ANALOG_FEEL.value, v))
        analog_feel.setObjectName("analog_feel_control")
        analog_layout.addWidget(analog_feel)
        
        wave_shape = Slider("Wave Shape", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.WAVE_SHAPE_COMMON.value, v))
        wave_shape.setObjectName("wave_shape_control")
        analog_layout.addWidget(wave_shape)
        
        layout.addWidget(analog_frame)
        
        return frame
        
    def _update_common_controls(self, param: int, value: int):
        """Update common parameter controls"""
        try:
            control_map = {
                0x0C: "tone_level",
                0x12: "portamento_sw",
                0x13: "portamento_time", 
                0x14: "mono_sw",
                0x15: "octave_shift",
                0x16: "bend_range_up",
                0x17: "bend_range_down",
                0x1F: "ring_sw",
                0x2E: "unison_sw",
                0x31: "portamento_mode",
                0x32: "legato_sw",
                0x34: "analog_feel",
                0x35: "wave_shape",
                0x3C: "unison_size",
            }
            
            if param not in control_map:
                return
            
            control_name = control_map[param]
            control = self.findChild(QWidget, f"{control_name}_control")
            
            if not control:
                return
            
            if param in (0x2E, 0x32):  # Switches
                control.setChecked(bool(value))
            elif param in (0x31, 0x3C):  # Combo boxes
                control.setCurrentIndex(value)
            else:  # Direct values
                control.setValue(value)
            
            logging.debug(f"Updated common control {control_name}: {value}")
            
        except Exception as e:
            logging.error(f"Error updating common control: {str(e)}") 
        
    def _create_partial_switches_section(self) -> QFrame:
        """Create partial switches section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(QLabel("Partial Switches"))
        
        # Create switches for each partial
        for i in range(1, 4):  # Partials 1-3
            partial_frame = QFrame()
            partial_layout = QHBoxLayout(partial_frame)
            
            # Switch
            switch = QCheckBox(f"Partial {i}")
            switch.setObjectName(f"partial{i}_switch_control")
            switch.toggled.connect(
                lambda v, n=i: self._send_parameter(
                    getattr(DigitalParameter, f'PARTIAL{n}_SWITCH').value, 
                    int(v)
                )
            )
            partial_layout.addWidget(switch)
            
            # Select
            select = QCheckBox(f"Select {i}")
            select.setObjectName(f"partial{i}_select_control")
            select.toggled.connect(
                lambda v, n=i: self._send_parameter(
                    getattr(DigitalParameter, f'PARTIAL{n}_SELECT').value, 
                    int(v)
                )
            )
            partial_layout.addWidget(select)
            
            layout.addWidget(partial_frame)
        
        return frame
        
    def _update_partial_switches(self, param: int, value: int):
        """Update partial switch controls
        
        Args:
            param: Parameter number (0x19-0x1E)
            value: Parameter value
        """
        try:
            control_map = {
                0x19: "partial1_switch",
                0x1A: "partial1_select",
                0x1B: "partial2_switch",
                0x1C: "partial2_select",
                0x1D: "partial3_switch",
                0x1E: "partial3_select"
            }
            
            if param not in control_map:
                return
            
            control_name = control_map[param]
            control = self.findChild(QWidget, f"{control_name}_control")
            
            if control:
                control.setChecked(bool(value))
                logging.debug(f"Updated partial control {control_name}: {value}")
                
        except Exception as e:
            logging.error(f"Error updating partial switch: {str(e)}") 
        
    def _create_modify_section(self) -> QFrame:
        """Create modify parameters section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(QLabel("Modify Parameters"))
        
        # Time sensitivity controls
        sens_frame = QFrame()
        sens_layout = QHBoxLayout(sens_frame)
        
        # Attack time sensitivity
        attack_sens = Slider("Attack Time Sens", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.ATTACK_TIME_SENS.value, v))
        attack_sens.setObjectName("attack_time_sens_control")
        sens_layout.addWidget(attack_sens)
        
        # Release time sensitivity
        release_sens = Slider("Release Time Sens", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.RELEASE_TIME_SENS.value, v))
        release_sens.setObjectName("release_time_sens_control")
        sens_layout.addWidget(release_sens)
        
        # Portamento time sensitivity
        porta_sens = Slider("Porta Time Sens", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.PORTA_TIME_SENS.value, v))
        porta_sens.setObjectName("porta_time_sens_control")
        sens_layout.addWidget(porta_sens)
        
        layout.addWidget(sens_frame)
        
        # Envelope loop controls
        env_frame = QFrame()
        env_layout = QHBoxLayout(env_frame)
        
        # Loop mode
        loop_mode = QComboBox()
        loop_mode.setObjectName("env_loop_mode_control")
        loop_mode.addItems(['OFF', 'FREE-RUN', 'TEMPO-SYNC'])
        loop_mode.currentIndexChanged.connect(
            lambda v: self._send_parameter(DigitalParameter.ENV_LOOP_MODE.value, v))
        env_layout.addWidget(loop_mode)
        
        # Loop sync note
        loop_sync = QComboBox()
        loop_sync.setObjectName("env_loop_sync_control")
        loop_sync.addItems(['16', '12', '8', '4', '2', '1', '3/4', '2/3', '1/2',
                           '3/8', '1/3', '1/4', '3/16', '1/6', '1/8', '3/32',
                           '1/12', '1/16', '1/24', '1/32'])
        loop_sync.currentIndexChanged.connect(
            lambda v: self._send_parameter(DigitalParameter.ENV_LOOP_SYNC.value, v))
        env_layout.addWidget(loop_sync)
        
        layout.addWidget(env_frame)
        
        # Chromatic portamento
        chrom_porta = QCheckBox("Chromatic Portamento")
        chrom_porta.setObjectName("chrom_porta_control")
        chrom_porta.toggled.connect(
            lambda v: self._send_parameter(DigitalParameter.CHROM_PORTA.value, int(v)))
        layout.addWidget(chrom_porta)
        
        return frame
        
    def _update_modify_controls(self, param: int, value: int):
        """Update modify parameter controls"""
        try:
            control_map = {
                0x01: "attack_time_sens",
                0x02: "release_time_sens",
                0x03: "porta_time_sens",
                0x04: "env_loop_mode",
                0x05: "env_loop_sync",
                0x06: "chrom_porta"
            }
            
            if param not in control_map:
                return
            
            control_name = control_map[param]
            control = self.findChild(QWidget, f"{control_name}_control")
            
            if not control:
                return
            
            if param == 0x06:  # Chromatic portamento switch
                control.setChecked(bool(value))
            elif param in (0x04, 0x05):  # Combo boxes
                control.setCurrentIndex(value)
            else:  # Sliders
                control.setValue(value)
            
            logging.debug(f"Updated modify control {control_name}: {value}")
            
        except Exception as e:
            logging.error(f"Error updating modify control: {str(e)}") 
        
    def _create_partial_osc_section(self) -> QFrame:
        """Create partial oscillator section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(QLabel("Oscillator"))
        
        # Wave type and variation
        wave_frame = QFrame()
        wave_layout = QHBoxLayout(wave_frame)
        
        # Wave type selector
        wave_type = QComboBox()
        wave_type.setObjectName("osc_wave_control")
        wave_type.addItems(['SAW', 'SQR', 'PW-SQR', 'TRI', 'SINE', 'NOISE', 'SUPER-SAW', 'PCM'])
        wave_type.currentIndexChanged.connect(
            lambda v: self._send_parameter(DigitalParameter.OSC_WAVE.value, v))
        wave_layout.addWidget(wave_type)
        
        # Wave variation selector
        variation = QComboBox()
        variation.setObjectName("osc_variation_control")
        variation.addItems(['A', 'B', 'C'])
        variation.currentIndexChanged.connect(
            lambda v: self._send_parameter(DigitalParameter.OSC_VARIATION.value, v))
        wave_layout.addWidget(variation)
        
        layout.addWidget(wave_frame)
        
        # Pitch controls
        pitch_frame = QFrame()
        pitch_layout = QHBoxLayout(pitch_frame)
        
        # Coarse pitch
        pitch = Slider("Pitch", -24, 24,
            lambda v: self._send_parameter(DigitalParameter.OSC_PITCH.value, v + 64))
        pitch.setObjectName("osc_pitch_control")
        pitch_layout.addWidget(pitch)
        
        # Fine tune (detune)
        detune = Slider("Detune", -50, 50,
            lambda v: self._send_parameter(DigitalParameter.OSC_DETUNE.value, v + 64))
        detune.setObjectName("osc_detune_control")
        pitch_layout.addWidget(detune)
        
        layout.addWidget(pitch_frame)
        
        # Pulse width controls
        pw_frame = QFrame()
        pw_layout = QHBoxLayout(pw_frame)
        
        # Pulse width
        pw = Slider("PW", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.OSC_PW.value, v))
        pw.setObjectName("osc_pw_control")
        pw_layout.addWidget(pw)
        
        # PWM depth
        pwm = Slider("PWM", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.OSC_PWM_DEPTH.value, v))
        pwm.setObjectName("osc_pwm_depth_control")
        pw_layout.addWidget(pwm)
        
        layout.addWidget(pw_frame)
        
        # Pitch envelope controls
        env_frame = QFrame()
        env_layout = QHBoxLayout(env_frame)
        
        # Attack time
        attack = Slider("Attack", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.OSC_PITCH_ATK.value, v))
        attack.setObjectName("osc_pitch_atk_control")
        env_layout.addWidget(attack)
        
        # Decay time
        decay = Slider("Decay", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.OSC_PITCH_DEC.value, v))
        decay.setObjectName("osc_pitch_dec_control")
        env_layout.addWidget(decay)
        
        # Envelope depth
        depth = Slider("Depth", -63, 63,
            lambda v: self._send_parameter(DigitalParameter.OSC_PITCH_DEPTH.value, v + 64))
        depth.setObjectName("osc_pitch_depth_control")
        env_layout.addWidget(depth)
        
        layout.addWidget(env_frame)
        
        return frame
        
    def _update_partial_osc_controls(self, param: int, value: int):
        """Update partial oscillator controls"""
        try:
            control_map = {
                0x00: "osc_wave",
                0x01: "osc_variation",
                0x03: "osc_pitch",
                0x04: "osc_detune",
                0x05: "osc_pwm_depth",
                0x06: "osc_pw",
                0x07: "osc_pitch_atk",
                0x08: "osc_pitch_dec",
                0x09: "osc_pitch_depth"
            }
            
            if param not in control_map:
                return
            
            control_name = control_map[param]
            control = self.findChild(QWidget, f"{control_name}_control")
            
            if not control:
                return
            
            if param in (0x00, 0x01):  # Combo boxes
                control.setCurrentIndex(value)
            elif param in (0x03, 0x04, 0x09):  # Bipolar values
                control.setValue(value - 64)
            else:  # Direct values
                control.setValue(value)
            
            logging.debug(f"Updated oscillator control {control_name}: {value}")
            
        except Exception as e:
            logging.error(f"Error updating oscillator control: {str(e)}") 
        
    def _create_partial_filter_section(self) -> QFrame:
        """Create partial filter section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(QLabel("Filter"))
        
        # Filter type controls
        type_frame = QFrame()
        type_layout = QHBoxLayout(type_frame)
        
        # Filter mode
        mode = QComboBox()
        mode.setObjectName("filter_mode_control")
        mode.addItems(['BYPASS', 'LPF', 'HPF', 'BPF', 'PKG', 'LPF2', 'LPF3', 'LPF4'])
        mode.currentIndexChanged.connect(
            lambda v: self._send_parameter(DigitalParameter.FILTER_MODE.value, v))
        type_layout.addWidget(mode)
        
        # Filter slope
        slope = QComboBox()
        slope.setObjectName("filter_slope_control")
        slope.addItems(['-12dB', '-24dB'])
        slope.currentIndexChanged.connect(
            lambda v: self._send_parameter(DigitalParameter.FILTER_SLOPE.value, v))
        type_layout.addWidget(slope)
        
        layout.addWidget(type_frame)
        
        # Cutoff and resonance
        cutoff_frame = QFrame()
        cutoff_layout = QHBoxLayout(cutoff_frame)
        
        # Cutoff
        cutoff = Slider("Cutoff", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.FILTER_CUTOFF.value, v))
        cutoff.setObjectName("filter_cutoff_control")
        cutoff_layout.addWidget(cutoff)
        
        # Resonance
        resonance = Slider("Resonance", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.FILTER_RESONANCE.value, v))
        resonance.setObjectName("filter_resonance_control")
        cutoff_layout.addWidget(resonance)
        
        layout.addWidget(cutoff_frame)
        
        # Keyfollow and velocity
        mod_frame = QFrame()
        mod_layout = QHBoxLayout(mod_frame)
        
        # Keyfollow
        keyfollow = Slider("Keyfollow", -100, 100,
            lambda v: self._send_parameter(DigitalParameter.FILTER_KEYFOLLOW.value, int(v * 20/200 + 54)))
        keyfollow.setObjectName("filter_keyfollow_control")
        mod_layout.addWidget(keyfollow)
        
        # Envelope velocity
        env_velo = Slider("Env Velo", -63, 63,
            lambda v: self._send_parameter(DigitalParameter.FILTER_ENV_VELO.value, v + 64))
        env_velo.setObjectName("filter_env_velo_control")
        mod_layout.addWidget(env_velo)
        
        layout.addWidget(mod_frame)
        
        # Filter envelope
        env_frame = QFrame()
        env_layout = QHBoxLayout(env_frame)
        
        # ADSR controls
        for name, param in [
            ("Attack", DigitalParameter.FILTER_ENV_ATK),
            ("Decay", DigitalParameter.FILTER_ENV_DEC),
            ("Sustain", DigitalParameter.FILTER_ENV_SUS),
            ("Release", DigitalParameter.FILTER_ENV_REL)
        ]:
            slider = Slider(name, 0, 127,
                lambda v, p=param: self._send_parameter(p.value, v))
            slider.setObjectName(f"filter_env_{name.lower()}_control")
            env_layout.addWidget(slider)
        
        layout.addWidget(env_frame)
        
        # Envelope depth
        depth = Slider("Env Depth", -63, 63,
            lambda v: self._send_parameter(DigitalParameter.FILTER_ENV_DEPTH.value, v + 64))
        depth.setObjectName("filter_env_depth_control")
        layout.addWidget(depth)
        
        return frame
        
    def _update_partial_filter_controls(self, param: int, value: int):
        """Update partial filter controls"""
        try:
            control_map = {
                0x0A: "filter_mode",
                0x0B: "filter_slope",
                0x0C: "filter_cutoff",
                0x0D: "filter_keyfollow",
                0x0E: "filter_env_velo",
                0x0F: "filter_resonance",
                0x10: "filter_env_attack",
                0x11: "filter_env_decay",
                0x12: "filter_env_sustain",
                0x13: "filter_env_release",
                0x14: "filter_env_depth"
            }
            
            if param not in control_map:
                return
            
            control_name = control_map[param]
            control = self.findChild(QWidget, f"{control_name}_control")
            
            if not control:
                return
            
            if param in (0x0A, 0x0B):  # Combo boxes
                control.setCurrentIndex(value)
            elif param == 0x0D:  # Keyfollow
                control.setValue(((value - 54) * 200 / 20) - 100)  # Convert to -100/+100
            elif param in (0x0E, 0x14):  # Bipolar values
                control.setValue(value - 64)  # Convert to -63/+63
            else:  # Direct values
                control.setValue(value)
            
            logging.debug(f"Updated filter control {control_name}: {value}")
            
        except Exception as e:
            logging.error(f"Error updating filter control: {str(e)}") 
        
    def _create_partial_amp_section(self) -> QFrame:
        """Create partial amplifier section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(QLabel("Amplifier"))
        
        # Level and velocity
        level_frame = QFrame()
        level_layout = QHBoxLayout(level_frame)
        
        # Level
        level = Slider("Level", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.AMP_LEVEL.value, v))
        level.setObjectName("amp_level_control")
        level_layout.addWidget(level)
        
        # Velocity sensitivity
        velo = Slider("Velocity", -63, 63,
            lambda v: self._send_parameter(DigitalParameter.AMP_VELO_SENS.value, v + 64))
        velo.setObjectName("amp_velo_sens_control")
        level_layout.addWidget(velo)
        
        layout.addWidget(level_frame)
        
        # ADSR envelope
        env_frame = QFrame()
        env_layout = QHBoxLayout(env_frame)
        
        # ADSR controls
        for name, param in [
            ("Attack", DigitalParameter.AMP_ENV_ATK),
            ("Decay", DigitalParameter.AMP_ENV_DEC),
            ("Sustain", DigitalParameter.AMP_ENV_SUS),
            ("Release", DigitalParameter.AMP_ENV_REL)
        ]:
            slider = Slider(name, 0, 127,
                lambda v, p=param: self._send_parameter(p.value, v))
            slider.setObjectName(f"amp_env_{name.lower()}_control")
            env_layout.addWidget(slider)
        
        layout.addWidget(env_frame)
        
        # Pan
        pan = Slider("Pan", -64, 63,
            lambda v: self._send_parameter(DigitalParameter.AMP_PAN.value, v + 64))
        pan.setObjectName("amp_pan_control")
        layout.addWidget(pan)
        
        return frame
        
    def _update_partial_amp_controls(self, param: int, value: int):
        """Update partial amplifier controls"""
        try:
            control_map = {
                0x15: "amp_level",
                0x16: "amp_velo_sens",
                0x17: "amp_env_attack",
                0x18: "amp_env_decay",
                0x19: "amp_env_sustain",
                0x1A: "amp_env_release",
                0x1B: "amp_pan"
            }
            
            if param not in control_map:
                return
            
            control_name = control_map[param]
            control = self.findChild(QWidget, f"{control_name}_control")
            
            if not control:
                return
            
            if param == 0x16:  # Velocity sens (-63 to +63)
                control.setValue(value - 64)
            elif param == 0x1B:  # Pan (L64-63R)
                control.setValue(value - 64)
            else:  # Direct values
                control.setValue(value)
            
            logging.debug(f"Updated amp control {control_name}: {value}")
            
        except Exception as e:
            logging.error(f"Error updating amp control: {str(e)}") 
        
    def _create_partial_lfo_section(self) -> QFrame:
        """Create partial LFO section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(QLabel("LFO"))
        
        # Shape and rate
        shape_frame = QFrame()
        shape_layout = QHBoxLayout(shape_frame)
        
        # Shape selector
        shape = QComboBox()
        shape.setObjectName("lfo_shape_control")
        shape.addItems(['TRI', 'SIN', 'SAW', 'SQR', 'S&H', 'RND'])
        shape.currentIndexChanged.connect(
            lambda v: self._send_parameter(DigitalParameter.LFO_SHAPE.value, v))
        shape_layout.addWidget(shape)
        
        # Rate
        rate = Slider("Rate", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.LFO_RATE.value, v))
        rate.setObjectName("lfo_rate_control")
        shape_layout.addWidget(rate)
        
        layout.addWidget(shape_frame)
        
        # Sync controls
        sync_frame = QFrame()
        sync_layout = QHBoxLayout(sync_frame)
        
        # Sync switch
        sync_sw = QCheckBox("Tempo Sync")
        sync_sw.setObjectName("lfo_sync_sw_control")
        sync_sw.toggled.connect(
            lambda v: self._send_parameter(DigitalParameter.LFO_SYNC_SW.value, int(v)))
        sync_layout.addWidget(sync_sw)
        
        # Sync note
        sync_note = QComboBox()
        sync_note.setObjectName("lfo_sync_note_control")
        sync_note.addItems(['16', '12', '8', '4', '2', '1', '3/4', '2/3', '1/2',
                           '3/8', '1/3', '1/4', '3/16', '1/6', '1/8', '3/32',
                           '1/12', '1/16', '1/24', '1/32'])
        sync_note.currentIndexChanged.connect(
            lambda v: self._send_parameter(DigitalParameter.LFO_SYNC_NOTE.value, v))
        sync_layout.addWidget(sync_note)
        
        layout.addWidget(sync_frame)
        
        # Fade and key trigger
        fade_frame = QFrame()
        fade_layout = QHBoxLayout(fade_frame)
        
        # Fade time
        fade = Slider("Fade Time", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.LFO_FADE.value, v))
        fade.setObjectName("lfo_fade_control")
        fade_layout.addWidget(fade)
        
        # Key trigger
        key_trig = QCheckBox("Key Trigger")
        key_trig.setObjectName("lfo_key_trig_control")
        key_trig.toggled.connect(
            lambda v: self._send_parameter(DigitalParameter.LFO_KEY_TRIG.value, int(v)))
        fade_layout.addWidget(key_trig)
        
        layout.addWidget(fade_frame)
        
        # Depth controls
        depth_frame = QFrame()
        depth_layout = QHBoxLayout(depth_frame)
        
        # Create depth sliders
        for name, param in [
            ("Pitch", DigitalParameter.LFO_PITCH_DEPTH),
            ("Filter", DigitalParameter.LFO_FILTER_DEPTH),
            ("Amp", DigitalParameter.LFO_AMP_DEPTH),
            ("Pan", DigitalParameter.LFO_PAN_DEPTH)
        ]:
            slider = Slider(f"{name} Depth", -63, 63,
                lambda v, p=param: self._send_parameter(p.value, v + 64))
            slider.setObjectName(f"lfo_{name.lower()}_depth_control")
            depth_layout.addWidget(slider)
        
        layout.addWidget(depth_frame)
        
        return frame
        
    def _update_partial_lfo_controls(self, param: int, value: int):
        """Update partial LFO controls"""
        try:
            control_map = {
                0x1C: "lfo_shape",
                0x1D: "lfo_rate",
                0x1E: "lfo_sync_sw",
                0x1F: "lfo_sync_note",
                0x20: "lfo_fade",
                0x21: "lfo_key_trig",
                0x22: "lfo_pitch_depth",
                0x23: "lfo_filter_depth",
                0x24: "lfo_amp_depth",
                0x25: "lfo_pan_depth"
            }
            
            if param not in control_map:
                return
            
            control_name = control_map[param]
            control = self.findChild(QWidget, f"{control_name}_control")
            
            if not control:
                return
            
            if param in (0x1C, 0x1F):  # Combo boxes
                control.setCurrentIndex(value)
            elif param in (0x1E, 0x21):  # Switches
                control.setChecked(bool(value))
            elif param in (0x22, 0x23, 0x24, 0x25):  # Depth controls
                control.setValue(value - 64)  # Convert to -63/+63
            else:  # Direct values
                control.setValue(value)
            
            logging.debug(f"Updated LFO control {control_name}: {value}")
            
        except Exception as e:
            logging.error(f"Error updating LFO control: {str(e)}") 
        
    def _create_partial_mod_lfo_section(self) -> QFrame:
        """Create partial modulation LFO section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(QLabel("Modulation LFO"))
        
        # Shape and rate
        shape_frame = QFrame()
        shape_layout = QHBoxLayout(shape_frame)
        
        # Shape selector
        shape = QComboBox()
        shape.setObjectName("mod_lfo_shape_control")
        shape.addItems(['TRI', 'SIN', 'SAW', 'SQR', 'S&H', 'RND'])
        shape.currentIndexChanged.connect(
            lambda v: self._send_parameter(DigitalParameter.MOD_LFO_SHAPE.value, v))
        shape_layout.addWidget(shape)
        
        # Rate
        rate = Slider("Rate", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.MOD_LFO_RATE.value, v))
        rate.setObjectName("mod_lfo_rate_control")
        shape_layout.addWidget(rate)
        
        layout.addWidget(shape_frame)
        
        # Sync controls
        sync_frame = QFrame()
        sync_layout = QHBoxLayout(sync_frame)
        
        # Sync switch
        sync_sw = QCheckBox("Tempo Sync")
        sync_sw.setObjectName("mod_lfo_sync_sw_control")
        sync_sw.toggled.connect(
            lambda v: self._send_parameter(DigitalParameter.MOD_LFO_SYNC_SW.value, int(v)))
        sync_layout.addWidget(sync_sw)
        
        # Sync note
        sync_note = QComboBox()
        sync_note.setObjectName("mod_lfo_sync_note_control")
        sync_note.addItems(['16', '12', '8', '4', '2', '1', '3/4', '2/3', '1/2',
                           '3/8', '1/3', '1/4', '3/16', '1/6', '1/8', '3/32',
                           '1/12', '1/16', '1/24', '1/32'])
        sync_note.currentIndexChanged.connect(
            lambda v: self._send_parameter(DigitalParameter.MOD_LFO_SYNC_NOTE.value, v))
        sync_layout.addWidget(sync_note)
        
        layout.addWidget(sync_frame)
        
        # PW shift
        pw_shift = Slider("PW Shift", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.OSC_PW_SHIFT.value, v))
        pw_shift.setObjectName("osc_pw_shift_control")
        layout.addWidget(pw_shift)
        
        # Depth controls
        depth_frame = QFrame()
        depth_layout = QHBoxLayout(depth_frame)
        
        # Create depth sliders
        for name, param in [
            ("Pitch", DigitalParameter.MOD_LFO_PITCH),
            ("Filter", DigitalParameter.MOD_LFO_FILTER),
            ("Amp", DigitalParameter.MOD_LFO_AMP),
            ("Pan", DigitalParameter.MOD_LFO_PAN)
        ]:
            slider = Slider(f"{name} Depth", -63, 63,
                lambda v, p=param: self._send_parameter(p.value, v + 64))
            slider.setObjectName(f"mod_lfo_{name.lower()}_depth_control")
            depth_layout.addWidget(slider)
        
        layout.addWidget(depth_frame)
        
        return frame
        
    def _update_partial_mod_lfo_controls(self, param: int, value: int):
        """Update partial modulation LFO controls"""
        try:
            control_map = {
                0x26: "mod_lfo_shape",
                0x27: "mod_lfo_rate",
                0x28: "mod_lfo_sync_sw",
                0x29: "mod_lfo_sync_note",
                0x2A: "osc_pw_shift",
                0x2C: "mod_lfo_pitch_depth",
                0x2D: "mod_lfo_filter_depth",
                0x2E: "mod_lfo_amp_depth",
                0x2F: "mod_lfo_pan_depth"
            }
            
            if param not in control_map:
                return
            
            control_name = control_map[param]
            control = self.findChild(QWidget, f"{control_name}_control")
            
            if not control:
                return
            
            if param in (0x26, 0x29):  # Combo boxes
                control.setCurrentIndex(value)
            elif param == 0x28:  # Switch
                control.setChecked(bool(value))
            elif param in (0x2C, 0x2D, 0x2E, 0x2F):  # Depth controls
                control.setValue(value - 64)  # Convert to -63/+63
            else:  # Direct values
                control.setValue(value)
            
            logging.debug(f"Updated mod LFO control {control_name}: {value}")
            
        except Exception as e:
            logging.error(f"Error updating mod LFO control: {str(e)}") 