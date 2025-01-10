from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QComboBox, QCheckBox, QPushButton,
    QFileDialog, QMessageBox, QScrollArea, QProgressDialog,
    QGroupBox, QTabWidget
)
from PySide6.QtCore import Qt, QMetaObject, Q_ARG
from PySide6.QtGui import QIcon
import logging

from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets import Slider, WaveformButton
from jdxi_manager.ui.widgets.preset_panel import PresetPanel
from jdxi_manager.midi import MIDIHelper
from jdxi_manager.midi.messages import (
    create_parameter_message,
    create_patch_load_message,
    create_patch_save_message,
    create_sysex_message
)
from jdxi_manager.midi.constants import (
    START_OF_SYSEX, ROLAND_ID, DEVICE_ID, MODEL_ID_1, MODEL_ID_2,
    MODEL_ID, JD_XI_ID, DT1_COMMAND_12, END_OF_SYSEX,
    DIGITAL_SYNTH_AREA, PART_1, OSC_PARAM_GROUP,
    LFO_PARAM_GROUP, SUBGROUP_ZERO, Waveform,
    DigitalPartial
)
from jdxi_manager.ui.editors.base_editor import BaseEditor


class DigitalSynthEditor(BaseEditor):
    def __init__(self, synth_num=1, midi_helper=None, parent=None):
        """Initialize digital synth editor
        
        Args:
            synth_num: Digital synth number (1 or 2)
            midi_helper: MIDI helper instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.synth_num = synth_num
        self.midi_helper = midi_helper
        self.main_window = parent
        
        # Set window properties
        self.setStyleSheet(Style.MAIN_STYLESHEET)
        self.setFixedWidth(1000)
        self.setMinimumHeight(600)
        
        # Create UI and set up bindings
        self._create_ui()
        self._setup_parameter_bindings()
        
        # Request patch data immediately
        self._request_patch_data()

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
        self.preset_panel = PresetPanel(f'digital{self.synth_num}', self)
        layout.addWidget(self.preset_panel)
        
        # Create partial structure controls
        structure = self._create_structure_section()
        layout.addWidget(structure)
        
        # Create tab widget for partials
        tabs = QTabWidget()
        
        # Add tabs for each partial
        for i in range(3):
            partial = self._create_partial_tab(i + 1)
            tabs.addTab(partial, f"Partial {i + 1}")
        
        layout.addWidget(tabs)
        
        # Add common controls at the bottom
        common = self._create_common_section()
        layout.addWidget(common)
        
        # Set the widget to scroll area
        scroll.setWidget(central)

    def _create_separator(self):
        """Create a separator line"""
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

    def _create_oscillator_section(self):
        """Create oscillator section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        
        # OSC 1
        osc1_group = QGroupBox("OSC 1")
        osc1_layout = QVBoxLayout(osc1_group)
        
        self.osc1_wave = WaveformButton("Waveform")
        self.osc1_range = Slider("Range", -24, 24)
        self.osc1_fine = Slider("Fine Tune", -50, 50)
        
        osc1_layout.addWidget(self.osc1_wave)
        osc1_layout.addWidget(self.osc1_range)
        osc1_layout.addWidget(self.osc1_fine)
        
        # OSC 2
        osc2_group = QGroupBox("OSC 2")
        osc2_layout = QVBoxLayout(osc2_group)
        
        self.osc2_wave = WaveformButton("Waveform")
        self.osc2_range = Slider("Range", -24, 24)
        self.osc2_fine = Slider("Fine Tune", -50, 50)
        
        osc2_layout.addWidget(self.osc2_wave)
        osc2_layout.addWidget(self.osc2_range)
        osc2_layout.addWidget(self.osc2_fine)
        
        # Add groups to main layout
        layout.addWidget(osc1_group)
        layout.addWidget(osc2_group)
        
        return section

    def _create_filter_section(self, partial_num, offset):
        """Create filter controls for a partial"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        header = QLabel(f"Filter {partial_num}")
        header.setStyleSheet(f"background-color: {Style.VCF_BG}; color: white; padding: 5px;")
        layout.addWidget(header)
        
        # Create filter type selector
        filter_type = QComboBox()
        filter_type.addItems([
            "Low Pass", "High Pass", "Band Pass", "Peaking", "Off"
        ])
        filter_type.currentIndexChanged.connect(
            lambda v: self._update_parameter(partial_num, 'FILTER_TYPE', v + offset)
        )
        layout.addWidget(filter_type)
        
        # Create sliders
        cutoff = Slider(
            "Cutoff", 0, 127,
            lambda v: self._update_parameter(partial_num, 'FILTER_CUTOFF', v + offset)
        )
        resonance = Slider(
            "Resonance", 0, 127,
            lambda v: self._update_parameter(partial_num, 'FILTER_RESO', v + offset)
        )
        env_depth = Slider(
            "Env Depth", -64, 63,
            lambda v: self._update_parameter(partial_num, 'FILTER_ENV', v + offset)
        )
        key_follow = Slider(
            "Key Follow", 0, 127,
            lambda v: self._update_parameter(partial_num, 'FILTER_KEY', v + offset)
        )
        
        layout.addWidget(cutoff)
        layout.addWidget(resonance)
        layout.addWidget(env_depth)
        layout.addWidget(key_follow)
        
        return frame

    def _create_amplifier_section(self, partial_num, offset):
        """Create amplifier controls for a partial"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        header = QLabel(f"Amplifier {partial_num}")
        header.setStyleSheet(f"background-color: {Style.VCA_BG}; color: white; padding: 5px;")
        layout.addWidget(header)
        
        # Create sliders
        level = Slider(
            "Level", 0, 127,
            lambda v: self._update_parameter(partial_num, 'AMP_LEVEL', v + offset)
        )
        pan = Slider(
            "Pan", -64, 63,
            lambda v: self._update_parameter(partial_num, 'AMP_PAN', v + offset)
        )
        
        layout.addWidget(level)
        layout.addWidget(pan)
        
        return frame

    def _create_modulation_section(self):
        """Create modulation section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        
        # LFO parameters
        lfo_group = QGroupBox("LFO")
        lfo_layout = QVBoxLayout(lfo_group)
        
        self.lfo_wave = WaveformButton("Waveform")
        self.lfo_rate = Slider("Rate", 0, 127)
        self.lfo_depth = Slider("Depth", 0, 127)
        
        lfo_layout.addWidget(self.lfo_wave)
        lfo_layout.addWidget(self.lfo_rate)
        lfo_layout.addWidget(self.lfo_depth)
        
        # Add group to main layout
        layout.addWidget(lfo_group)
        
        return section

    def _setup_parameter_bindings(self):
        """Set up parameter bindings for all controls"""
        try:
            logging.debug("Setting up parameter bindings")
            
            # Structure controls bindings are already set in _create_structure_section
            
            # Common section bindings
            self.volume.valueChanged.connect(
                lambda v: self._send_parameter(0x00, v))  # Volume
            self.pan.valueChanged.connect(
                lambda v: self._send_parameter(0x01, v + 64))  # Pan
            self.portamento.valueChanged.connect(
                lambda v: self._send_parameter(0x02, v))  # Portamento
            self.porta_mode.clicked.connect(
                lambda checked: self._send_parameter(0x03, 127 if checked else 0))  # Porta Mode
            
            # Partial bindings are handled in their respective _update_parameter calls
            
            logging.debug("Parameter bindings completed")
            
        except Exception as e:
            logging.error(f"Error setting up parameter bindings: {str(e)}")
            raise

    def _send_parameter(self, param_num: int, value: int):
        """Send a parameter change message"""
        try:
            msg = create_parameter_message(
                DIGITAL_SYNTH_AREA,
                self.synth_num,  # Use synth number for proper routing
                param_num,
                value
            )
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                
        except Exception as e:
            logging.error(f"Error sending parameter {param_num}: {str(e)}")

    def set_midi_ports(self, midi_in, midi_out):
        """Update MIDI port connections"""
        self.midi_in = midi_in
        self.midi_out = midi_out
        
        # Set main window reference for indicators
        if hasattr(self, 'main_window'):
            if midi_in:
                midi_in.main_window = self.main_window
            if midi_out:
                midi_out.main_window = self.main_window
        
        if midi_in:
            midi_in.set_callback(self._handle_midi_input)
            logging.debug(f"Set MIDI input callback for Digital Synth {self.synth_num}")

    def _handle_midi_input(self, message, timestamp):
        """Handle incoming MIDI messages"""
        try:
            # Get the raw MIDI data
            data = message[0] if isinstance(message, tuple) else message
            
            # Set MIDI indicator active
            if self.main_window and hasattr(self.main_window, 'midi_in_indicator'):
                self.main_window.midi_in_indicator.set_active()
            
            # Check if it's a SysEx message
            if data[0] == 0xF0 and len(data) > 8:
                # Verify it's a Roland message for JD-Xi
                if (data[1] == 0x41 and  # Roland ID
                    data[4:8] == bytes([0x00, 0x00, 0x00, 0x0E])):  # JD-Xi ID
                    
                    # Get address and parameter data
                    addr = data[8:12]  # 4-byte address
                    param_data = data[12:-1]  # Parameter data (excluding F7)
                    
                    # Update UI directly
                    self._update_ui_from_sysex(addr, param_data)
                    
            # Check for program change messages
            elif len(data) >= 2 and data[0] & 0xF0 == 0xC0:  # Program Change
                self._handle_program_change(data[1])
                
            # Set MIDI indicator inactive after processing
            if self.main_window and hasattr(self.main_window, 'midi_in_indicator'):
                self.main_window.midi_in_indicator.set_inactive()
            
        except Exception as e:
            logging.error(f"Error handling MIDI input: {str(e)}")

    def _validate_sysex_message(self, message):
        """Validate incoming SysEx message"""
        try:
            # Check message format
            if len(message) < 8:
                return False
            
            # Check if it's a Roland SysEx message
            if message[0] != 0xF0 or message[1] != 0x41:
                return False
            
            # Check if it's for the digital synth
            if message[7] != 0x19:
                return False
            
            # Check if it's for this part number
            if message[8] != self.synth_num:
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Error validating SysEx message: {str(e)}")
            return False

    def _handle_preset_load(self, preset_num, preset_name):
        """Handle preset being loaded"""
        try:
            # Update main window display
            self._update_main_window_preset(preset_num, preset_name)
            
            # Request patch data
            self._request_patch_data()
            
            logging.debug(f"Loaded Digital Synth preset {preset_num}: {preset_name}")
            
        except Exception as e:
            logging.error(f"Error handling preset load: {str(e)}")

    def _handle_program_change(self, program_number):
        """Handle program change from device"""
        try:
            preset_num = program_number + 1  # Convert 0-based to 1-based
            # Request patch name from device
            self._request_patch_name(preset_num)
            logging.debug(f"Received program change: {preset_num}")
            
        except Exception as e:
            logging.error(f"Error handling program change: {str(e)}")

    def _request_patch_name(self, preset_num):
        """Request patch name from device"""
        try:
            # Calculate address for patch name
            base_addr = 0x19  # Digital synth memory
            patch_offset = (preset_num - 1) * 0x20  # Each patch is 32 bytes
            name_addr = [base_addr, patch_offset & 0x7F, (patch_offset >> 7) & 0x7F, 0x00]
            
            msg = create_sysex_message(
                bytes(name_addr),  # Address for patch name
                bytes([0x0C])  # Request 12 bytes (name length)
            )
            
            if self.main_window and self.main_window.midi_out:
                self.main_window.midi_out.send_message(msg)
                logging.debug(f"Requested name for preset {preset_num}")
                
        except Exception as e:
            logging.error(f"Error requesting patch name: {str(e)}")

    def _update_ui_from_sysex(self, addr: bytes, data: bytes):
        """Update UI controls based on received SysEx data"""
        # Check if it's for this synth (0x19)
        if addr[0] != 0x19 or addr[1] != self.synth_num:
            return
            
        section = addr[2]  # Section address
        param = addr[3]    # Parameter number
        value = data[0]    # Parameter value
        
        try:
            # Update the appropriate control based on section/parameter
            self._update_control(section, param, value)
            
        except Exception as e:
            logging.error(f"Error updating UI from SysEx: {str(e)}")

    def _update_control(self, section: int, param: int, value: int):
        """Update a specific control based on section and parameter numbers"""
        try:
            # Common parameters
            if section == 0x00:
                if param == 0x00:
                    self.volume.setValue(value)
                elif param == 0x01:
                    self.pan.setValue(value - 64)
                elif param == 0x02:
                    self.portamento.setValue(value)
                elif param == 0x03:
                    self.porta_mode.setChecked(value > 64)
                    
            # Partial parameters are handled through the tab widgets
            # We'll need to route these to the correct partial tab
            else:
                partial_num = (section >> 5) + 1  # Calculate partial number from section
                param_offset = section & 0x1F     # Get parameter offset within partial
                
                # Find the correct tab and update its controls
                tab_widget = self.findChild(QTabWidget)
                if tab_widget:
                    partial_tab = tab_widget.widget(partial_num - 1)
                    if partial_tab:
                        self._update_partial_control(partial_tab, param_offset, value)
                        
        except Exception as e:
            logging.error(f"Error updating control: {str(e)}")

    def _update_partial_control(self, partial_tab, param_offset, value):
        """Update a control within a partial tab"""
        try:
            # Find the control based on parameter offset and update it
            # This will need to match the parameter offsets in DigitalPartial.Params
            controls = partial_tab.findChildren(QWidget)
            for control in controls:
                if isinstance(control, Slider):
                    if control.objectName() == f"param_{param_offset}":
                        control.setValue(value)
                elif isinstance(control, QComboBox):
                    if control.objectName() == f"param_{param_offset}":
                        control.setCurrentIndex(value)
                        
        except Exception as e:
            logging.error(f"Error updating partial control: {str(e)}")

    def _create_structure_section(self):
        """Create partial structure controls"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        header = QLabel("Structure")
        header.setStyleSheet(f"background-color: {Style.HEADER_BG}; color: white; padding: 5px;")
        layout.addWidget(header)
        
        # Create structure selector
        structure = QComboBox()
        structure.addItems([
            "Single (Partial 1)",
            "Layer (1+2)", 
            "Layer (2+3)",
            "Layer (1+3)",
            "Layer All",
            "Split (1/2)",
            "Split (2/3)", 
            "Split (1/3)"
        ])
        structure.currentIndexChanged.connect(self._update_structure)
        layout.addWidget(structure)
        
        # Create partial switches
        switches = QHBoxLayout()
        for i in range(3):
            switch = QPushButton(f"Partial {i+1}")
            switch.setCheckable(True)
            switch.setChecked(i == 0)  # Partial 1 on by default
            switch.clicked.connect(lambda checked, x=i: self._toggle_partial(x, checked))
            switches.addWidget(switch)
        layout.addLayout(switches)
        
        return frame

    def _create_partial_tab(self, partial_num):
        """Create a tab for a single partial"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Calculate parameter offset for this partial
        offset = (partial_num - 1) * DigitalPartial.Offset.PARTIAL_2
        
        # Create sections
        osc = self._create_osc_section(partial_num, offset)
        filter_section = self._create_filter_section(partial_num, offset)
        amp = self._create_amp_section(partial_num, offset)
        lfo = self._create_lfo_section(partial_num, offset)
        env = self._create_env_section(partial_num, offset)
        
        # Add sections to layout
        layout.addWidget(osc)
        layout.addWidget(filter_section)
        layout.addWidget(amp)
        layout.addWidget(lfo)
        layout.addWidget(env)
        layout.addStretch()
        
        return widget

    def _create_osc_section(self, partial_num, offset):
        """Create oscillator controls for a partial"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        header = QLabel(f"Oscillator {partial_num}")
        header.setStyleSheet(f"background-color: {Style.OSC_BG}; color: white; padding: 5px;")
        layout.addWidget(header)
        
        # Create wave selector
        wave = QComboBox()
        wave.addItems([
            "Super Saw", "Super Square", "Super Triangle", "Super Sine",
            "Noise", "PCM Synth", "PCM Drum", "External"
        ])
        wave.currentIndexChanged.connect(
            lambda v: self._update_parameter(partial_num, 'OSC_WAVE', v + offset)
        )
        layout.addWidget(wave)
        
        # Create sliders
        pitch = Slider(
            "Pitch", -24, 24,
            lambda v: self._update_parameter(partial_num, 'OSC_PITCH', v + offset)
        )
        fine = Slider(
            "Fine", -50, 50,
            lambda v: self._update_parameter(partial_num, 'OSC_FINE', v + offset)
        )
        pwm = Slider(
            "PWM", 0, 127,
            lambda v: self._update_parameter(partial_num, 'OSC_PWM', v + offset)
        )
        
        layout.addWidget(pitch)
        layout.addWidget(fine)
        layout.addWidget(pwm)
        
        return frame

    def _update_structure(self, index):
        """Update partial structure"""
        try:
            msg = create_parameter_message(
                DIGITAL_SYNTH_AREA,
                SUBGROUP_ZERO,
                DigitalPartial.CC.STRUCTURE,
                index
            )
            if self.midi_helper:
                self.midi_helper.send_message(msg)
        except Exception as e:
            logging.error(f"Error updating structure: {str(e)}")

    def _toggle_partial(self, partial_num, enabled):
        """Toggle partial on/off"""
        try:
            msg = create_parameter_message(
                DIGITAL_SYNTH_AREA,
                SUBGROUP_ZERO,
                DigitalPartial.CC.PARTIAL_SW + partial_num,
                127 if enabled else 0
            )
            if self.midi_helper:
                self.midi_helper.send_message(msg)
        except Exception as e:
            logging.error(f"Error toggling partial {partial_num}: {str(e)}")

    def _update_parameter(self, partial_num, param, value):
        """Update a parameter for a specific partial"""
        try:
            param_cc = getattr(DigitalPartial.CC, param)
            msg = create_parameter_message(
                DIGITAL_SYNTH_AREA,
                SUBGROUP_ZERO,
                param_cc + ((partial_num - 1) * DigitalPartial.Offset.PARTIAL_2),
                value
            )
            if self.midi_helper:
                self.midi_helper.send_message(msg)
        except Exception as e:
            logging.error(f"Error updating parameter {param} for partial {partial_num}: {str(e)}")

    def _create_amp_section(self, partial_num, offset):
        """Create amplifier controls for a partial"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        header = QLabel(f"Amplifier {partial_num}")
        header.setStyleSheet(f"background-color: {Style.VCA_BG}; color: white; padding: 5px;")
        layout.addWidget(header)
        
        # Create sliders
        level = Slider(
            "Level", 0, 127,
            lambda v: self._update_parameter(partial_num, 'AMP_LEVEL', v + offset)
        )
        pan = Slider(
            "Pan", -64, 63,
            lambda v: self._update_parameter(partial_num, 'AMP_PAN', v + offset)
        )
        
        layout.addWidget(level)
        layout.addWidget(pan)
        
        return frame

    def _create_lfo_section(self, partial_num, offset):
        """Create LFO controls for a partial"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        header = QLabel(f"LFO {partial_num}")
        header.setStyleSheet(f"background-color: {Style.LFO_BG}; color: white; padding: 5px;")
        layout.addWidget(header)
        
        # Create wave selector
        wave = QComboBox()
        wave.addItems([
            "Triangle", "Sine", "Sawtooth", "Square", 
            "Sample & Hold", "Random"
        ])
        wave.currentIndexChanged.connect(
            lambda v: self._update_parameter(partial_num, 'LFO_WAVE', v + offset)
        )
        layout.addWidget(wave)
        
        # Create sliders
        rate = Slider(
            "Rate", 0, 127,
            lambda v: self._update_parameter(partial_num, 'LFO_RATE', v + offset)
        )
        pitch = Slider(
            "Pitch Mod", 0, 127,
            lambda v: self._update_parameter(partial_num, 'LFO_PITCH', v + offset)
        )
        filter_mod = Slider(
            "Filter Mod", 0, 127,
            lambda v: self._update_parameter(partial_num, 'LFO_FILTER', v + offset)
        )
        amp_mod = Slider(
            "Amp Mod", 0, 127,
            lambda v: self._update_parameter(partial_num, 'LFO_AMP', v + offset)
        )
        
        layout.addWidget(rate)
        layout.addWidget(pitch)
        layout.addWidget(filter_mod)
        layout.addWidget(amp_mod)
        
        return frame

    def _create_env_section(self, partial_num, offset):
        """Create envelope controls for a partial"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        header = QLabel(f"Envelope {partial_num}")
        header.setStyleSheet(f"background-color: {Style.VCA_ENV_BG}; color: white; padding: 5px;")
        layout.addWidget(header)
        
        # Create ADSR sliders
        attack = Slider(
            "Attack", 0, 127,
            lambda v: self._update_parameter(partial_num, 'ENV_ATTACK', v + offset)
        )
        decay = Slider(
            "Decay", 0, 127,
            lambda v: self._update_parameter(partial_num, 'ENV_DECAY', v + offset)
        )
        sustain = Slider(
            "Sustain", 0, 127,
            lambda v: self._update_parameter(partial_num, 'ENV_SUSTAIN', v + offset)
        )
        release = Slider(
            "Release", 0, 127,
            lambda v: self._update_parameter(partial_num, 'ENV_RELEASE', v + offset)
        )
        
        layout.addWidget(attack)
        layout.addWidget(decay)
        layout.addWidget(sustain)
        layout.addWidget(release)
        
        return frame

    def _request_patch_data(self):
        """Request current patch data from device"""
        try:
            logging.debug(f"Requesting patch data for Digital Synth {self.synth_num}")
            
            # Calculate base address for this synth
            base_addr = [
                DIGITAL_SYNTH_AREA,  # Digital synth area
                self.synth_num,      # Synth number (1 or 2)
                0x00,                # Start at first parameter
                0x00                 # Parameter offset
            ]
            
            # Request common parameters
            common_msg = create_sysex_message(
                bytes(base_addr),
                bytes([0x20])  # Request 32 bytes of common parameters
            )
            
            # Request partial parameters (for each partial)
            partial_msgs = []
            for i in range(3):
                partial_addr = base_addr.copy()
                partial_addr[2] = i * DigitalPartial.Offset.PARTIAL_2  # Offset for each partial
                
                msg = create_sysex_message(
                    bytes(partial_addr),
                    bytes([0x40])  # Request 64 bytes of partial parameters
                )
                partial_msgs.append(msg)
            
            # Send all requests if MIDI is available
            if self.midi_helper:
                # Send common parameters request
                self.midi_helper.send_message(common_msg)
                logging.debug("Sent common parameters request")
                
                # Send partial parameters requests with slight delay
                for i, msg in enumerate(partial_msgs):
                    self.midi_helper.send_message(msg)
                    logging.debug(f"Sent partial {i+1} parameters request")
                    
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

    # ... (rest of the file remains unchanged) 