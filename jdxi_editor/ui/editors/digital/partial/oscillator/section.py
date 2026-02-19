"""
Digital Oscillator Section for the JDXI Editor
"""

from typing import Callable

from decologr import Decologr as log
from PySide6.QtWidgets import (
    QHBoxLayout,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.midi.data.digital.oscillator import DigitalOscillatorWidgetTypes
from jdxi_editor.midi.data.parameter.digital.spec import (
    DigitalGroupBox,
    DigitalOscillatorTab,
)
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.base.layout.spec import OscillatorFeature
from jdxi_editor.ui.editors.base.oscillator.section import BaseOscillatorSection
from jdxi_editor.ui.editors.digital.partial.oscillator.spec import (
    DigitalOscillatorLayoutSpec,
)
from jdxi_editor.ui.editors.digital.partial.oscillator.widget import (
    DigitalOscillatorWidgets,
)
from jdxi_editor.ui.image.waveform import generate_icon_from_waveform
from jdxi_editor.ui.widgets.controls.registry import ControlRegistry
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_group_from_definition,
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.editor.mode_button_group import (
    ModeButtonGroup,
    ModeButtonSpec,
)
from jdxi_editor.ui.widgets.pcm.wave import PCMWaveWidget
from jdxi_editor.ui.widgets.spec import PitchEnvelopeSpec, PWMSpec, SliderSpec


class DigitalOscillatorSection(BaseOscillatorSection):
    """Digital Oscillator Section for JD-Xi Editor (spec-driven)."""

    # --- Enable rules for dependent widgets (which tab/widgets to enable per waveform)
    BUTTON_ENABLE_RULES = {
        Digital.Wave.Osc.PW_SQUARE: [
            DigitalOscillatorWidgetTypes.PWM,
            DigitalOscillatorWidgetTypes.PW_SHIFT,
        ],
        Digital.Wave.Osc.PCM: [
            DigitalOscillatorWidgetTypes.PCM_WAVE_GAIN,
            DigitalOscillatorWidgetTypes.PCM_WAVE_NUMBER,
        ],
        Digital.Wave.Osc.SUPER_SAW: [DigitalOscillatorWidgetTypes.SUPER_SAW_DETUNE],
    }

    def generate_wave_shapes(self):
        """Generate waveform button specs (same pattern as Analog Oscillator / Analog Filter)."""
        return self.generate_wave_shapes_digital()

    def __init__(
        self,
        icons_row_type: str = IconType.ADSR,
        analog: bool = False,
        send_midi_parameter: Callable = None,
        midi_helper: MidiIOHelper = None,
        address: JDXiSysExAddress = None,
    ):
        self.widgets: DigitalOscillatorWidgets | None = None
        self.wave_shapes = self.generate_wave_shapes()
        self._define_spec()
        self.wave_mode_group: ModeButtonGroup | None = None
        # Initialize controls before creating PCMWaveWidget so it can register controls
        # (ControlRegistry is a singleton, so this ensures self.controls exists)
        self.controls = ControlRegistry()
        self.pcm_wave = PCMWaveWidget(
            groupbox_spec=DigitalGroupBox,
            create_parameter_combo_box=self._create_parameter_combo_box,
            send_param=send_midi_parameter,
        )
        super().__init__(
            send_midi_parameter=send_midi_parameter,
            midi_helper=midi_helper,
            address=address,
            icons_row_type=icons_row_type,
            analog=analog,
        )
        # With singleton, controls registered by PCMWaveWidget are already in the shared registry
        # Just ensure they're accessible via self.controls
        self.controls[self.SYNTH_SPEC.Param.PCM_WAVE_GAIN] = self.pcm_wave.pcm_wave_gain
        self.controls[self.SYNTH_SPEC.Param.PCM_WAVE_NUMBER] = (
            self.pcm_wave.pcm_wave_number
        )
        # Also set as direct attributes for _has_pcm() compatibility (though we check pcm_wave now)
        self.pcm_wave_gain = self.pcm_wave.pcm_wave_gain
        self.pcm_wave_number = self.pcm_wave.pcm_wave_number
        self.finalize()

    def finalize(self):
        """Skip base _assemble_ui(); Digital builds UI via SectionBaseWidget._setup_ui and TAB_BUILDERS (no pitch_widget/tuning_group/pw_group)."""
        self._initialize_states()

    def _define_spec(self):
        self.spec: DigitalOscillatorLayoutSpec = self._build_layout_spec()

    def _setup_ui(self):
        """Assemble section UI with centered waveform button row (same pattern as Digital Filter mode buttons)."""
        layout = self.create_layout()
        # Centered waveform button row
        if self.wave_mode_group is not None:
            if self.wave_mode_group.parent() is None:
                self.wave_mode_group.setParent(self)
            row = QHBoxLayout()
            row.addStretch()
            row.addWidget(self.wave_mode_group)
            row.addStretch()
            layout.addLayout(row)
        self._create_tab_widget()
        layout.addWidget(self.tab_widget)

    def _create_tab_widget(self):
        """Override to add PitchEnvelopeWidget and PWMWidget as tabs"""

        self.tab_widget = QTabWidget()
        try:
            for feature, builder in self.spec.feature_tabs.items():
                if self._has(feature):
                    log.message(f"feature {feature} found, running {builder}")
                    builder()
                else:
                    log.message(f"feature {feature} not found!!!")
        except Exception as ex:
            log.exception(
                f"Error {ex} occurred creating tab widget",
                scope=self.__class__.__name__,
            )

    # ------------------------------------------------------------------
    # Waveform buttons via ModeButtonGroup (shared pattern with filter modes)
    # ------------------------------------------------------------------
    def _create_waveform_buttons(self):
        """Create Digital wave buttons using ModeButtonGroup instead of raw QPushButtons."""
        specs = [
            ModeButtonSpec(
                mode=spec.param,  # Digital.Wave.Osc.*
                label=spec.label,
                icon_name=spec.icon_name,
            )
            for spec in self.wave_shapes
        ]

        def _on_mode_changed(mode):
            # Enable/disable dependent widgets per BUTTON_ENABLE_RULES
            self._update_button_enabled_states(mode)

        def _waveform_icon_factory(icon_name):
            # Waveform icons use PIL-generated pixmaps, not QtAwesome names
            key = getattr(icon_name, "value", icon_name)
            return generate_icon_from_waveform(key)

        self.wave_mode_group = ModeButtonGroup(
            specs,
            analog=self.analog,
            send_midi_parameter=self._send_param,
            midi_param=Digital.Param.OSC_WAVEFORM,
            on_mode_changed=_on_mode_changed,
            icon_factory=_waveform_icon_factory,
            parent=None,
        )

        # Expose legacy mapping API used elsewhere
        self.waveform_buttons = self.wave_mode_group.buttons
        self.wave_layout_widgets = list(self.wave_mode_group.buttons.values())
        return self.waveform_buttons

    def _create_feature_widgets(self):
        # pcm_wave is already created in __init__ before super().__init__()/finalize()
        self._build_additional_widgets()

        self.tuning_sliders = [
            self.osc_pitch_coarse_slider,
            self.osc_pitch_fine_slider,
        ]

    def _get_param_specs(self):
        """Return [] so section_base does not build control sliders; we build them in _build_additional_digital_widgets() to avoid duplicate tuning sliders."""
        return []

    def build_widgets(self):
        """Override to create PitchEnvelopeWidget and PWMWidget from specs"""
        self.waveform_buttons = self._create_waveform_buttons()
        # Create Pitch Envelope widget from PITCH_ENV_SPEC (stores controls into self.controls)
        self.pitch_env_widget = self._create_pitch_env_widget()
        self.pitch_env_widgets = [self.pitch_env_widget]

        # Create PWMWidget from PWM_SPEC (base stores controls into self.controls)
        self.pwm_widget = self._create_pwm_widget()
        # Call parent to create other widgets (section_base uses SLIDER_GROUPS)
        super().build_widgets()
        self._build_additional_widgets()

        self.tuning_sliders = [
            self.osc_pitch_coarse_slider,
            self.osc_pitch_fine_slider,
        ]

        # All oscillator widgets in one container (same shape as Analog)
        self.widgets = DigitalOscillatorWidgets(
            waveform_buttons=self.waveform_buttons,
            pitch_env_widget=self.pitch_env_widget,
            pwm_widget=self.pwm_widget,
            tuning=self.tuning_sliders,
            env=[],
            pcm_wave=getattr(self, "pcm_wave", None),
            pw_shift_slider=getattr(self, DigitalOscillatorWidgetTypes.PW_SHIFT, None),
            osc_pitch_coarse_slider=getattr(
                self, DigitalOscillatorWidgetTypes.OSC_PITCH_COARSE, None
            ),
            osc_pitch_fine_slider=getattr(
                self, DigitalOscillatorWidgetTypes.OSC_PITCH_FINE, None
            ),
            super_saw_detune=getattr(
                self, DigitalOscillatorWidgetTypes.SUPER_SAW_DETUNE, None
            ),
        )

    def _build_additional_widgets(self):
        self._build_additional_digital_widgets()

    def _build_additional_digital_widgets(self):
        """Build control sliders from SLIDER_GROUPS (same pattern as Analog Oscillator), then PCM controls.
        Remove any control sliders already in tuning_control_widgets (from section_base) so we end up with exactly 3.
        """
        for param in (
            self.SYNTH_SPEC.Param.OSC_PITCH_COARSE,
            self.SYNTH_SPEC.Param.OSC_PITCH_FINE,
            self.SYNTH_SPEC.Param.SUPER_SAW_DETUNE,
        ):
            if param in self.controls:
                w = self.controls.pop(param)
                if w in self.amp_control_widgets:
                    self.amp_control_widgets.remove(w)
        control_sliders = self._build_sliders(self.spec.tuning)
        if len(control_sliders) >= 3:
            (
                self.osc_pitch_coarse_slider,
                self.osc_pitch_fine_slider,
                self.super_saw_detune,
            ) = (
                control_sliders[0],
                control_sliders[1],
                control_sliders[2],
            )
            for spec, widget in zip(self.spec.tuning, control_sliders):
                self.controls[spec.param] = widget
                self.amp_control_widgets.append(widget)
            # Initially disable SuperSaw Detune (enabled when SuperSaw waveform is selected)
            self.super_saw_detune.setEnabled(False)
        self._create_pulse_width_shift_slider()

    def _create_pulse_width_shift_slider(self):
        """Create OSC_PULSE_WIDTH_SHIFT slider and register in controls (PWM tab)."""
        if not hasattr(self.SYNTH_SPEC.Param, "OSC_PULSE_WIDTH_SHIFT"):
            return None
        self.pw_shift_sliders = self._build_sliders(self.spec.pw_controls)
        self.pw_shift_slider = self.pw_shift_sliders[0]
        self.controls[Digital.Param.OSC_PULSE_WIDTH_SHIFT] = self.pw_shift_slider
        self.pw_shift_slider.setEnabled(False)
        return self.pw_shift_slider

    def _has_pwm(self) -> bool:
        return getattr(self, DigitalOscillatorWidgetTypes.PWM, None) is not None

    def _has_pitch_env(self) -> bool:
        return getattr(self, DigitalOscillatorWidgetTypes.PITCH_ENV, None) is not None

    def _has_pcm(self) -> bool:
        """Check if PCM wave widget exists and has both gain and number controls."""
        if not hasattr(self, "pcm_wave") or self.pcm_wave is None:
            return False
        return (
            hasattr(self.pcm_wave, DigitalOscillatorWidgetTypes.PCM_WAVE_GAIN)
            and self.pcm_wave.pcm_wave_gain is not None
            and hasattr(self.pcm_wave, DigitalOscillatorWidgetTypes.PCM_WAVE_NUMBER)
            and self.pcm_wave.pcm_wave_number is not None
        )

    def _has_adsr(self) -> bool:
        return getattr(self, "adsr_widget", None) is not None

    def _add_pcm_tab(self):
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
        self.pwm_widget.setMaximumHeight(JDXi.UI.Style.PWM_WIDGET_HEIGHT)
        pw_layout.addWidget(self.pwm_widget)
        if getattr(self, DigitalOscillatorWidgetTypes.PW_SHIFT, None) is not None:
            pw_layout.addWidget(self.pw_shift_slider)
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
        # --- Waveform buttons ---
        self.waveform_button_layout = self._create_wave_layout()
        layout.addLayout(self.waveform_button_layout)
        JDXi.UI.Theme.apply_tabs_style(self.tab_widget, analog=self.analog)
        layout.addWidget(self.tab_widget)

        layout.addStretch()

        if self.wave_shapes:
            self._on_button_selected(self.wave_shapes[0])

    def _build_layout_spec(self) -> DigitalOscillatorLayoutSpec:
        """build Analog Oscillator Layout Spec"""
        S = self.SYNTH_SPEC
        tuning = [
            SliderSpec(
                param=S.Param.OSC_PITCH_COARSE,
                label=S.Param.OSC_PITCH_COARSE.display_name,
            ),
            SliderSpec(
                param=S.Param.OSC_PITCH_FINE,
                label=S.Param.OSC_PITCH_FINE.display_name,
            ),
            SliderSpec(
                param=S.Param.SUPER_SAW_DETUNE,
                label=S.Param.SUPER_SAW_DETUNE.display_name,
            ),
        ]
        pw_controls = [
            SliderSpec(
                param=S.Param.OSC_PULSE_WIDTH_SHIFT,
                label=S.Display.Name.OSC_PULSE_WIDTH_SHIFT,
                vertical=False,
            ),
        ]
        pwm = PWMSpec(
            pulse_width_param=S.Param.OSC_PULSE_WIDTH,
            mod_depth_param=S.Param.OSC_PULSE_WIDTH_MOD_DEPTH,
        )
        pitch_env = PitchEnvelopeSpec(
            attack_param=S.Param.OSC_PITCH_ENV_ATTACK_TIME,
            decay_param=S.Param.OSC_PITCH_ENV_DECAY_TIME,
            depth_param=S.Param.OSC_PITCH_ENV_DEPTH,
        )
        return DigitalOscillatorLayoutSpec(
            tuning=tuning,
            pw_controls=pw_controls,
            pwm=pwm,
            pitch_env=pitch_env,
            features={
                OscillatorFeature.WAVEFORM,
                OscillatorFeature.TUNING,
                OscillatorFeature.PWM,
                OscillatorFeature.PITCH_ENV,
                OscillatorFeature.PCM,
                OscillatorFeature.SUPER_SAW,
                OscillatorFeature.PW_SHIFT,
            },
            feature_tabs={
                OscillatorFeature.TUNING: self._add_tuning_tab,
                OscillatorFeature.PWM: self._add_pwm_tab,
                OscillatorFeature.PITCH_ENV: self._add_pitch_env_tab,
                OscillatorFeature.PCM: self._add_pcm_tab,
            },
        )
