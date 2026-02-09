"""
Digital Oscillator Section for the JDXI Editor
"""

from typing import Callable

from PySide6.QtWidgets import (
    QHBoxLayout,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.midi.data.parameter.digital.spec import DigitalOscillatorTab, DigitalGroupBox
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.analog.oscillator.widget import OscillatorWidgets
from jdxi_editor.ui.editors.base.layout.spec import LayoutSpec
from jdxi_editor.ui.editors.base.oscillator import BaseOscillatorSection
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_envelope_group,
    create_group_from_definition,
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.controls.registry import ControlRegistry
from jdxi_editor.ui.widgets.pcm.wave import PCMWaveWidget
from jdxi_editor.ui.widgets.spec import PitchEnvelopeSpec, PWMSpec, SliderSpec


class DigitalOscillatorSection(BaseOscillatorSection):
    """Digital Oscillator Section for JD-Xi Editor (spec-driven)."""

    # --- Enable rules for dependent widgets (which tab/widgets to enable per waveform)
    BUTTON_ENABLE_RULES = {
        Digital.Wave.Osc.PW_SQUARE: ["pwm_widget", "pw_shift_slider"],
        Digital.Wave.Osc.PCM: ["pcm_wave_gain", "pcm_wave_number"],
        Digital.Wave.Osc.SUPER_SAW: ["super_saw_detune"],
    }

    # --- Optional ADSR can be added if Oscillator has one (Digital usually has pitch envelope)
    ADSR_SPEC = None

    PWM_SPEC = PWMSpec(
        pulse_width_param=Digital.Param.OSC_PULSE_WIDTH,
        mod_depth_param=Digital.Param.OSC_PULSE_WIDTH_MOD_DEPTH,
    )

    PITCH_ENV_SPEC = PitchEnvelopeSpec(
        attack_param=Digital.Param.OSC_PITCH_ENV_ATTACK_TIME,
        decay_param=Digital.Param.OSC_PITCH_ENV_DECAY_TIME,
        depth_param=Digital.Param.OSC_PITCH_ENV_DEPTH,
    )

    TAB_BUILDERS = (
        "_add_tuning_tab",
        ("_has_pwm", "_add_pwm_tab"),
        ("_has_pitch_env", "_add_pitch_env_tab"),
        ("_has_pcm", "_add_pcm_wave_gain_tab"),
        ("_has_adsr", "_add_adsr_tab"),
    )

    def generate_wave_shapes(self):
        """Generate waveform button specs (same pattern as Analog Oscillator / Analog Filter)."""
        W = self.SYNTH_SPEC.Wave
        return [
            SliderSpec(
                param=W.Osc.SAW,
                label=W.WaveType.UPSAW,
                icon_name=W.WaveType.UPSAW,
            ),
            SliderSpec(
                param=W.Osc.SQUARE,
                label=W.WaveType.SQUARE,
                icon_name=W.WaveType.SQUARE,
            ),
            SliderSpec(
                param=W.Osc.PW_SQUARE,
                label=W.WaveType.PWSQU,
                icon_name=W.WaveType.PWSQU,
            ),
            SliderSpec(
                param=W.Osc.TRI,
                label=W.WaveType.TRIANGLE,
                icon_name=W.WaveType.TRIANGLE,
            ),
            SliderSpec(
                param=W.Osc.SINE,
                label=W.WaveType.SINE,
                icon_name=W.WaveType.SINE,
            ),
            SliderSpec(
                param=W.Osc.NOISE,
                label=W.WaveType.NOISE,
                icon_name=W.WaveType.NOISE,
            ),
            SliderSpec(
                param=W.Osc.SUPER_SAW,
                label=W.WaveType.SPSAW,
                icon_name=W.WaveType.SPSAW,
            ),
            SliderSpec(
                param=W.Osc.PCM,
                label=W.WaveType.PCM,
                icon_name=W.WaveType.PCM,
            ),
        ]

    def __init__(
        self,
        icons_row_type: str = IconType.ADSR,
        analog: bool = False,
        send_midi_parameter: Callable = None,
        midi_helper: MidiIOHelper = None,
        address: JDXiSysExAddress = None,
    ):
        self.wave_shapes = self.generate_wave_shapes()
        self.SLIDER_GROUPS: LayoutSpec = self._build_layout_spec()
        # Initialize controls before creating PCMWaveWidget so it can register controls
        # (ControlRegistry is a singleton, so this ensures self.controls exists)
        self.controls = ControlRegistry()
        self.pcm_wave = PCMWaveWidget(groupbox_spec=DigitalGroupBox,
                                      create_parameter_combo_box=self._create_parameter_combo_box,
                                      send_param=send_midi_parameter)
        super().__init__(
            send_midi_parameter=send_midi_parameter,
            midi_helper=midi_helper,
            address=address,
            icons_row_type=icons_row_type,
            analog=analog,
        )
        # With singleton, controls registered by PCMWaveWidget are already in the shared registry
        # Just ensure they're accessible via self.controls
        self.controls[Digital.Param.PCM_WAVE_GAIN] = self.pcm_wave.pcm_wave_gain
        self.controls[Digital.Param.PCM_WAVE_NUMBER] = self.pcm_wave.pcm_wave_number
        # Also set as direct attributes for _has_pcm() compatibility (though we check pcm_wave now)
        self.pcm_wave_gain = self.pcm_wave.pcm_wave_gain
        self.pcm_wave_number = self.pcm_wave.pcm_wave_number

    def _get_param_specs(self):
        """Return [] so section_base does not build control sliders; we build them in _build_additional_digital_widgets() to avoid duplicate tuning sliders."""
        return []

    def build_widgets(self):
        """Override to create PitchEnvelopeWidget and PWMWidget from specs"""
        self.waveform_buttons = self._create_waveform_buttons()
        # Create Pitch Envelope widget from PITCH_ENV_SPEC (stores controls into self.controls)
        self.pitch_env_widget = self._create_pitch_env_widget()
        # Create PWMWidget from PWM_SPEC (base stores controls into self.controls)
        self.pwm_widget = self._create_pwm_widget()
        # Call parent to create other widgets (section_base uses SLIDER_GROUPS)
        super().build_widgets()
        if not self.analog:
            self._build_additional_digital_widgets()

        """Build widgets: run base to create waveform buttons, pitch env, PWM, then analog-specific (sub-osc switch, tuning)."""
        # Keep self.osc for any code that expects OscillatorWidgets (switches/tuning/env)
        self.widgets = OscillatorWidgets(
            waveform_buttons=(
                self.waveform_buttons),
            pitch_env_widget=(
                self.pitch_env_widget
            ),
            pwm_widget=self.pwm_widget
        )

    def _build_additional_digital_widgets(self):
        """Build control sliders from SLIDER_GROUPS (same pattern as Analog Oscillator), then PCM controls.
        Remove any control sliders already in tuning_control_widgets (from section_base) so we end up with exactly 3.
        """
        for param in (
            Digital.Param.OSC_PITCH,
            Digital.Param.OSC_DETUNE,
            Digital.Param.SUPER_SAW_DETUNE,
        ):
            if param in self.controls:
                w = self.controls.pop(param)
                if w in self.amp_control_widgets:
                    self.amp_control_widgets.remove(w)
        control_sliders = self._build_sliders(self.SLIDER_GROUPS.controls)
        if len(control_sliders) >= 3:
            self.osc_pitch_slider, self.osc_detune_slider, self.super_saw_detune = (
                control_sliders[0],
                control_sliders[1],
                control_sliders[2],
            )
            for spec, widget in zip(self.SLIDER_GROUPS.controls, control_sliders):
                self.controls[spec.param] = widget
                self.amp_control_widgets.append(widget)
            # Initially disable SuperSaw Detune (enabled when SuperSaw waveform is selected)
            self.super_saw_detune.setEnabled(False)
        self._create_pulse_width_shift_slider()

    def _create_pulse_width_shift_slider(self):
        """Create OSC_PULSE_WIDTH_SHIFT slider and register in controls (PWM tab)."""
        if not hasattr(Digital.Param, "OSC_PULSE_WIDTH_SHIFT"):
            return
        self.pw_shift_slider = self._create_parameter_slider(
            Digital.Param.OSC_PULSE_WIDTH_SHIFT,
            Digital.Display.Name.OSC_PULSE_WIDTH_SHIFT,
        )
        self.controls[Digital.Param.OSC_PULSE_WIDTH_SHIFT] = self.pw_shift_slider
        self.pw_shift_slider.setEnabled(False)

    def _has_pwm(self) -> bool:
        return getattr(self, "pwm_widget", None) is not None

    def _has_pitch_env(self) -> bool:
        return getattr(self, "pitch_env_widget", None) is not None

    def _has_pcm(self) -> bool:
        """Check if PCM wave widget exists and has both gain and number controls."""
        if not hasattr(self, "pcm_wave") or self.pcm_wave is None:
            return False
        return (
            hasattr(self.pcm_wave, "pcm_wave_gain")
            and self.pcm_wave.pcm_wave_gain is not None
            and hasattr(self.pcm_wave, "pcm_wave_number")
            and self.pcm_wave.pcm_wave_number is not None
        )

    def _has_adsr(self) -> bool:
        return getattr(self, "adsr_widget", None) is not None

    def _create_tab_widget(self):
        """Override to add PitchEnvelopeWidget and PWMWidget as tabs"""

        self.tab_widget = QTabWidget()

        for entry in self.TAB_BUILDERS:
            if isinstance(entry, str):
                getattr(self, entry)()
            else:
                predicate, builder = entry
                if getattr(self, predicate)():
                    getattr(self, builder)()

    def _add_adsr_tab(self):
        adsr_group = create_envelope_group(
            "Envelope", adsr_widget=self.adsr_widget, analog=self.analog
        )
        self._add_tab(key=DigitalOscillatorTab.ADSR, widget=adsr_group)

    def _add_pcm_wave_gain_tab(self):
        """Add PCM Wave gain tab"""
        self._add_tab(key=DigitalOscillatorTab.PCM, widget=self.pcm_wave)

    def _add_pitch_env_tab(self):
        """Add pitch env tab"""
        centered_layout = QHBoxLayout()
        centered_layout.addStretch()
        pitch_env_layout = create_layout_with_widgets(
            widgets=[self.pitch_env_widget], vertical=False
        )
        pitch_env_group = create_group_from_definition(
            key=Digital.GroupBox.PITCH_ENVELOPE,
            layout_or_widget=centered_layout,
            set_attr=self,
        )
        centered_layout.addLayout(pitch_env_layout)
        centered_layout.addStretch()
        pitch_env_group.setProperty("adsr", True)
        self._add_tab(key=DigitalOscillatorTab.PITCH, widget=pitch_env_group)

    def _add_pwm_tab(self):
        """Add PWM tab with optional pulse width shift slider and PWM widget."""
        pw_layout = QVBoxLayout()
        pw_layout.addStretch()
        if getattr(self, "pw_shift_slider", None) is not None:
            pw_layout.addWidget(self.pw_shift_slider)
        self.pwm_widget.setMaximumHeight(JDXi.UI.Style.PWM_WIDGET_HEIGHT)
        pw_layout.addWidget(self.pwm_widget)
        pw_layout.addStretch()
        pw_group = create_group_from_definition(
            key=Digital.GroupBox.PULSE_WIDTH,
            layout_or_widget=pw_layout,
            set_attr=self,
        )
        self._add_tab(key=DigitalOscillatorTab.PULSE_WIDTH, widget=pw_group)

    def _add_tuning_tab(self):
        """Add Tuning tab"""
        tuning_widget = self._create_row_widget(widgets=self.amp_control_widgets)
        self._add_tab(key=DigitalOscillatorTab.TUNING, widget=tuning_widget)

    def _create_row_widget(
        self,
        widgets: list[QWidget],
    ) -> QWidget:
        """Create a QWidget containing a horizontal row of widgets."""
        widget = QWidget()
        layout = create_layout_with_widgets(widgets, vertical=False)
        widget.setLayout(layout)
        return widget

    def _initialize_button_states(self):
        """Override to skip initialization until after all widgets are created"""
        # Don't initialize button states during __init__ - widgets may not exist yet
        # This will be called manually after all widgets are created
        pass

    def setup_ui(self):
        """Override to create UI with button row layout and initialize button states.
        Skip creating tab widget / button row if already done by base _setup_ui() in __init__,
        to avoid duplicate tuning sliders and ensure super_saw_detune enable targets the visible widget.
        """
        layout = self.get_layout()

        # Only add button row and tab widget if not already added by SectionBaseWidget._setup_ui()
        if self.tab_widget is None or self.tab_widget.parent() is None:
            if self.button_widgets:
                button_layout = self._create_button_row_layout()
                if button_layout is not None:
                    layout.addLayout(button_layout)
            self._create_tab_widget()
            if self.tab_widget:
                layout.addWidget(self.tab_widget)

        layout.addStretch()

        # Now that all widgets are created, initialize button states
        # This will also enable/disable SuperSaw Detune based on selected waveform
        if self.wave_shapes:
            self._on_button_selected(self.wave_shapes[0])

    def _build_layout_spec(self) -> LayoutSpec:
        """build Analog Oscillator Layout Spec"""
        S = self.SYNTH_SPEC
        controls = [
            SliderSpec(
                param=S.Param.OSC_PITCH,
                label=S.Param.OSC_PITCH.display_name,
            ),
            SliderSpec(
                param=S.Param.OSC_DETUNE,
                label=S.Param.OSC_DETUNE.display_name,
            ),
            SliderSpec(
                param=S.Param.SUPER_SAW_DETUNE,
                label=S.Param.SUPER_SAW_DETUNE.display_name,
            ),
        ]
        return LayoutSpec(controls=controls)
