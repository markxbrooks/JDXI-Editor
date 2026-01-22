"""
Digital Oscillator Section for the JDXI Editor
"""

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.digital.oscillator import DigitalOscWave, WaveformIconType
from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.option import DigitalDisplayOptions
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
from jdxi_editor.ui.editors.param_section import ParameterSectionBase
from jdxi_editor.ui.editors.widget_specs import SliderSpec
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.widgets.editor.helper import (
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.pitch.envelope import PitchEnvelopeWidget
from jdxi_editor.ui.widgets.pulse_width.pwm import PWMWidget


class DigitalOscillatorSection(ParameterSectionBase):
    """Digital Oscillator Section for JD-Xi Editor (spec-driven)."""

    # --- Sliders
    PARAM_SPECS = [
        SliderSpec(DigitalPartialParam.OSC_PITCH, DigitalDisplayName.OSC_PITCH),
        SliderSpec(DigitalPartialParam.OSC_DETUNE, DigitalDisplayName.OSC_DETUNE),
        SliderSpec(DigitalPartialParam.SUPER_SAW_DETUNE, DigitalDisplayName.SUPER_SAW_DETUNE),
    ]

    # --- Waveform buttons
    BUTTON_SPECS = [
        SliderSpec(DigitalOscWave.SAW, WaveformIconType.UPSAW, icon_name=WaveformIconType.UPSAW),
        SliderSpec(DigitalOscWave.SQUARE, WaveformIconType.SQUARE, icon_name=WaveformIconType.SQUARE),
        SliderSpec(DigitalOscWave.PW_SQUARE, WaveformIconType.PWSQU, icon_name=WaveformIconType.PWSQU),
        SliderSpec(DigitalOscWave.TRIANGLE, WaveformIconType.TRIANGLE, icon_name=WaveformIconType.TRIANGLE),
        SliderSpec(DigitalOscWave.SINE, WaveformIconType.SINE, icon_name=WaveformIconType.SINE),
        SliderSpec(DigitalOscWave.NOISE, WaveformIconType.NOISE, icon_name=WaveformIconType.NOISE),
        SliderSpec(DigitalOscWave.SUPER_SAW, WaveformIconType.SPSAW, icon_name=WaveformIconType.SPSAW),
        SliderSpec(DigitalOscWave.PCM, WaveformIconType.PCM, icon_name=WaveformIconType.PCM),
    ]

    # --- Enable rules for dependent widgets
    BUTTON_ENABLE_RULES = {
        DigitalOscWave.PW_SQUARE: ["pwm_widget", "pw_shift_slider"],
        DigitalOscWave.PCM: ["pwm_widget", "pcm_wave_gain", "pcm_wave_number"],
        DigitalOscWave.SUPER_SAW: ["super_saw_detune"],
    }

    # --- Optional ADSR can be added if Oscillator has one (Digital usually has pitch envelope)
    ADSR_SPEC = None

    def build_widgets(self):
        """Override to create PitchEnvelopeWidget and PWMWidget"""
        # Create PitchEnvelopeWidget for pitch envelope (Attack, Decay, Depth)
        self.pitch_env_widget = PitchEnvelopeWidget(
            attack_param=DigitalPartialParam.OSC_PITCH_ENV_ATTACK_TIME,
            decay_param=DigitalPartialParam.OSC_PITCH_ENV_DECAY_TIME,
            depth_param=DigitalPartialParam.OSC_PITCH_ENV_DEPTH,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
        )
        # Store pitch envelope controls
        self.controls[DigitalPartialParam.OSC_PITCH_ENV_ATTACK_TIME] = self.pitch_env_widget.attack_control
        self.controls[DigitalPartialParam.OSC_PITCH_ENV_DECAY_TIME] = self.pitch_env_widget.decay_control
        self.controls[DigitalPartialParam.OSC_PITCH_ENV_DEPTH] = self.pitch_env_widget.depth_control
        
        # Create PWMWidget for pulse width modulation
        self.pwm_widget = PWMWidget(
            pulse_width_param=DigitalPartialParam.OSC_PULSE_WIDTH,
            mod_depth_param=DigitalPartialParam.OSC_PULSE_WIDTH_MOD_DEPTH,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
        )
        # Store PWM controls
        self.controls[DigitalPartialParam.OSC_PULSE_WIDTH] = self.pwm_widget.pulse_width_control
        self.controls[DigitalPartialParam.OSC_PULSE_WIDTH_MOD_DEPTH] = self.pwm_widget.mod_depth_control
        
        # Call parent to create other widgets from PARAM_SPECS
        super().build_widgets()
    
    def _create_tab_widget(self):
        """Override to add PitchEnvelopeWidget and PWMWidget as tabs"""
        from PySide6.QtWidgets import QWidget, QTabWidget, QGroupBox, QHBoxLayout, QVBoxLayout
        from jdxi_editor.core.jdxi import JDXi
        from jdxi_editor.ui.widgets.editor.helper import create_envelope_group, create_adsr_icon
        from jdxi_editor.ui.image.waveform import generate_waveform_icon
        from jdxi_editor.ui.image.utils import base64_to_pixmap
        
        self.tab_widget = QTabWidget()

        # Controls tab
        controls_widget = QWidget()
        controls_layout = create_layout_with_widgets(self.control_widgets)
        controls_widget.setLayout(controls_layout)
        self.tab_widget.addTab(
            controls_widget, 
            JDXi.UI.IconRegistry.get_icon(JDXi.UI.IconRegistry.TUNE, JDXi.UI.Style.GREY), 
            "Controls"
        )

        # Pulse Width tab
        if hasattr(self, 'pwm_widget') and self.pwm_widget:
            pw_group = QGroupBox("Pulse Width")
            pw_layout = QVBoxLayout()
            pw_layout.addStretch()
            self.pwm_widget.setMaximumHeight(JDXi.UI.Style.PWM_WIDGET_HEIGHT)
            pw_layout.addWidget(self.pwm_widget)
            pw_layout.addStretch()
            pw_group.setLayout(pw_layout)
            # Use square wave icon for PWM tab
            pw_icon_base64 = generate_waveform_icon(WaveformIconType.SQUARE, JDXi.UI.Style.WHITE, 1.0)
            pw_icon = QIcon(base64_to_pixmap(pw_icon_base64))
            self.tab_widget.addTab(pw_group, pw_icon, "Pulse Width")

        # Pitch Envelope tab
        if hasattr(self, 'pitch_env_widget') and self.pitch_env_widget:
            pitch_env_group = QGroupBox("Pitch Envelope")
            pitch_env_group.setProperty("adsr", True)
            pitch_env_layout = QHBoxLayout()
            pitch_env_layout.addStretch()
            pitch_env_layout.addWidget(self.pitch_env_widget)
            pitch_env_layout.addStretch()
            pitch_env_group.setLayout(pitch_env_layout)
            self.tab_widget.addTab(pitch_env_group, create_adsr_icon(), "Pitch Env")

        # ADSR tab (if any)
        if self.adsr_widget:
            adsr_group = create_envelope_group("Envelope", adsr_widget=self.adsr_widget, analog=self.analog)
            self.tab_widget.addTab(adsr_group, create_adsr_icon(), "ADSR")

    def _initialize_button_states(self):
        """Override to skip initialization until after all widgets are created"""
        # Don't initialize button states during __init__ - widgets may not exist yet
        # This will be called manually after all widgets are created
        pass
    
    def setup_ui(self):
        """Override to initialize button states after all widgets are created"""
        super().setup_ui()
        # Now that all widgets are created, initialize button states
        if self.BUTTON_SPECS:
            first_param = self.BUTTON_SPECS[0].param
            self._on_button_selected(first_param)

    def _create_buttons(self):
        """Override to create waveform buttons with custom icon generation"""
        self.wave_buttons = {}
        self.wave_layout_widgets = []

        for spec in self.BUTTON_SPECS:
            wave = spec.param
            icon_type = spec.icon_name  # This is a WaveformIconType enum
            
            # --- Generate icon from waveform type
            icon_base64 = generate_waveform_icon(icon_type, JDXi.UI.Style.WHITE, 1.0)
            # --- Use QPushButton directly since WaveformButton expects Waveform enum, not DigitalOscWave
            from PySide6.QtWidgets import QPushButton
            btn = QPushButton(spec.label)  # Use label from spec
            btn.setCheckable(True)
            
            # --- Set icon
            pixmap = base64_to_pixmap(icon_base64)
            if pixmap and not pixmap.isNull():
                btn.setIcon(QIcon(pixmap))
                btn.setIconSize(QSize(20, 20))
            
            btn.setFixedSize(
                JDXi.UI.Dimensions.WAVEFORM_ICON.WIDTH,
                JDXi.UI.Dimensions.WAVEFORM_ICON.HEIGHT,
            )
            btn.clicked.connect(lambda _, w=wave: self._on_button_selected(w))
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)

            self.wave_buttons[wave] = btn
            self.button_widgets[wave] = btn
            self.controls[DigitalPartialParam.OSC_WAVE] = btn
            self.wave_layout_widgets.append(btn)
    
    def _create_button_row_layout(self):
        """Override to create waveform button row layout"""
        from PySide6.QtWidgets import QHBoxLayout
        
        # Create wave variation combo box
        self.wave_variation = self._create_parameter_combo_box(
            DigitalPartialParam.OSC_WAVE_VARIATION,
            DigitalDisplayName.OSC_WAVE_VARIATION,
            options=DigitalDisplayOptions.OSC_WAVE_VARIATION,
            values=[0, 1, 2],  # A, B, C
        )
        self.controls[DigitalPartialParam.OSC_WAVE_VARIATION] = self.wave_variation
        
        top_row = QHBoxLayout()
        top_row.addStretch()
        top_row.addLayout(create_layout_with_widgets(self.wave_layout_widgets))
        top_row.addWidget(self.wave_variation)  # Add wave variation switch
        top_row.addStretch()
        return top_row
    
    def _on_button_selected(self, button_param):
        """Override to handle waveform button selection with correct MIDI parameter"""
        # --- Reset all buttons
        for btn in self.button_widgets.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)
        
        # Set selected button
        selected_btn = self.button_widgets[button_param]
        selected_btn.setChecked(True)
        selected_btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)
        
        # Update enabled states
        self._update_button_enabled_states(button_param)
        
        # --- Send MIDI parameter - button_param is a DigitalOscWave enum
        if self.send_midi_parameter:
            self.send_midi_parameter(DigitalPartialParam.OSC_WAVE, button_param.value)
    
    def _update_button_enabled_states(self, button_param):
        """Override to enable/disable widgets based on selected waveform.
        
        This is called after all widgets are created (in setup_ui), so widgets
        should exist. We still check for None as a safety measure.
        """
        # --- Disable all first
        for attrs in self.BUTTON_ENABLE_RULES.values():
            for attr in attrs:
                widget = getattr(self, attr, None)
                if widget is not None:
                    widget.setEnabled(False)
        # --- Enable per selected button
        for attr in self.BUTTON_ENABLE_RULES.get(button_param, []):
            widget = getattr(self, attr, None)
            if widget is not None:
                widget.setEnabled(True)
