"""
Digital Oscillator Section for the JDXI Editor
"""

from typing import Callable

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from decologr import Decologr as log
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.digital.oscillator import DigitalOscWave, WaveformIconType
from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.option import DigitalDisplayOptions
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
from jdxi_editor.midi.data.pcm.waves import PCM_WAVES_CATEGORIZED
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.digital.partial.pwm import PWMWidget
from jdxi_editor.ui.editors.widget_specs import SliderSpec
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.widgets.button.waveform.waveform import WaveformButton
from jdxi_editor.ui.widgets.combo_box.searchable_filterable import (
    SearchableFilterableComboBox,
)
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_layout_with_widgets,
    create_widget_with_layout,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.pitch.envelope import PitchEnvelopeWidget


class DigitalOscillatorSection(SectionBaseWidget):
    """Digital Oscillator Section for the JDXI Editor"""

    # --- Spec-driven sliders for tuning and supersaw
    TUNING_SLIDERS = [
        SliderSpec(DigitalPartialParam.OSC_PITCH, DigitalDisplayName.OSC_PITCH),
        SliderSpec(DigitalPartialParam.OSC_DETUNE, DigitalDisplayName.OSC_DETUNE),
        SliderSpec(DigitalPartialParam.SUPER_SAW_DETUNE, DigitalDisplayName.SUPER_SAW_DETUNE),
    ]

    # --- Waveform buttons spec
    WAVEFORM_BUTTONS = [
        (DigitalOscWave.SAW, "UPSAW"),
        (DigitalOscWave.SQUARE, "SQUARE"),
        (DigitalOscWave.PW_SQUARE, "PWSQU"),
        (DigitalOscWave.TRIANGLE, "TRIANGLE"),
        (DigitalOscWave.SINE, "SINE"),
        (DigitalOscWave.NOISE, "NOISE"),
        (DigitalOscWave.SUPER_SAW, "SPSAW"),
        (DigitalOscWave.PCM, "PCM"),
    ]

    # --- Declarative waveform-enable mapping
    WAVEFORM_ENABLE_RULES = {
        DigitalOscWave.PW_SQUARE: ["pwm_widget", "pw_shift_slider"],
        DigitalOscWave.PCM: ["pcm_wave_gain", "pcm_wave_number"],
        DigitalOscWave.SUPER_SAW: ["super_saw_detune"],
    }

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable,
        create_parameter_combo_box: Callable,
        send_midi_parameter: Callable,
        partial_number: int,
        midi_helper,
        controls: dict,
        address,
    ):
        self.partial_number = partial_number
        self.midi_helper = midi_helper
        self.controls = controls
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._create_parameter_combo_box = create_parameter_combo_box
        self.send_midi_parameter = send_midi_parameter
        self.address = address
        self.pwm_widget = None

        super().__init__(icon_type=IconType.OSCILLATOR, analog=False)

        self.build_widgets()
        self.setup_ui()
        self._initialise_control_states()

    def build_widgets(self):
        """Build all widgets in order."""
        self._create_waveform_buttons()
        self.wave_variation_switch = self._create_parameter_switch(
            DigitalPartialParam.OSC_WAVE_VARIATION,
            DigitalDisplayName.OSC_WAVE_VARIATION,
            DigitalDisplayOptions.OSC_WAVE_VARIATION,
        )
        self._create_tuning_layout_widgets()
        self._create_pitch_env_widget()
        self._create_tuning_pitch_widget()
        self._create_tuning_group()
        self._create_pwm_widgets()
        self._create_pcm_widgets()
        self._create_tab_widget()

    def _create_tab_widget(self):
        """Create and populate the tab widget"""
        self.oscillator_tab_widget = QTabWidget()
        
        # --- Tuning and Pitch tab (combines Tuning and Pitch Envelope like Analog) ---
        tuning_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.MUSIC_NOTE, color=JDXi.UI.Style.GREY
        )
        self.oscillator_tab_widget.addTab(
            self.pitch_widget, tuning_icon, "Pitch"
        )
        self.oscillator_tab_widget.addTab(
            self.tuning_group, tuning_icon, "Tuning"
        )

        # --- Pulse Width tab ---
        pw_group = self._create_pw_group()
        pw_icon = JDXi.UI.IconRegistry.get_generated_icon("square")
        self.oscillator_tab_widget.addTab(pw_group, pw_icon, "Pulse Width")

        # --- PCM Wave tab (unique to Digital) ---
        pcm_group = self._create_pcm_group()
        pcm_icon = JDXi.UI.IconRegistry.get_generated_icon("pcm")
        self.oscillator_tab_widget.addTab(pcm_group, pcm_icon, "PCM Wave")

    def setup_ui(self):
        """Assemble the oscillator section UI."""
        layout = self.get_layout(margins=(1, 1, 1, 1))
        layout.addLayout(self.create_waveform_buttons_layout())
        layout.addWidget(self.oscillator_tab_widget)
        layout.addStretch()

    # --- Waveform buttons ---
    def _create_waveform_buttons(self):
        self.wave_buttons = {}
        self.wave_layout_widgets = []

        for wave, icon_type in self.WAVEFORM_BUTTONS:
            icon_base64 = generate_waveform_icon(icon_type, JDXi.UI.Style.WHITE, 1.0)
            btn = WaveformButton(wave)
            btn.setIcon(QIcon(base64_to_pixmap(icon_base64)))
            btn.setFixedSize(
                JDXi.UI.Dimensions.WAVEFORM_ICON.WIDTH,
                JDXi.UI.Dimensions.WAVEFORM_ICON.HEIGHT,
            )
            btn.clicked.connect(lambda _, w=wave: self._on_waveform_selected(w))
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)

            self.wave_buttons[wave] = btn
            self.controls[DigitalPartialParam.OSC_WAVE] = btn
            self.wave_layout_widgets.append(btn)

    def create_waveform_buttons_layout(self) -> QHBoxLayout:
        """create wave form buttons"""
        top_row = QHBoxLayout()
        top_row.addStretch()
        top_row.addLayout(create_layout_with_widgets(self.wave_layout_widgets))
        top_row.addWidget(self.wave_variation_switch)
        top_row.addStretch()
        return top_row

    # --- Tuning
    def _create_tuning_layout_widgets(self):
        """create tuning layout widgets"""
        sliders = {
            spec.param: self._create_parameter_slider(spec.param, spec.label, vertical=True)
            for spec in self.TUNING_SLIDERS
        }
        self.super_saw_detune = sliders[DigitalPartialParam.SUPER_SAW_DETUNE]
        self.tuning_layout_widgets = list(sliders.values())

    def _create_pitch_env_widget(self):
        """create pitch env widget"""
        self.pitch_env_widget = PitchEnvelopeWidget(
            attack_param=DigitalPartialParam.OSC_PITCH_ENV_ATTACK_TIME,
            decay_param=DigitalPartialParam.OSC_PITCH_ENV_DECAY_TIME,
            depth_param=DigitalPartialParam.OSC_PITCH_ENV_DEPTH,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
        )

    def _create_tuning_pitch_widget(self):
        """create tuning pitch widgets"""
        pitch_layout = create_layout_with_widgets([self._create_pitch_env_group()])
        self.pitch_widget = create_widget_with_layout(pitch_layout)
        self.pitch_widget.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MINIMUM_HEIGHT)

    def _create_pitch_env_group(self) -> QGroupBox:
        """create pitch env group"""
        group = QGroupBox("Pitch Envelope")
        layout = QVBoxLayout()
        layout.addWidget(self.pitch_env_widget)
        group.setLayout(layout)
        JDXi.UI.ThemeManager.apply_adsr_style(self.pitch_env_widget)
        return group

    def _create_tuning_group(self):
        """create tuning group"""
        self.tuning_group = QGroupBox("Tuning")
        layout = create_layout_with_widgets(self.tuning_layout_widgets)
        self.tuning_group.setLayout(layout)
        JDXi.UI.ThemeManager.apply_adsr_style(self.tuning_group)

    # --- PWM
    def _create_pwm_widgets(self):
        """create pwm widgets"""
        self.pw_shift_slider = self._create_parameter_slider(
            DigitalPartialParam.OSC_PULSE_WIDTH_SHIFT,
            DigitalDisplayName.OSC_PULSE_WIDTH_SHIFT,
            vertical=True,
        )
        self.pwm_widget = PWMWidget(
            pulse_width_param=DigitalPartialParam.OSC_PULSE_WIDTH,
            mod_depth_param=DigitalPartialParam.OSC_PULSE_WIDTH_MOD_DEPTH,
            midi_helper=self.midi_helper,
            address=self.address,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
        )
        self.pw_widgets = [self.pwm_widget, self.pw_shift_slider]

    def _create_pw_group(self) -> QGroupBox:
        """create pw group"""
        group = QGroupBox("Pulse Width")
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addLayout(create_layout_with_widgets(self.pw_widgets))
        layout.addStretch()
        group.setLayout(layout)
        self.pwm_widget.setMaximumHeight(JDXi.UI.Style.PWM_WIDGET_HEIGHT)
        JDXi.UI.ThemeManager.apply_adsr_style(self.pwm_widget)
        JDXi.UI.ThemeManager.apply_adsr_style(self.pw_shift_slider)
        return group

    # --- PCM ---
    def _create_pcm_widgets(self):
        """create pcm widgets"""
        self.pcm_wave_gain = self._create_parameter_combo_box(
            DigitalPartialParam.PCM_WAVE_GAIN,
            DigitalDisplayName.PCM_WAVE_GAIN,
            options=DigitalDisplayOptions.PCM_WAVE_GAIN,
        )

        pcm_options = [f"{w['Wave Number']}: {w['Wave Name']}" for w in PCM_WAVES_CATEGORIZED]
        pcm_values = [w["Wave Number"] for w in PCM_WAVES_CATEGORIZED]
        pcm_categories = sorted(set(w["Category"] for w in PCM_WAVES_CATEGORIZED))

        def pcm_category_filter(wave_name, category):
            if not category:
                return True
            for wave in PCM_WAVES_CATEGORIZED:
                if f"{wave['Wave Number']}: {wave['Wave Name']}" == wave_name:
                    return wave["Category"] == category
            return False

        self.pcm_wave_number = SearchableFilterableComboBox(
            label=DigitalDisplayName.PCM_WAVE_NUMBER,
            options=pcm_options,
            values=pcm_values,
            categories=pcm_categories,
            category_filter_func=pcm_category_filter,
            show_label=True,
            show_search=True,
            show_category=True,
        )
        self.pcm_wave_number.valueChanged.connect(
            lambda v: self.send_midi_parameter(DigitalPartialParam.PCM_WAVE_NUMBER, v)
        )
        self.controls[DigitalPartialParam.PCM_WAVE_NUMBER] = self.pcm_wave_number

    def _create_pcm_group(self) -> QGroupBox:
        """Create PCM wave group"""
        pcm_group = QGroupBox("PCM Wave")
        pcm_layout = QGridLayout()
        pcm_group.setLayout(pcm_layout)
        pcm_layout.setColumnStretch(0, 1)  # left side stretches
        pcm_layout.addWidget(self.pcm_wave_gain, 0, 1)
        pcm_layout.addWidget(self.pcm_wave_number, 0, 2, 1, 3)  # Span 3 columns
        pcm_layout.setColumnStretch(5, 1)  # right side stretches
        return pcm_group

    # --- Waveform selection ---
    def _on_waveform_selected(self, waveform: DigitalOscWave):
        for btn in self.wave_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)

        selected_btn = self.wave_buttons.get(waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)

        self.send_midi_parameter(DigitalPartialParam.OSC_WAVE, waveform.value)
        self._update_waveform_controls_enabled_states(waveform)

    def _update_waveform_controls_enabled_states(self, waveform: DigitalOscWave):
        """Enable/disable controls declaratively based on waveform."""
        for attrs in self.WAVEFORM_ENABLE_RULES.values():
            for attr in attrs:
                getattr(self, attr).setEnabled(False)
        for attr in self.WAVEFORM_ENABLE_RULES.get(waveform, []):
            getattr(self, attr).setEnabled(True)

    def _initialise_control_states(self):
        """Initialise control states"""
        self._update_waveform_controls_enabled_states(DigitalOscWave.SAW)
