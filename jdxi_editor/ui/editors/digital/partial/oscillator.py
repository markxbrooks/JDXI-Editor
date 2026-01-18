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
from jdxi_editor.jdxi.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.digital.oscillator import DigitalOscWave
from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.option import DigitalDisplayOptions
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
from jdxi_editor.midi.data.pcm.waves import PCM_WAVES_CATEGORIZED
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.digital.partial.pwm import PWMWidget
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.widgets.button.waveform.waveform import WaveformButton
from jdxi_editor.ui.widgets.combo_box.searchable_filterable import (
    SearchableFilterableComboBox,
)
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.pitch.envelope import PitchEnvelopeWidget
from picomidi.sysex.parameter.address import AddressParameter


class DigitalOscillatorSection(SectionBaseWidget):
    """Digital Oscillator Section for the JDXI Editor"""

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable,
        create_parameter_combo_box: Callable,
        send_midi_parameter: Callable,
        partial_number: int,
        midi_helper: MidiIOHelper,
        controls: dict[AddressParameter, QWidget],
        address: RolandSysExAddress,
    ):
        self.pwm_widget = None
        self.partial_number = partial_number
        self.midi_helper = midi_helper
        self.controls = controls
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._create_parameter_combo_box = create_parameter_combo_box
        self.send_midi_parameter = send_midi_parameter
        self.address = address

        super().__init__(icon_type=IconType.OSCILLATOR, analog=False)
        self.setup_ui()
        log.parameter(f"initialization complete for", self)

    def setup_ui(self):
        """Setup the oscillator section UI."""
        layout = self.get_layout(margins=(1, 1, 1, 1))

        # --- Top row: Waveform buttons and variation switch ---
        layout.addLayout(self.create_waveform_buttons())

        # --- Create tab widget ---
        self.oscillator_tab_widget = QTabWidget()
        layout.addWidget(self.oscillator_tab_widget)

        # --- Tuning and Pitch tab (combines Tuning and Pitch Envelope like Analog) ---
        tuning_pitch_widget = self._create_tuning_pitch_widget()
        tuning_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.MUSIC_NOTE, color=JDXi.UI.Style.GREY
        )
        self.oscillator_tab_widget.addTab(
            tuning_pitch_widget, tuning_icon, "Tuning and Pitch"
        )

        # --- Pulse Width tab ---
        pw_group = self._create_pw_group()
        pw_icon = QIcon(
            base64_to_pixmap(generate_waveform_icon("square", "#FFFFFF", 1.0))
        )
        self.oscillator_tab_widget.addTab(pw_group, pw_icon, "Pulse Width")

        # --- PCM Wave tab (unique to Digital) ---
        pcm_group = self._create_pcm_group()
        pcm_icon = QIcon(
            base64_to_pixmap(generate_waveform_icon("pcm", "#FFFFFF", 1.0))
        )
        self.oscillator_tab_widget.addTab(pcm_group, pcm_icon, "PCM Wave")

        layout.addStretch()

        # --- Initialize states ---
        self._update_pw_controls_enabled_state(DigitalOscWave.SAW)
        self._update_pcm_controls_enabled_state(DigitalOscWave.PCM)
        self._update_supersaw_controls_enabled_state(DigitalOscWave.PCM)

    def create_waveform_buttons(self) -> QHBoxLayout:
        """Create waveform buttons layout"""
        top_row = QHBoxLayout()
        top_row.addStretch()
        wave_layout = QHBoxLayout()
        self.wave_buttons = {}

        wave_icons = {
            DigitalOscWave.SAW: generate_waveform_icon("upsaw", "#FFFFFF", 1.0),
            DigitalOscWave.SQUARE: generate_waveform_icon("square", "#FFFFFF", 1.0),
            DigitalOscWave.PW_SQUARE: generate_waveform_icon("pwsqu", "#FFFFFF", 1.0),
            DigitalOscWave.TRIANGLE: generate_waveform_icon("triangle", "#FFFFFF", 1.0),
            DigitalOscWave.SINE: generate_waveform_icon("sine", "#FFFFFF", 1.0),
            DigitalOscWave.NOISE: generate_waveform_icon("noise", "#FFFFFF", 1.0),
            DigitalOscWave.SUPER_SAW: generate_waveform_icon("spsaw", "#FFFFFF", 1.0),
            DigitalOscWave.PCM: generate_waveform_icon("pcm", "#FFFFFF", 1.0),
        }

        for wave, icon_base64 in wave_icons.items():
            btn = WaveformButton(wave)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)
            btn.setFixedSize(
                JDXi.UI.Dimensions.WAVEFORM_ICON.WIDTH,
                JDXi.UI.Dimensions.WAVEFORM_ICON.HEIGHT,
            )
            btn.setIcon(QIcon(base64_to_pixmap(icon_base64)))
            btn.clicked.connect(lambda checked, w=wave: self._on_waveform_selected(w))
            self.wave_buttons[wave] = btn
            self.controls[DigitalPartialParam.OSC_WAVE] = btn
            wave_layout.addWidget(btn)

        top_row.addLayout(wave_layout)
        self.wave_variation_switch = self._create_parameter_switch(
            DigitalPartialParam.OSC_WAVE_VARIATION,
            DigitalDisplayName.OSC_WAVE_VARIATION,
            DigitalDisplayOptions.OSC_WAVE_VARIATION,
        )
        top_row.addWidget(self.wave_variation_switch)
        top_row.addStretch()
        return top_row

    def _create_tuning_pitch_widget(self) -> QWidget:
        """Create tuning and pitch widget combining Tuning and Pitch Envelope"""
        pitch_layout = QHBoxLayout()
        pitch_layout.addStretch()
        pitch_layout.addWidget(self._create_tuning_group())
        pitch_layout.addWidget(self._create_pitch_env_group())
        pitch_layout.addStretch()
        pitch_widget = QWidget()
        pitch_widget.setLayout(pitch_layout)
        pitch_widget.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MINIMUM_HEIGHT)
        return pitch_widget

    def _create_tuning_group(self) -> QGroupBox:
        """Create tuning group"""
        tuning_group = QGroupBox("Tuning")
        tuning_layout = QHBoxLayout()
        tuning_layout.addStretch()
        tuning_group.setLayout(tuning_layout)
        tuning_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.OSC_PITCH,
                DigitalDisplayName.OSC_PITCH,
                vertical=True,
            )
        )
        tuning_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.OSC_DETUNE,
                DigitalDisplayName.OSC_DETUNE,
                vertical=True,
            )
        )
        self.super_saw_detune = self._create_parameter_slider(
            DigitalPartialParam.SUPER_SAW_DETUNE,
            DigitalDisplayName.SUPER_SAW_DETUNE,
            vertical=True,
        )
        tuning_layout.addWidget(self.super_saw_detune)
        tuning_layout.addStretch()
        JDXi.UI.ThemeManager.apply_adsr_style(tuning_group)
        return tuning_group

    def _create_pitch_env_group(self) -> QGroupBox:
        """Create pitch envelope group"""
        pitch_env_group = QGroupBox("Pitch Envelope")
        pitch_env_layout = QVBoxLayout()
        pitch_env_group.setLayout(pitch_env_layout)
        # --- Pitch Env Widget ---
        self.pitch_env_widget = PitchEnvelopeWidget(
            attack_param=DigitalPartialParam.OSC_PITCH_ENV_ATTACK_TIME,
            decay_param=DigitalPartialParam.OSC_PITCH_ENV_DECAY_TIME,
            depth_param=DigitalPartialParam.OSC_PITCH_ENV_DEPTH,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
        )
        JDXi.UI.ThemeManager.apply_adsr_style(self.pitch_env_widget)
        pitch_env_layout.addWidget(self.pitch_env_widget)
        return pitch_env_group

    def _create_pw_group(self) -> QGroupBox:
        """Create pulse width group"""
        pw_group = QGroupBox("Pulse Width")
        pw_layout = QVBoxLayout()
        pw_layout.addStretch()
        pw_group.setLayout(pw_layout)

        self.pw_shift_slider = self._create_parameter_slider(
            DigitalPartialParam.OSC_PULSE_WIDTH_SHIFT,
            DigitalDisplayName.OSC_PULSE_WIDTH_SHIFT,
            vertical=True,
        )
        JDXi.UI.ThemeManager.apply_adsr_style(self.pw_shift_slider)
        pwm_widget_layout = QHBoxLayout()
        pwm_widget_layout.addStretch()
        self.pwm_widget = PWMWidget(
            pulse_width_param=DigitalPartialParam.OSC_PULSE_WIDTH,
            mod_depth_param=DigitalPartialParam.OSC_PULSE_WIDTH_MOD_DEPTH,
            midi_helper=self.midi_helper,
            address=self.address,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
        )
        JDXi.UI.ThemeManager.apply_adsr_style(self.pwm_widget)
        self.pwm_widget.setMaximumHeight(JDXi.UI.Style.PWM_WIDGET_HEIGHT)
        pwm_widget_layout.addWidget(self.pwm_widget)
        pwm_widget_layout.addWidget(self.pw_shift_slider)
        pwm_widget_layout.addStretch()
        pw_layout.addLayout(pwm_widget_layout)
        pw_layout.addStretch()
        return pw_group

    def _create_pcm_group(self) -> QGroupBox:
        """Create PCM wave group"""
        pcm_group = QGroupBox("PCM Wave")
        pcm_layout = QGridLayout()
        pcm_group.setLayout(pcm_layout)
        self.pcm_wave_gain = self._create_parameter_combo_box(
            DigitalPartialParam.PCM_WAVE_GAIN,
            DigitalDisplayName.PCM_WAVE_GAIN,
            options=DigitalDisplayOptions.PCM_WAVE_GAIN,
        )

        # Create PCM wave options and values
        pcm_wave_options = [
            f"{w['Wave Number']}: {w['Wave Name']}" for w in PCM_WAVES_CATEGORIZED
        ]
        pcm_wave_values = [w["Wave Number"] for w in PCM_WAVES_CATEGORIZED]
        pcm_categories = sorted(set(w["Category"] for w in PCM_WAVES_CATEGORIZED))

        # Category filter function for PCM waves
        def pcm_category_filter(wave_name: str, category: str) -> bool:
            """Check if a wave name matches a category."""
            if not category:
                return True
            # Find the wave in PCM_WAVES_CATEGORIZED and check its category
            for wave in PCM_WAVES_CATEGORIZED:
                wave_display = f"{wave['Wave Number']}: {wave['Wave Name']}"
                if wave_display == wave_name:
                    return wave["Category"] == category
            return False

        # Create SearchableFilterableComboBox for PCM wave selection
        self.pcm_wave_number = SearchableFilterableComboBox(
            label=DigitalDisplayName.PCM_WAVE_NUMBER,
            options=pcm_wave_options,
            values=pcm_wave_values,
            categories=pcm_categories,
            category_filter_func=pcm_category_filter,
            show_label=True,
            show_search=True,
            show_category=True,
        )

        # Connect valueChanged signal to send MIDI parameter updates
        self.pcm_wave_number.valueChanged.connect(
            lambda v: self.send_midi_parameter(DigitalPartialParam.PCM_WAVE_NUMBER, v)
        )

        # Store in controls dict for consistency
        self.controls[DigitalPartialParam.PCM_WAVE_NUMBER] = self.pcm_wave_number

        pcm_layout.setColumnStretch(0, 1)  # left side stretches
        pcm_layout.addWidget(self.pcm_wave_gain, 0, 1)
        pcm_layout.addWidget(self.pcm_wave_number, 0, 2, 1, 3)  # Span 3 columns
        pcm_layout.setColumnStretch(5, 1)  # right side stretches
        return pcm_group

    def _on_waveform_selected(self, waveform: DigitalOscWave):
        """Handle waveform button clicks"""
        # --- Reset all buttons to default style ---
        for btn in self.wave_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)

        # --- Apply active style to the selected waveform button ---
        selected_btn = self.wave_buttons.get(waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)

        # --- Send MIDI message ---
        if not self.send_midi_parameter(DigitalPartialParam.OSC_WAVE, waveform.value):
            log.warning(f"Failed to set waveform to {waveform.name}")

        self._update_waveform_controls_enabled_states(waveform)

    def _update_waveform_controls_enabled_states(self, waveform: DigitalOscWave):
        """
        _update_waveform_controls_states

        :param waveform: DigitalOscWave
        :return: None

        Update control visibility and enabled state based on the selected waveform.
        """
        self._update_pw_controls_enabled_state(waveform)
        self._update_pcm_controls_enabled_state(waveform)
        self._update_supersaw_controls_enabled_state(waveform)

    def _update_pw_controls_enabled_state(self, waveform: DigitalOscWave):
        """Update pulse width controls enabled state based on waveform"""
        pw_enabled = waveform == DigitalOscWave.PW_SQUARE
        self.pwm_widget.setEnabled(pw_enabled)
        self.pw_shift_slider.setEnabled(pw_enabled)

    def _update_pcm_controls_enabled_state(self, waveform: DigitalOscWave):
        """Update PCM wave controls visibility based on waveform"""
        pcm_enabled = waveform == DigitalOscWave.PCM
        self.pcm_wave_gain.setEnabled(pcm_enabled)
        self.pcm_wave_number.setEnabled(pcm_enabled)

    def _update_supersaw_controls_enabled_state(self, waveform: DigitalOscWave):
        """Update supersaw controls visibility based on waveform"""
        supersaw_enabled = waveform == DigitalOscWave.SUPER_SAW
        self.super_saw_detune.setEnabled(supersaw_enabled)
