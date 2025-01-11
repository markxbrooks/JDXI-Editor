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
    create_sysex_message,
    create_patch_load_message,
    create_patch_save_message,
    JDXiSysEx
)
from jdxi_manager.midi.constants import (
    START_OF_SYSEX, ROLAND_ID, DEVICE_ID, MODEL_ID_1, MODEL_ID_2,
    MODEL_ID, JD_XI_ID, DT1_COMMAND_12, END_OF_SYSEX,
    DIGITAL_SYNTH_AREA,
    DIGITAL_SYNTH_1, DIGITAL_PART_1,
    PROGRAM_GROUP, COMMON_GROUP, PARTIAL_GROUP,
    SUBGROUP_ZERO,
    Waveform, DigitalGroup, DigitalPartial
)
from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.data.digital import DigitalSynth


class DigitalSynthEditor(BaseEditor):
    def __init__(self, synth_num=1, midi_helper=None, parent=None):
        """Initialize digital synth editor"""
        super().__init__(midi_helper, parent)
        self.synth_num = synth_num
        self.area = DIGITAL_SYNTH_1 if synth_num == 1 else DIGITAL_SYNTH_2
        self.part = DIGITAL_PART_1 if synth_num == 1 else DIGITAL_PART_2
        
        # Verify MIDI helper
        logging.debug(f"MIDI helper: {midi_helper}")
        if midi_helper:
            logging.debug(f"MIDI out port: {midi_helper.current_out_port}")
        
        # Set window properties
        self.setStyleSheet(Style.MAIN_STYLESHEET)
        self.setFixedWidth(1000)
        self.setMinimumHeight(600)
        self.setWindowTitle(f"Digital Synth {synth_num}")
        
        # Create UI
        self._create_ui()
        
        # Request patch data immediately
        if self.midi_helper:
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
        volume = Slider("Volume", 0, 127)
        volume.valueChanged.connect(
            lambda v: self._send_parameter(
                area=self.area,
                part=self.part,
                group=COMMON_GROUP,
                param=0x00,  # Volume
                value=v
            )
        )
        
        pan = Slider("Pan", -64, 63)
        pan.valueChanged.connect(
            lambda v: self._send_parameter(
                area=self.area,
                part=self.part,
                group=COMMON_GROUP,
                param=0x01,  # Pan
                value=v + 64  # Center at 64
            )
        )
        
        portamento = Slider("Portamento", 0, 127)
        portamento.valueChanged.connect(
            lambda v: self._send_parameter(
                area=self.area,
                part=self.part,
                group=COMMON_GROUP,
                param=0x02,  # Portamento
                value=v
            )
        )
        
        porta_mode = QPushButton("Porta Mode")
        porta_mode.setCheckable(True)
        porta_mode.clicked.connect(
            lambda checked: self._send_parameter(
                area=self.area,
                part=self.part,
                group=COMMON_GROUP,
                param=0x03,  # Porta Mode
                value=127 if checked else 0
            )
        )
        
        # Add to layout
        layout.addWidget(volume)
        layout.addWidget(pan)
        layout.addWidget(portamento)
        layout.addWidget(porta_mode)
        
        return section

    def _create_oscillator_section(self, partial_num, offset):
        """Create oscillator controls for a partial"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        header = QLabel(f"Oscillator {partial_num}")
        header.setStyleSheet(f"background-color: {Style.OSC_BG}; color: white; padding: 5px;")
        layout.addWidget(header)
        
        # Create wave selector using correct JD-Xi waveform values
        wave = QComboBox()
        waveforms = [
            ("SAW", Waveform.SAW.value),             # 0x00
            ("SQUARE", Waveform.SQUARE.value),       # 0x01
            ("PW SQUARE", Waveform.PW_SQUARE.value), # 0x02
            ("TRIANGLE", Waveform.TRIANGLE.value),   # 0x03
            ("SINE", Waveform.SINE.value),           # 0x04
            ("NOISE", Waveform.NOISE.value),         # 0x05
            ("SUPER SAW", Waveform.SUPER_SAW.value), # 0x06
            ("PCM", Waveform.PCM.value)              # 0x07
        ]
        wave.addItems([name for name, _ in waveforms])
        wave.currentIndexChanged.connect(
            lambda idx: self._send_partial_parameter(
                group=PARTIAL_GROUP,      # 0x20
                param=DigitalPartial.CC.OSC_WAVE.value,  # Base parameter (0x00)
                value=waveforms[idx][1],  # Get actual JD-Xi value for selected waveform
                partial_num=partial_num
            )
        )
        layout.addWidget(wave)
        
        # Create sliders
        pitch = Slider("Pitch", -24, 24)
        pitch.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,      # 0x20
                param=DigitalPartial.CC.OSC_PITCH.value,  # Base parameter (0x01)
                value=v + 64,  # Center at 64
                partial_num=partial_num
            )
        )
        
        fine = Slider("Fine", -50, 50)
        fine.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,      # 0x20
                param=DigitalPartial.CC.OSC_FINE.value,  # Base parameter (0x02)
                value=v + 64,  # Center at 64
                partial_num=partial_num
            )
        )
        
        pwm = Slider("PWM", 0, 127)
        pwm.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,      # 0x20
                param=DigitalPartial.CC.OSC_PWM.value,  # Base parameter (0x03)
                value=v,
                partial_num=partial_num
            )
        )
        
        layout.addWidget(pitch)
        layout.addWidget(fine)
        layout.addWidget(pwm)
        
        return frame

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
        filter_types = [
            ("LPF", 0x00),      # Low Pass Filter
            ("HPF", 0x01),      # High Pass Filter
            ("BPF", 0x02),      # Band Pass Filter
            ("PKG", 0x03),      # Peaking Filter
            ("OFF", 0x04)       # Filter Off
        ]
        filter_type.addItems([name for name, _ in filter_types])
        filter_type.currentIndexChanged.connect(
            lambda idx: self._send_partial_parameter(
                group=PARTIAL_GROUP,
                param=DigitalPartial.CC.FILTER_TYPE.value,  # 0x0A
                value=filter_types[idx][1],
                partial_num=partial_num
            )
        )
        layout.addWidget(filter_type)
        
        # Create filter parameter sliders
        cutoff = Slider("Cutoff", 0, 127)
        cutoff.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,
                param=DigitalPartial.CC.FILTER_CUTOFF.value,  # 0x0B
                value=v,
                partial_num=partial_num
            )
        )
        
        resonance = Slider("Resonance", 0, 127)
        resonance.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,
                param=DigitalPartial.CC.FILTER_RESO.value,  # 0x0C
                value=v,
                partial_num=partial_num
            )
        )
        
        env_depth = Slider("Env Depth", -64, 63)
        env_depth.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,
                param=DigitalPartial.CC.FILTER_ENV.value,  # 0x0D
                value=v + 64,  # Center at 64
                partial_num=partial_num
            )
        )
        
        key_follow = Slider("Key Follow", -64, 63)
        key_follow.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,
                param=DigitalPartial.CC.FILTER_KEY.value,  # 0x0E
                value=v + 64,  # Center at 64
                partial_num=partial_num
            )
        )
        
        velocity = Slider("Velocity", -64, 63)
        velocity.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,
                param=DigitalPartial.CC.FILTER_VELO.value,  # 0x0F
                value=v + 64,  # Center at 64
                partial_num=partial_num
            )
        )
        
        # Add controls to layout
        layout.addWidget(cutoff)
        layout.addWidget(resonance)
        layout.addWidget(env_depth)
        layout.addWidget(key_follow)
        layout.addWidget(velocity)
        
        return frame

    def _send_filter_parameter(self, partial_num: int, param_name: str, value: int):
        """Send filter parameter change"""
        try:
            # Get parameter CC value
            param = getattr(DigitalPartial.CC, f"FILTER_{param_name}").value
            
            # Log the parameter details
            logging.debug(
                f"Sending filter parameter: partial={partial_num} "
                f"param={param_name}(0x{param:02X}) value={value}"
            )
            
            # Send parameter with proper group
            self._send_partial_parameter(
                group=PARTIAL_GROUP,      # 0x20
                param=param,              # Parameter number
                value=value,             # Parameter value
                partial_num=partial_num  # Partial number for offset
            )
            
        except Exception as e:
            logging.error(f"Error sending filter parameter: {str(e)}")
            logging.exception(e)

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
        level = Slider("Level", 0, 127)
        level.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,      # 0x20
                param=DigitalPartial.CC.AMP_LEVEL.value,  # 0x15
                value=v,
                partial_num=partial_num
            )
        )
        
        pan = Slider("Pan", -64, 63)
        pan.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,      # 0x20
                param=DigitalPartial.CC.AMP_PAN.value,  # 0x16
                value=v + 64,  # Center at 64
                partial_num=partial_num
            )
        )
        
        layout.addWidget(level)
        layout.addWidget(pan)
        
        return frame

    def _create_modulation_section(self, partial_num):
        """Create modulation section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        
        # LFO parameters
        lfo_group = QGroupBox("LFO")
        lfo_layout = QVBoxLayout(lfo_group)
        
        # Create wave selector
        wave = QComboBox()
        lfo_waves = [
            ("Triangle", 0x00),
            ("Sine", 0x01),
            ("Sawtooth", 0x02),
            ("Square", 0x03),
            ("Sample & Hold", 0x04),
            ("Random", 0x05)
        ]
        wave.addItems([name for name, _ in lfo_waves])
        wave.currentIndexChanged.connect(
            lambda idx: self._send_partial_parameter(
                group=PARTIAL_GROUP,
                param=DigitalPartial.CC.LFO_WAVE.value,  # 0x30
                value=lfo_waves[idx][1],
                partial_num=partial_num
            )
        )
        
        rate = Slider("Rate", 0, 127)
        rate.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,
                param=DigitalPartial.CC.LFO_RATE.value,  # 0x31
                value=v,
                partial_num=partial_num
            )
        )
        
        depth = Slider("Depth", 0, 127)
        depth.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,
                param=DigitalPartial.CC.LFO_DEPTH.value,  # 0x32
                value=v,
                partial_num=partial_num
            )
        )
        
        lfo_layout.addWidget(wave)
        lfo_layout.addWidget(rate)
        lfo_layout.addWidget(depth)
        
        layout.addWidget(lfo_group)
        
        return section

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
        offset = (partial_num - 1) * DigitalPartial.Offset.PARTIAL_2.value
        
        # Create sections
        osc = self._create_oscillator_section(partial_num, offset)
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
        lfo_waves = [
            ("Triangle", 0x00),
            ("Sine", 0x01),
            ("Sawtooth", 0x02),
            ("Square", 0x03),
            ("Sample & Hold", 0x04),
            ("Random", 0x05)
        ]
        wave.addItems([name for name, _ in lfo_waves])
        wave.currentIndexChanged.connect(
            lambda idx: self._send_partial_parameter(
                group=PARTIAL_GROUP,      # 0x20
                param=DigitalPartial.CC.LFO_WAVE.value,  # 0x30
                value=lfo_waves[idx][1],
                partial_num=partial_num
            )
        )
        layout.addWidget(wave)
        
        # Create sliders
        rate = Slider("Rate", 0, 127)
        rate.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,      # 0x20
                param=DigitalPartial.CC.LFO_RATE.value,  # 0x31
                value=v,
                partial_num=partial_num
            )
        )
        
        pitch = Slider("Pitch Mod", 0, 127)
        pitch.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,      # 0x20
                param=DigitalPartial.CC.LFO_PITCH.value,  # 0x33
                value=v,
                partial_num=partial_num
            )
        )
        
        filter_mod = Slider("Filter Mod", 0, 127)
        filter_mod.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,      # 0x20
                param=DigitalPartial.CC.LFO_FILTER.value,  # 0x34
                value=v,
                partial_num=partial_num
            )
        )
        
        amp_mod = Slider("Amp Mod", 0, 127)
        amp_mod.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,      # 0x20
                param=DigitalPartial.CC.LFO_AMP.value,  # 0x35
                value=v,
                partial_num=partial_num
            )
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
        attack = Slider("Attack", 0, 127)
        attack.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,      # 0x20
                param=DigitalPartial.CC.ENV_ATTACK.value,  # 0x40
                value=v,
                partial_num=partial_num
            )
        )
        
        decay = Slider("Decay", 0, 127)
        decay.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,      # 0x20
                param=DigitalPartial.CC.ENV_DECAY.value,  # 0x41
                value=v,
                partial_num=partial_num
            )
        )
        
        sustain = Slider("Sustain", 0, 127)
        sustain.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,      # 0x20
                param=DigitalPartial.CC.ENV_SUSTAIN.value,  # 0x42
                value=v,
                partial_num=partial_num
            )
        )
        
        release = Slider("Release", 0, 127)
        release.valueChanged.connect(
            lambda v: self._send_partial_parameter(
                group=PARTIAL_GROUP,      # 0x20
                param=DigitalPartial.CC.ENV_RELEASE.value,  # 0x43
                value=v,
                partial_num=partial_num
            )
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
                partial_addr[2] = i * DigitalPartial.Offset.PARTIAL_2.value
                
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

    def load_preset(self, preset_name: str):
        """Load a preset patch"""
        try:
            if hasattr(self, 'preset_type') and self.preset_type.currentText() == 'Basic Waveforms':
                # Handle basic waveform presets
                if preset_name in DigitalSynth.WAVEFORMS:
                    waveform_value = DigitalSynth.WAVEFORMS[preset_name]
                    self._send_parameter(DIGITAL_SYNTH_AREA, 0x00, waveform_value)
                    logging.info(f"Loaded basic waveform: {preset_name}")
            else:
                # Handle SuperNATURAL presets
                if preset_name in DigitalSynth.SN_PRESETS:
                    # Extract program number from preset name (first 3 digits)
                    program_num = int(preset_name.split(':')[0])
                    # Send program change
                    self.load_program(program_num)
                    logging.info(f"Loaded SN preset: {preset_name}")
                else:
                    logging.error(f"Preset not found: {preset_name}")
                
        except Exception as e:
            logging.error(f"Error loading preset {preset_name}: {str(e)}")

    def _create_preset_section(self):
        """Create preset selection section"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header("Presets"))
        
        # Create scroll area for presets
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create widget for preset buttons
        preset_widget = QWidget()
        preset_layout = QVBoxLayout(preset_widget)
        
        # Add preset buttons
        for preset_name in DigitalSynth.SN_PRESETS:
            btn = QPushButton(preset_name)
            btn.clicked.connect(lambda checked, name=preset_name: self.load_preset(name))
            preset_layout.addWidget(btn)
        
        # Add stretch at bottom
        preset_layout.addStretch()
        
        # Set up scroll area
        scroll.setWidget(preset_widget)
        layout.addWidget(scroll)
        
        return frame

    def _update_structure(self, index):
        """Update partial structure"""
        try:
            self._send_parameter(
                area=self.area,
                part=self.part,
                group=COMMON_GROUP,
                param=0x00,  # Structure parameter
                value=index
            )
            logging.debug(f"Updated structure to index {index}")
        except Exception as e:
            logging.error(f"Error updating structure: {str(e)}")
            logging.exception(e)

    def _toggle_partial(self, partial_num, enabled):
        """Toggle partial on/off"""
        try:
            self._send_parameter(
                area=self.area,
                part=self.part,
                group=COMMON_GROUP,
                param=0x01 + partial_num,  # Partial switch parameter (0x01, 0x02, 0x03)
                value=127 if enabled else 0
            )
            logging.debug(f"Toggled partial {partial_num} {'on' if enabled else 'off'}")
        except Exception as e:
            logging.error(f"Error toggling partial {partial_num}: {str(e)}")
            logging.exception(e)

    def _send_partial_parameter(self, group: int, param: int, value: int, partial_num: int = 1):
        """Send parameter for a specific partial
        
        Args:
            group: Parameter group (e.g. PARTIAL_GROUP)
            param: Base parameter number
            value: Parameter value
            partial_num: Partial number (1-3)
        """
        try:
            # Calculate partial offset
            partial_offset = (partial_num - 1) * DigitalPartial.Offset.PARTIAL_2.value
            logging.debug(f"Partial {partial_num} offset: {hex(partial_offset)}")
            
            # Add partial offset to parameter address
            param_with_offset = param + partial_offset
            logging.debug(
                f"Parameter {hex(param)} + offset {hex(partial_offset)} = "
                f"{hex(param_with_offset)}"
            )
            
            # Send parameter
            self._send_parameter(
                area=self.area,      # DIGITAL_SYNTH_1 or DIGITAL_SYNTH_2
                part=self.part,      # DIGITAL_PART_1 or DIGITAL_PART_2
                group=group,         # Parameter group
                param=param_with_offset,  # Parameter number with partial offset
                value=value         # Parameter value
            )
            logging.debug(
                f"Sent partial parameter: partial={partial_num} "
                f"param=0x{param:02X} value={value}"
            )
            
        except Exception as e:
            logging.error(f"Error sending partial parameter: {str(e)}")
            logging.exception(e)

    # ... (rest of the file remains unchanged) 