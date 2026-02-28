"""
LFO section of the digital partial editor.
"""

from enum import Enum, auto
from typing import Any, Callable

from decologr import Decologr as log
from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QButtonGroup,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QTabWidget,
)

from jdxi_editor.ui.common import JDXi, QWidget
from jdxi_editor.midi.data.analog.lfo import AnalogLFOShape
from jdxi_editor.midi.data.analog.oscillator import AnalogWaveOsc
from jdxi_editor.midi.data.base.oscillator import OscillatorWidgetTypes
from jdxi_editor.midi.data.digital import DigitalWaveOsc
from jdxi_editor.midi.data.digital.lfo import DigitalLFOShape
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.ui.editors.base.layout.spec import OscillatorFeature
from jdxi_editor.ui.editors.base.oscillator.layout_spec import OscillatorLayoutSpec
from jdxi_editor.ui.editors.base.oscillator.widget import OscillatorWidgets
from jdxi_editor.ui.image.waveform import generate_icon_from_waveform
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_group_with_widgets,
    create_layout_with_items,
    create_widget_with_layout,
)
from jdxi_editor.ui.widgets.editor.mode_button_group import (
    ModeButtonGroup,
    ModeButtonSpec,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.pitch.envelope import PitchEnvWidget
from jdxi_editor.ui.widgets.pulse_width.pwm import PWMWidget
from jdxi_editor.ui.widgets.spec import SliderSpec


class OscillatorComponent(Enum):
    """Oscillator Components"""

    WAVE_SELECTOR = auto()
    TUNING = auto()
    PWM = auto()
    PITCH_ENV = auto()
    PCM = auto()
    SUB_OSC = auto()
    ADSR = auto()


class BaseOscillatorSection(SectionBaseWidget):
    """Abstract base class for Oscillator sections (Analog and Digital)."""

    # Skip SectionBaseWidget._setup_ui() so layout/tabs are built once in finalize() -> setup_ui().
    SKIP_BASE_SETUP_UI = True

    controls_tab_label: str = "Controls"
    adsr_tab_label: str = "ADSR"
    spec: OscillatorLayoutSpec | None = None
    SYNTH_SPEC = Digital

    ANALOG_WAVES = [
        ("SAW", "UPSAW", "UPSAW"),
        ("TRI", "SQUARE", "SQUARE"),
        ("SQUARE", "PWSQU", "PWSQU"),
    ]

    DIGITAL_WAVES = [
        ("SAW", "UPSAW", "UPSAW"),
        ("SQUARE", "SQUARE", "SQUARE"),
        ("PW_SQUARE", "PWSQU", "PWSQU"),
        ("TRI", "TRIANGLE", "TRIANGLE"),
        ("SINE", "SINE", "SINE"),
        ("NOISE", "NOISE", "NOISE"),
        ("SUPER_SAW", "SPSAW", "SPSAW"),
        ("PCM", "PCM", "PCM"),
    ]

    def __init__(
        self,
        *,
        send_midi_parameter: Callable = None,
        midi_helper=None,
        address=None,
        icons_row_type: str = IconType.OSCILLATOR,
        analog: bool = False,
    ):
        """
        Initialize the BaseOscillatorSection
        :param send_midi_parameter: Callable to send MIDI parameters
        :param midi_helper: MIDI helper instance
        :param controls: Dictionary of controls
        :param address: Roland SysEx address
        :param icons_row_type: Type of icon
        :param analog: bool
        """

        self.widgets = OscillatorWidgets
        self.pitch_env_widgets = None
        # Param/key -> widget; use _register_widget() for dual-write during migration from named attrs
        self._widgets: dict[AddressParameter, QWidget] = {}
        self.shape_icon_map: dict | None = None
        self.sub_oscillator_type_switch: QPushButton | None = None
        self.tuning_sliders: list | None = None
        self.wave_layout_widgets: list = []
        self.wave_shape_param: list | None = None
        self.switch_row_widgets: list | None = None
        self.rate_layout_widgets: list | None = None
        self.depths_layout_widgets: list | None = None
        self._send_param: Callable | None = send_midi_parameter
        self.wave_shape_buttons: dict = {}  # --- Dictionary to store LFO shape buttons
        # QButtonGroup to enforce wave button exclusivity (Analog + Digital)
        self.wave_button_group: QButtonGroup | None = None
        self.analog: bool = analog
        # Subclasses (Analog/Digital oscillator) set wave_shapes before super().__init__; do not overwrite
        if getattr(self, "wave_shapes", None) is None:
            self.common_wave_shapes = [
                self.SYNTH_SPEC.Wave.Osc.SAW,
                self.SYNTH_SPEC.Wave.Osc.TRI,
                self.SYNTH_SPEC.Wave.Osc.SQUARE,
            ]
            self.wave_shapes = (
                self.common_wave_shapes
                if self.analog
                else self.common_wave_shapes
                + [
                    self.SYNTH_SPEC.Wave.Osc.TRI,
                    self.SYNTH_SPEC.Wave.Osc.SINE,
                    self.SYNTH_SPEC.Wave.Osc.NOISE,
                    self.SYNTH_SPEC.Wave.Osc.SUPER_SAW,
                    self.SYNTH_SPEC.Wave.Osc.PCM,
                ]
            )
        else:
            self.common_wave_shapes = getattr(self, "common_wave_shapes", [])
        super().__init__(
            send_midi_parameter=send_midi_parameter,
            midi_helper=midi_helper,
            address=address,
            icons_row_type=icons_row_type,
            analog=analog,
        )

    def widget_for(self, key: Any) -> QWidget | None:
        """Return the widget stored under key (e.g. OscillatorWidgetTypes.PITCH_ENV)."""
        return self._widgets.get(key)

    def _create_tab_widget(self):
        """Create tab widget only. Tabs are added once in setup_ui() via base _create_tabs(); do not add tabs here or they appear twice."""
        self.tab_widget = QTabWidget()

    def _get_button_specs(self):
        """Oscillator creates waveform buttons in its own build_widgets() / _create_core_widgets().
        Return [] so SectionBaseWidget.build_widgets() does not create a second set and overwrite
        button_widgets with param-only keys (which breaks _on_button_selected lookup by (param, label)).
        """
        return []

    def _create_tabs(self):
        for feature, builder_name in self.spec.feature_tabs.items():
            if feature not in self.spec.features:
                continue

            builder = getattr(self, builder_name, None)
            if builder is None:
                raise RuntimeError(
                    f"{self.__class__.__name__} missing tab builder '{builder_name}' "
                    f"for feature {feature}"
                )

            builder()

    def finalize(self):
        """Unified flow: feature widgets (if any), then setup_ui (layout + tabs), then init state. build_widgets runs once from __init__."""
        self._create_feature_widgets()
        self.setup_ui()
        self._initialize_states()

    def _define_spec(self):
        """Subclass must populate self.spec"""
        raise NotImplementedError

    def _build_wave_specs(self, spec_rows):
        W = self.SYNTH_SPEC.Wave
        return [
            SliderSpec(
                param=getattr(W.Osc, osc),
                label=getattr(W.WaveType, label),
                icon_name=getattr(W.WaveType, icon),
            )
            for osc, label, icon in spec_rows
        ]

    def _create_feature_widgets(self):
        """Subclass optional extension point"""
        pass

    def _initialize_states(self):
        if getattr(self, "wave_shapes", None):
            self._on_button_selected(self.wave_shapes[0])

    def _get_param_specs(self) -> list:
        """Return param specs for section_base._build_widgets. Oscillator layout specs (Analog) use .env/.tuning, not .controls."""
        if not hasattr(self.spec, "controls"):
            return []
        return getattr(self.spec, "controls", [])

    def build_widgets(self):
        """Unified flow: feature widgets (e.g. tuning_sliders for Analog), base widgets, tuning sliders, additional (Analog/Digital), then tab widget."""
        self._create_feature_widgets()
        super().build_widgets()
        self._create_tuning_sliders()
        self._build_additional_widgets()
        self._create_tab_widget()

    def setup_ui(self) -> None:
        """
        Setup the UI (standardized method name matching Digital Oscillator)
        :return: None
        """
        layout = self.get_layout(margins=JDXi.UI.Dimensions.EDITOR.MARGINS)
        # --- Waveform buttons ---
        self.waveform_button_layout = self._create_wave_layout()
        layout.addLayout(self.waveform_button_layout)
        # --- Tab widget (same as self.tab_widget so _add_tab adds tabs to the widget in the layout) ---
        JDXi.UI.Theme.apply_tabs_style(self.tab_widget, analog=self.analog)
        layout.addWidget(self.tab_widget)
        self._create_tabs()

        layout.addStretch()

    def _add_pitch_env_tab(self):
        self.pitch_widget = self._create_tuning_pitch_widget()
        self._add_tab(key=self.SYNTH_SPEC.Wave.Tab.PITCH, widget=self.pitch_widget)

    def _add_pwm_tab(self):
        self.pw_group = self._create_pw_group()
        self._add_tab(key=self.SYNTH_SPEC.Wave.Tab.PULSE_WIDTH, widget=self.pw_group)

    def _add_tuning_tab(self):
        self.tuning_group = self._create_tuning_group()
        self._add_tab(key=self.SYNTH_SPEC.Wave.Tab.TUNING, widget=self.tuning_group)

    def _has(self, feature: OscillatorFeature) -> bool:
        return self.spec.supports(feature)

    def _register_widget(
        self,
        key: Any,
        widget: QWidget,
        *,
        legacy_attr: str | None = None,
    ) -> None:
        """
        Store widget by key. During migration also set legacy named attr so existing
        code keeps working; later remove legacy_attr and delete the named params.
        """
        self._widgets[key] = widget
        if legacy_attr is not None:
            setattr(self, legacy_attr, widget)

    def _create_waveform_buttons(self):
        """Create waveform buttons. Analog uses ModeButtonGroup (same as Digital); other subclasses use manual QButtonGroup."""
        if self.analog:
            return self._create_waveform_buttons_mode_group()
        return self._create_waveform_buttons_manual()

    def _create_waveform_buttons_mode_group(self):
        """Analog path: use ModeButtonGroup for exclusive waveform row (harmonized with Digital oscillator)."""
        specs = [
            ModeButtonSpec(
                mode=spec.param,
                label=spec.label,
                icon_name=spec.icon_name,
            )
            for spec in self.wave_shapes
        ]

        def _on_mode_changed(mode):
            self._update_button_enabled_states(mode)
            if hasattr(self, "_on_waveform_selected") and callable(
                getattr(self, "_on_waveform_selected", None)
            ):
                self._on_waveform_selected(mode)

        def _waveform_icon_factory(icon_name):
            key = getattr(icon_name, "value", icon_name)
            return generate_icon_from_waveform(key)

        self.wave_mode_group = ModeButtonGroup(
            specs,
            analog=self.analog,
            send_midi_parameter=self._send_param,
            midi_param=self.SYNTH_SPEC.Param.OSC_WAVEFORM,
            on_mode_changed=_on_mode_changed,
            icon_factory=_waveform_icon_factory,
            parent=None,
        )
        self.wave_layout_widgets = list(self.wave_mode_group.buttons.values())
        self.controls[self.SYNTH_SPEC.Param.OSC_WAVEFORM] = self.wave_mode_group
        return self.wave_mode_group.buttons

    def _create_waveform_buttons_manual(self):
        """Manual QPushButton + QButtonGroup path (used when not analog and subclass does not override)."""
        waveform_buttons = {}
        self.wave_layout_widgets = []

        if self.wave_button_group is None:
            self.wave_button_group = QButtonGroup(self)
            self.wave_button_group.setExclusive(True)

        for spec in self.wave_shapes:
            wave = spec.param
            icon_name = spec.icon_name  # This is a WaveformIconType enum

            pixmap = generate_icon_from_waveform(icon_name)
            # --- Use QPushButton directly since WaveformButton expects Waveform enum, not Digital.Wave.Osc

            btn = QPushButton(spec.label)  # Use label from spec
            btn.setCheckable(True)

            # --- Set icon
            if pixmap and not pixmap.isNull():
                btn.setIcon(QIcon(pixmap))
                btn.setIconSize(QSize(20, 20))

            btn.setFixedSize(
                JDXi.UI.Dimensions.WaveformIcon.WIDTH,
                JDXi.UI.Dimensions.WaveformIcon.HEIGHT,
            )

            # Use (param, label) as key so duplicate params (e.g. SQUARE and PWSQU) each have a button
            btn_key = (spec.param, getattr(spec, "label", None))

            def _on_click(_, s=spec):
                self._on_button_selected(s)
                # Invoke editor callback when set (e.g. Analog waveform_selected_callback)
                if hasattr(self, "_on_waveform_selected") and callable(
                    getattr(self, "_on_waveform_selected", None)
                ):
                    self._on_waveform_selected(s.param)

            btn.clicked.connect(_on_click)

            # Base style (match Digital Filter section mode buttons)
            JDXi.UI.Theme.apply_button_rect(btn, analog=self.analog)

            # Add to the exclusive button group
            self.wave_button_group.addButton(btn)

            waveform_buttons[wave] = btn  # last wins for param-only lookup
            self.button_widgets[btn_key] = btn
            self.controls[self.SYNTH_SPEC.Param.OSC_WAVEFORM] = btn
            self.wave_layout_widgets.append(btn)
        return waveform_buttons

    def _on_wave_shape_selected(self, lfo_shape: DigitalLFOShape | AnalogLFOShape):
        """
        Handle Mod LFO shape button clicks

        :param lfo_shape: DigitalLFOShape enum value
        """
        for btn in self.wave_shape_buttons.values():
            btn.setChecked(False)
            JDXi.UI.Theme.apply_button_rect(btn, analog=self.analog)
        selected_btn = self.wave_shape_buttons.get(lfo_shape)
        if selected_btn:
            selected_btn.setChecked(True)
            JDXi.UI.Theme.apply_button_active(widget=selected_btn, analog=self.analog)

        # ---  Send MIDI message
        if self._send_param:
            if not self._send_param(self.wave_shape_param, lfo_shape.value):
                log.warning(f"Failed to set Mod LFO shape to {lfo_shape.name}")

    def _create_switch_row_layout(self) -> QHBoxLayout:
        """Create Switch row"""
        switch_row_layout = create_layout_with_items(self.switch_row_widgets)
        return switch_row_layout

    def _create_switch_layout_widgets(self):
        """Create switch layout widgets"""
        if not hasattr(self, "spec") or not hasattr(self.spec, "switches"):
            self.switch_row_widgets = []
        else:
            self.switch_row_widgets = self._build_switches(self.spec.switches)

    def _on_button_selected(self, spec_or_param):
        """Override to handle waveform button selection with correct MIDI parameter.

        spec_or_param: SliderSpec (with .param, .label) or a single param enum for backward compat.
        """
        if hasattr(spec_or_param, "param") and hasattr(spec_or_param, "label"):
            btn_key = (spec_or_param.param, getattr(spec_or_param, "label", None))
            button_param = spec_or_param.param
        else:
            btn_key = spec_or_param
            button_param = spec_or_param

        # Reset all buttons (use wave_layout_widgets so every button is reset; button_widgets may have duplicate keys)
        for btn in self.wave_layout_widgets:
            btn.setChecked(False)
            JDXi.UI.Theme.apply_button_rect(btn, analog=self.analog)

        selected_btn = self.button_widgets.get(btn_key)
        if selected_btn is None:
            # Fallback when only param was passed (e.g. initial state): first button with this param
            for (p, _), b in self.button_widgets.items():
                if p == button_param:
                    selected_btn = b
                    break
        if selected_btn is not None:
            selected_btn.setChecked(True)
            JDXi.UI.Theme.apply_button_active(selected_btn, analog=self.analog)

        # Update enabled states
        self._update_button_enabled_states(button_param)

        # --- Send MIDI parameter - button_param is a Digital.Wave.Osc / AnalogWaveOsc enum.
        # Guard with _suppress_waveform_midi so data_request-driven UI updates don't echo MIDI.
        if self._send_param and not getattr(self, "_suppress_waveform_midi", False):
            self._send_param(self.SYNTH_SPEC.Param.OSC_WAVEFORM, button_param.value)

    def _resolve_rule_widget(self, key):
        """Resolve a BUTTON_ENABLE_RULES key to a widget. Prefer _widgets, then attribute."""
        w = self.widget_for(key)
        if w is not None:
            return w
        return getattr(self, key, None)

    def _update_button_enabled_states(self, button_param):
        """Override to enable/disable widgets based on selected waveform.

        This is called after all widgets are created (in setup_ui), so widgets
        should exist. We still check for None as a safety measure.
        """
        # --- Disable all first
        for attrs in self.BUTTON_ENABLE_RULES.values():
            for key in attrs:
                widget = self._resolve_rule_widget(key)
                if widget is not None:
                    widget.setEnabled(False)
        # --- Enable per selected button
        for key in self.BUTTON_ENABLE_RULES.get(button_param, []):
            widget = self._resolve_rule_widget(key)
            if widget is not None:
                widget.setEnabled(True)

    def _create_button_row_layout(self):
        """Override to create waveform button row layout"""

        # --- Create wave variation combo box
        self.wave_variation = self._create_parameter_combo_box(
            self.SYNTH_SPEC.Param.OSC_WAVE_VARIATION,
            self.SYNTH_SPEC.Display.Name.OSC_WAVE_VARIATION,
            options=self.SYNTH_SPEC.Display.Options.OSC_WAVE_VARIATION,
            values=[0, 1, 2],  # A, B, C
        )
        self.controls[self.SYNTH_SPEC.Param.OSC_WAVE_VARIATION] = self.wave_variation

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addLayout(create_layout_with_items(self.wave_layout_widgets))
        button_row.addWidget(self.wave_variation)  # Add wave variation switch
        button_row.addStretch()
        return button_row

    def _create_tuning_pitch_widget(self) -> QWidget:
        """Create tuning and pitch widget combining Tuning and Pitch Envelope (standardized name matching Digital)"""
        pitch_layout = create_layout_with_items(items=[self._create_pitch_env_group()])
        pitch_widget = create_widget_with_layout(pitch_layout)
        pitch_widget.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MIN_HEIGHT)
        return pitch_widget

    def _create_wave_layout(self) -> QHBoxLayout:
        """
        Create the waveform buttons layout (ModeButtonGroup when analog, else manual button row).
        """
        if getattr(self, "wave_mode_group", None) is not None:
            row = QHBoxLayout()
            row.addStretch()
            row.addWidget(self.wave_mode_group)
            if self.sub_oscillator_type_switch is not None:
                row.addWidget(self.sub_oscillator_type_switch)
            row.addStretch()
            return row
        waveform_buttons_list = [
            w for w in self.wave_mode_group.buttons.values() if w is not None
        ]
        if self.sub_oscillator_type_switch is not None:
            waveform_buttons_list.append(self.sub_oscillator_type_switch)
        wave_layout = create_layout_with_items(waveform_buttons_list)
        return wave_layout

    def _create_tuning_group(self) -> QGroupBox:
        """
        Create the tuning group (standardized private method matching Digital)

        :return: QGroupBox
        """
        tuning_group = create_group_with_widgets(
            label="Controls", widgets=self.tuning_sliders
        )
        return tuning_group

    def _create_pw_group(self) -> QGroupBox:
        """
        Create the pulse width group (standardized private method matching Digital)

        :return: QGroupBox
        """
        pwm_widget = self.widget_for(OscillatorWidgetTypes.PWM) or getattr(
            self.widgets, "pwm_widget", None
        )
        pw_group = create_group_with_widgets(
            label="Pulse Width", widgets=[pwm_widget] if pwm_widget else []
        )
        return pw_group

    def _create_pitch_env_group(self) -> QGroupBox:
        """
        Create the pitch envelope group (standardized private method matching Digital)

        :return: QGroupBox
        """
        pitch_env = self.widget_for(OscillatorWidgetTypes.PITCH_ENV)
        widgets = [pitch_env] if pitch_env else (self.pitch_env_widgets or [])
        pitch_env_group = create_group_with_widgets(
            label="Pitch Envelope", widgets=widgets
        )
        return pitch_env_group

    def _on_waveform_selected_local(self, waveform: AnalogWaveOsc | DigitalWaveOsc):
        """
        Handle waveform button selection locally (for section-level handling)
        This is separate from the editor's callback to avoid conflicts.

        :param waveform: AnalogOscWave value
        :return: None
        """
        if self.midi_helper:
            sysex_message = self.sysex_composer.compose_message(
                address=self.address,
                param=self.SYNTH_SPEC.Param.OSC_WAVEFORM,
                value=waveform.value,
            )
            self.midi_helper.send_midi_message(sysex_message)

            # --- Reset all buttons to default style (match Digital Filter section mode buttons)
            for btn in self.wave_mode_group.buttons.values():
                btn.setChecked(False)
                JDXi.UI.Theme.apply_button_rect(btn, analog=self.analog)
            # --- Apply active style to the selected waveform button
            selected_btn = self.wave_mode_group.buttons.get(waveform)
            if selected_btn:
                selected_btn.setChecked(True)
                JDXi.UI.Theme.apply_button_active(selected_btn, analog=self.analog)

    def _create_pwm_widget(self) -> PWMWidget:
        """Create PWM widget from PWM_SPEC or SYNTH_SPEC params."""
        spec = getattr(self, "PWM_SPEC", None)
        if spec is not None:
            pulse_width_param = spec.pulse_width_param
            mod_depth_param = spec.mod_depth_param
        else:
            pulse_width_param = self.SYNTH_SPEC.Param.OSC_PULSE_WIDTH
            mod_depth_param = self.SYNTH_SPEC.Param.OSC_PULSE_WIDTH_MOD_DEPTH
        pwm_widget = PWMWidget(
            pulse_width_param=pulse_width_param,
            mod_depth_param=mod_depth_param,
            midi_helper=self.midi_helper,
            address=self.address,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            analog=self.analog,
        )
        return pwm_widget

    def _create_pitch_env_widget(self) -> PitchEnvWidget:
        """Create Pitch Envelope widget from PITCH_ENV_SPEC or SYNTH_SPEC params."""
        spec = getattr(self, "PITCH_ENV_SPEC", None)
        if spec is not None:
            attack_param = spec.attack_param
            decay_param = spec.decay_param
            depth_param = spec.depth_param
        else:
            attack_param = self.SYNTH_SPEC.Param.OSC_PITCH_ENV_ATTACK_TIME
            decay_param = self.SYNTH_SPEC.Param.OSC_PITCH_ENV_DECAY_TIME
            depth_param = self.SYNTH_SPEC.Param.OSC_PITCH_ENV_DEPTH
        pitch_env_widget = PitchEnvWidget(
            attack_param=attack_param,
            decay_param=decay_param,
            depth_param=depth_param,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
            analog=self.analog,
        )
        return pitch_env_widget

    def _build_additional_widgets(self):
        raise NotImplementedError("Should be implemented in a subclass")

    def _build_additional_digital_widgets(self):
        raise NotImplementedError("Should be implemented in a Digital subclass")

    def _build_additional_analog_widgets(self):
        raise NotImplementedError("Should be implemented in an Analog subclass")

    def _add_pcm_wave_gain_tab(self):
        raise NotImplementedError("Should be implemented in a subclass")

    def _create_tuning_sliders(self):
        """create tuning sliders"""
        # Reset
        self.osc_pitch_coarse_slider = None
        self.osc_pitch_fine_slider = None
        self.super_saw_detune = None
        self.tuning_sliders = []

        # Remove previous tuning controls cleanly
        for spec in self.spec.tuning:
            param = spec.param
            if param in self.controls:
                w = self.controls.pop(param)
                if w in self.amp_control_widgets:
                    self.amp_control_widgets.remove(w)

        sliders = self._build_sliders(self.spec.tuning)

        for spec, widget in zip(self.spec.tuning, sliders):
            self.controls[spec.param] = widget
            self.amp_control_widgets.append(widget)

            param_name = spec.param.name  # enum name string

            if param_name == "OSC_PITCH_COARSE":
                self.osc_pitch_coarse_slider = widget
                self.tuning_sliders.append(widget)

            elif param_name == "OSC_PITCH_FINE":
                self.osc_pitch_fine_slider = widget
                self.tuning_sliders.append(widget)

            elif param_name == "SUPER_SAW_DETUNE":
                self.super_saw_detune = widget

        if self.super_saw_detune:
            self.super_saw_detune.setEnabled(False)
