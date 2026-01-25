"""
Digital Oscillator Section for the JDXI Editor
"""

from typing import Callable

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.base.oscillator import BaseOscillatorSection
from jdxi_editor.ui.editors.widget_specs import SliderSpec
from jdxi_editor.ui.image.waveform import generate_icon_from_waveform
from jdxi_editor.ui.widgets.combo_box import SearchableFilterableComboBox
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_envelope_group,
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.pitch.envelope import PitchEnvelopeWidget
from jdxi_editor.ui.widgets.pulse_width.pwm import PWMWidget


class DigitalOscillatorSection(BaseOscillatorSection):
    """Digital Oscillator Section for JD-Xi Editor (spec-driven)."""

    # --- Sliders
    PARAM_SPECS = [
        SliderSpec(param=Digital.Param.OSC_PITCH, label=Digital.Display.Name.OSC_PITCH),
        SliderSpec(
            param=Digital.Param.OSC_DETUNE, label=Digital.Display.Name.OSC_DETUNE
        ),
        SliderSpec(
            param=Digital.Param.SUPER_SAW_DETUNE,
            label=Digital.Display.Name.SUPER_SAW_DETUNE,
        ),
    ]

    # --- Waveform buttons
    BUTTON_SPECS = [
        SliderSpec(
            param=Digital.Wave.Osc.SAW,
            label=Digital.Wave.WaveType.UPSAW,
            icon_name=Digital.Wave.WaveType.UPSAW,
        ),
        SliderSpec(
            param=Digital.Wave.Osc.SQUARE,
            label=Digital.Wave.WaveType.SQUARE,
            icon_name=Digital.Wave.WaveType.SQUARE,
        ),
        SliderSpec(
            param=Digital.Wave.Osc.PW_SQUARE,
            label=Digital.Wave.WaveType.PWSQU,
            icon_name=Digital.Wave.WaveType.PWSQU,
        ),
        SliderSpec(
            param=Digital.Wave.Osc.TRIANGLE,
            label=Digital.Wave.WaveType.TRIANGLE,
            icon_name=Digital.Wave.WaveType.TRIANGLE,
        ),
        SliderSpec(
            param=Digital.Wave.Osc.SINE,
            label=Digital.Wave.WaveType.SINE,
            icon_name=Digital.Wave.WaveType.SINE,
        ),
        SliderSpec(
            param=Digital.Wave.Osc.NOISE,
            label=Digital.Wave.WaveType.NOISE,
            icon_name=Digital.Wave.WaveType.NOISE,
        ),
        SliderSpec(
            param=Digital.Wave.Osc.SUPER_SAW,
            label=Digital.Wave.WaveType.SPSAW,
            icon_name=Digital.Wave.WaveType.SPSAW,
        ),
        SliderSpec(
            param=Digital.Wave.Osc.PCM,
            label=Digital.Wave.WaveType.PCM,
            icon_name=Digital.Wave.WaveType.PCM,
        ),
    ]

    # --- Enable rules for dependent widgets
    BUTTON_ENABLE_RULES = {
        Digital.Wave.Osc.PW_SQUARE: ["pwm_widget", "pw_shift_slider"],
        Digital.Wave.Osc.PCM: ["pwm_widget", "pcm_wave_gain", "pcm_wave_number"],
        Digital.Wave.Osc.SUPER_SAW: ["super_saw_detune"],
    }

    # --- Optional ADSR can be added if Oscillator has one (Digital usually has pitch envelope)
    ADSR_SPEC = None

    def __init__(
        self,
        icons_row_type: str = IconType.ADSR,
        analog: bool = False,
        send_midi_parameter: Callable = None,
        midi_helper: MidiIOHelper = None,
        controls: dict = None,
        address: RolandSysExAddress = None,
    ):
        super().__init__(
            send_midi_parameter=send_midi_parameter,
            midi_helper=midi_helper,
            controls=controls,
            address=address,
            icons_row_type=icons_row_type,
            analog=analog,
        )

    def build_widgets(self):
        """Override to create PitchEnvelopeWidget and PWMWidget"""
        # Create PitchEnvelopeWidget for pitch envelope (Attack, Decay, Depth)
        self.pitch_env_widget = PitchEnvelopeWidget(
            attack_param=Digital.Param.OSC_PITCH_ENV_ATTACK_TIME,
            decay_param=Digital.Param.OSC_PITCH_ENV_DECAY_TIME,
            depth_param=Digital.Param.OSC_PITCH_ENV_DEPTH,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
        )
        # Store pitch envelope controls
        self.controls[Digital.Param.OSC_PITCH_ENV_ATTACK_TIME] = (
            self.pitch_env_widget.attack_control
        )
        self.controls[Digital.Param.OSC_PITCH_ENV_DECAY_TIME] = (
            self.pitch_env_widget.decay_control
        )
        self.controls[Digital.Param.OSC_PITCH_ENV_DEPTH] = (
            self.pitch_env_widget.depth_control
        )

        # Create PWMWidget for pulse width modulation
        self.pwm_widget = PWMWidget(
            pulse_width_param=Digital.Param.OSC_PULSE_WIDTH,
            mod_depth_param=Digital.Param.OSC_PULSE_WIDTH_MOD_DEPTH,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
        )
        # Store PWM controls
        self.controls[Digital.Param.OSC_PULSE_WIDTH] = (
            self.pwm_widget.pulse_width_control
        )
        self.controls[Digital.Param.OSC_PULSE_WIDTH_MOD_DEPTH] = (
            self.pwm_widget.mod_depth_control
        )

        # Call parent to create other widgets from PARAM_SPECS
        super().build_widgets()

        # Create PCM Wave controls (Gain and Number) after parent builds widgets
        # These will be added to a separate "PCM" tab, not the Controls tab
        # PCM Wave Gain: combo box with -6, 0, +6, +12 dB options
        self.pcm_wave_gain = self._create_parameter_combo_box(
            Digital.Param.PCM_WAVE_GAIN,
            Digital.Display.Name.PCM_WAVE_GAIN,
            options=Digital.Display.Options.PCM_WAVE_GAIN,
            values=[0, 1, 2, 3],  # MIDI values for -6, 0, +6, +12 dB
        )
        self.controls[Digital.Param.PCM_WAVE_GAIN] = self.pcm_wave_gain
        # Don't add to control_widgets - it will be in the PCM tab

        # PCM Wave Number: SearchableFilterableComboBox with categorized PCM waves
        from jdxi_editor.midi.data.pcm.waves import PCM_WAVES_CATEGORIZED

        # Build options, values, and categories from PCM_WAVES_CATEGORIZED
        pcm_options = [
            f"{w['Wave Number']:03d}: {w['Wave Name']}" for w in PCM_WAVES_CATEGORIZED
        ]
        pcm_values = [w["Wave Number"] for w in PCM_WAVES_CATEGORIZED]
        pcm_categories = sorted(
            set(w["Category"] for w in PCM_WAVES_CATEGORIZED if w["Category"] != "None")
        )

        # Category filter function
        def pcm_category_filter(wave_name: str, category: str) -> bool:
            """Check if a PCM wave matches a category."""
            if not category:
                return True
            # Find the wave in PCM_WAVES_CATEGORIZED and check its category
            wave_num_str = wave_name.split(":")[0].strip()
            try:
                wave_num = int(wave_num_str)
                for w in PCM_WAVES_CATEGORIZED:
                    if w["Wave Number"] == wave_num:
                        return w["Category"] == category
            except ValueError:
                pass
            return False

        self.pcm_wave_number = SearchableFilterableComboBox(
            label=Digital.Display.Name.PCM_WAVE_NUMBER,
            options=pcm_options,
            values=pcm_values,
            categories=pcm_categories,
            category_filter_func=pcm_category_filter,
            show_label=True,
            show_search=True,
            show_category=True,
            show_bank=False,
            search_placeholder="Search PCM waves...",
            category_label="Category:",
        )
        # Connect to MIDI parameter sending
        if self.send_midi_parameter:
            self.pcm_wave_number.valueChanged.connect(
                lambda v: self.send_midi_parameter(Digital.Param.PCM_WAVE_NUMBER, v)
            )
        self.controls[Digital.Param.PCM_WAVE_NUMBER] = self.pcm_wave_number
        # Don't add to control_widgets - it will be in the PCM tab

    def _create_tab_widget(self):
        """Override to add PitchEnvelopeWidget and PWMWidget as tabs"""

        self.tab_widget = QTabWidget()

        from jdxi_editor.midi.data.parameter.digital.spec import DigitalOscillatorTab
        
        # Controls tab
        controls_widget = QWidget()
        controls_layout = create_layout_with_widgets(self.control_widgets)
        controls_widget.setLayout(controls_layout)
        self._add_tab(key=DigitalOscillatorTab.CONTROLS, widget=controls_widget)

        from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
        from jdxi_editor.ui.widgets.editor.helper import create_group_from_definition
        
        # Pulse Width tab
        if hasattr(self, "pwm_widget") and self.pwm_widget:
            pw_layout = QVBoxLayout()
            pw_layout.addStretch()
            self.pwm_widget.setMaximumHeight(JDXi.UI.Style.PWM_WIDGET_HEIGHT)
            pw_layout.addWidget(self.pwm_widget)
            pw_layout.addStretch()
            pw_group = create_group_from_definition(
                key=Digital.GroupBox.PULSE_WIDTH,
                layout_or_widget=pw_layout,
                set_attr=self,
            )
            self._add_tab(key=DigitalOscillatorTab.PULSE_WIDTH, widget=pw_group)

        # --- Pitch Envelope tab
        if hasattr(self, "pitch_env_widget") and self.pitch_env_widget:
            pitch_env_layout = create_layout_with_widgets(widget_list=[self.pitch_env_widget], vertical=False)
            pitch_env_group = create_group_from_definition(
                key=Digital.GroupBox.PITCH_ENVELOPE,
                layout_or_widget=pitch_env_layout,
                set_attr=self,
            )
            pitch_env_group.setProperty("adsr", True)
            self._add_tab(key=DigitalOscillatorTab.PITCH_ENV, widget=pitch_env_group)

        # --- PCM tab
        if hasattr(self, "pcm_wave_gain") and hasattr(self, "pcm_wave_number"):
            pcm_layout = create_layout_with_widgets(widget_list=[self.pcm_wave_gain, self.pcm_wave_number], vertical=True)
            pcm_group = create_group_from_definition(
                key=Digital.GroupBox.PCM_WAVE,
                layout_or_widget=pcm_layout,
                set_attr=self,
            )
            self._add_tab(key=DigitalOscillatorTab.PCM, widget=pcm_group)

        # --- ADSR tab (if any)
        if self.adsr_widget:
            adsr_group = create_envelope_group(
                "Envelope", adsr_widget=self.adsr_widget, analog=self.analog
            )
            self._add_tab(key=DigitalOscillatorTab.ADSR, widget=adsr_group)

    def _initialize_button_states(self):
        """Override to skip initialization until after all widgets are created"""
        # Don't initialize button states during __init__ - widgets may not exist yet
        # This will be called manually after all widgets are created
        pass

    def setup_ui(self):
        """Override to create UI with button row layout and initialize button states"""
        layout = self.get_layout()

        # Add button row layout if buttons exist
        if self.button_widgets:
            button_layout = self._create_button_row_layout()
            if button_layout is not None:
                layout.addLayout(button_layout)

        # Create and add tab widget
        self._create_tab_widget()
        if self.tab_widget:
            layout.addWidget(self.tab_widget)

        layout.addStretch()

        # Now that all widgets are created, initialize button states
        if self.BUTTON_SPECS:
            first_param = self.BUTTON_SPECS[0].param
            self._on_button_selected(first_param)

    def _create_waveform_buttons(self):
        """Override to create waveform buttons with custom icon generation"""
        self.waveform_buttons = {}
        self.wave_layout_widgets = []

        for spec in self.BUTTON_SPECS:
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
                JDXi.UI.Dimensions.WAVEFORM_ICON.WIDTH,
                JDXi.UI.Dimensions.WAVEFORM_ICON.HEIGHT,
            )
            btn.clicked.connect(lambda _, w=wave: self._on_button_selected(w))
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)

            self.waveform_buttons[wave] = btn
            self.button_widgets[wave] = btn
            self.controls[Digital.Param.OSC_WAVE] = btn
            self.wave_layout_widgets.append(btn)

    def _create_button_row_layout(self):
        """Override to create waveform button row layout"""

        # --- Create wave variation combo box
        self.wave_variation = self._create_parameter_combo_box(
            Digital.Param.OSC_WAVE_VARIATION,
            Digital.Display.Name.OSC_WAVE_VARIATION,
            options=Digital.Display.Options.OSC_WAVE_VARIATION,
            values=[0, 1, 2],  # A, B, C
        )
        self.controls[Digital.Param.OSC_WAVE_VARIATION] = self.wave_variation

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addLayout(create_layout_with_widgets(self.wave_layout_widgets))
        button_row.addWidget(self.wave_variation)  # Add wave variation switch
        button_row.addStretch()
        return button_row

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

        # --- Send MIDI parameter - button_param is a Digital.Wave.Osc enum
        if self.send_midi_parameter:
            self.send_midi_parameter(Digital.Param.OSC_WAVE, button_param.value)

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
