"""
Analog Oscillator Section
"""

from typing import Callable, Dict, Union

from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QTabWidget, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.analog.oscillator import AnalogWaveOsc
from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.analog.helpers import (
    generate_analog_wave_button,
    generate_analog_waveform_icon_name,
)
from jdxi_editor.ui.editors.widget_specs import SliderSpec, SwitchSpec
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_group_with_widgets,
    create_layout_with_widgets,
    create_widget_with_layout,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.pitch.envelope import PitchEnvelopeWidget
from jdxi_editor.ui.widgets.pulse_width.pwm import PWMWidget


class AnalogOscillatorSection(SectionBaseWidget):
    """Analog Oscillator Section"""

    SLIDER_GROUPS = {
        "tuning": [
            SliderSpec(Analog.Param.OSC_PITCH_COARSE,
                       Analog.Display.Name.OSC_PITCH_COARSE,
                       vertical=True),
            SliderSpec(Analog.Param.OSC_PITCH_FINE,
                       Analog.Display.Name.OSC_PITCH_FINE,
                       vertical=True),
        ],
        "env": [
            SliderSpec(Analog.Param.OSC_PITCH_ENV_VELOCITY_SENSITIVITY,
                       Analog.Display.Name.OSC_PITCH_ENV_VELOCITY_SENSITIVITY,
                       vertical=True)
        ]
    }
    SWITCH_SPECS = [
        SwitchSpec(
            Analog.Param.SUB_OSCILLATOR_TYPE,
            Analog.Display.Name.SUB_OSCILLATOR_TYPE,
            Analog.Display.Options.SUB_OSCILLATOR_TYPE,
        ),
    ]

    def __init__(
            self,
            waveform_selected_callback: Callable,
            wave_buttons: dict,
            midi_helper: MidiIOHelper,
            controls: dict[AddressParameter, QWidget],
            address: RolandSysExAddress,
    ):
        """
        Initialize the AnalogOscillatorSection

        :param waveform_selected_callback: Callable
        :param wave_buttons: dict to store waveform buttons (waveform -> button mapping)
        :param midi_helper: MidiIOHelper
        :param address: RolandSysExAddress
        """
        self.pitch_env_widget: PitchEnvelopeWidget | None = None
        self.pwm_widget: PWMWidget | None = None
        self._on_waveform_selected = waveform_selected_callback
        self.waveform_buttons: dict = wave_buttons or {}
        self.midi_helper = midi_helper
        self.analog: bool = True

        super().__init__(icons_row_type=IconType.OSCILLATOR, analog=True, midi_helper=midi_helper)
        # --- Set attributes after super().__init__() to avoid them being overwritten
        self.controls: Dict[Union[Analog.Param], QWidget] = controls or {}
        self.address = address
        self.build_widgets()
        self.setup_ui()

    def build_widgets(self):
        """build widgets"""
        self._create_waveform_buttons()
        (
            self.osc_pitch_env_velocity_sensitivity_slider,
        ) = self._build_sliders(self.SLIDER_GROUPS["env"])
        # --- Only one switch, for Sub Oscillator Type
        (self.sub_oscillator_type_switch,) = self._build_switches(self.SWITCH_SPECS)
        # --- Tuning Group sliders
        (
            self.osc_pitch_coarse_slider,
            self.osc_pitch_fine_slider,
        ) = self._build_sliders(self.SLIDER_GROUPS["tuning"])
        self.tuning_sliders = [self.osc_pitch_coarse_slider,
                               self.osc_pitch_fine_slider]

        # --- PWM Widget ---
        self.pwm_widget = PWMWidget(
            pulse_width_param=Analog.Param.OSC_PULSE_WIDTH,
            mod_depth_param=Analog.Param.OSC_PULSE_WIDTH_MOD_DEPTH,
            midi_helper=self.midi_helper,
            address=self.address,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            analog=self.analog,
        )

        # --- Pitch Env Widget ---
        self.pitch_env_widget = PitchEnvelopeWidget(
            attack_param=Analog.Param.OSC_PITCH_ENV_ATTACK_TIME,
            decay_param=Analog.Param.OSC_PITCH_ENV_DECAY_TIME,
            depth_param=Analog.Param.OSC_PITCH_ENV_DEPTH,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
            analog=self.analog
        )
        # --- Create pitch_env_widgets list after pitch_env_widget is created
        self.pitch_env_widgets = [self.pitch_env_widget, self.osc_pitch_env_velocity_sensitivity_slider]
        # --- Finally create Tab widget with all of the above widgets
        self._create_tab_widget()

    def _create_tab_widget(self):
        """Tab widget with tuning group and pitch widget"""
        self.oscillator_tab_widget = QTabWidget()
        # --- Tuning tab (standardized name matching Digital) ---
        self.tuning_group = self._create_tuning_group()
        # --- Pitch tab (standardized name matching Digital) ---
        self.pitch_widget = self._create_tuning_pitch_widget()
        # --- Pulse Width tab ---
        self.pw_group = self._create_pw_group()

    def setup_ui(self) -> None:
        """
        Setup the UI (standardized method name matching Digital Oscillator)
        :return: None
        """
        layout = self.get_layout(margins=JDXi.UI.Dimensions.EDITOR_ANALOG.MARGINS)
        # --- Waveform buttons ---
        self.waveform_button_layout = self._create_wave_layout()
        layout.addLayout(self.waveform_button_layout)
        # --- Tab widget to add pitch and PW controls to ---
        JDXi.UI.Theme.apply_tabs_style(self.oscillator_tab_widget, analog=True)
        layout.addWidget(self.oscillator_tab_widget)
        self._add_tab(key=Analog.Wave.Tab.PITCH, widget=self.pitch_widget)
        self._add_tab(key=Analog.Wave.Tab.TUNING, widget=self.tuning_group)
        self._add_tab(key=Analog.Wave.Tab.PULSE_WIDTH, widget=self.pw_group)

        layout.addStretch()

    def _create_tuning_pitch_widget(self) -> QWidget:
        """Create tuning and pitch widget combining Tuning and Pitch Envelope (standardized name matching Digital)"""
        pitch_layout = create_layout_with_widgets(widgets=[self._create_pitch_env_group()])
        pitch_widget = create_widget_with_layout(pitch_layout)
        pitch_widget.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MINIMUM_HEIGHT)
        return pitch_widget

    def _create_wave_layout(self) -> QHBoxLayout:
        """
        Create the waveform buttons layout

        :return: QHBoxLayout
        """
        # --- Get buttons in order for layout
        waveform_buttons_list = list(self.waveform_buttons.values())
        waveform_buttons_list.append(self.sub_oscillator_type_switch)
        wave_layout = create_layout_with_widgets(waveform_buttons_list)
        return wave_layout

    def _create_waveform_buttons(self) -> None:
        """Create waveform buttons and store in dict"""
        for waveform in [
            Analog.Wave.Osc.SAW,
            Analog.Wave.Osc.TRIANGLE,
            Analog.Wave.Osc.PULSE,
        ]:
            icon_name = generate_analog_waveform_icon_name(waveform)
            btn = generate_analog_wave_button(icon_name, waveform)
            btn.waveform_selected.connect(self._on_waveform_selected)
            self.waveform_buttons[waveform] = btn
            self.controls[Analog.Param.OSC_WAVEFORM] = btn

    def _create_tuning_group(self) -> QGroupBox:
        """
        Create the tuning group (standardized private method matching Digital)

        :return: QGroupBox
        """
        tuning_group = create_group_with_widgets(label="Tuning",
                                                 widgets=self.tuning_sliders)
        return tuning_group

    def _create_pw_group(self) -> QGroupBox:
        """
        Create the pulse width group (standardized private method matching Digital)

        :return: QGroupBox
        """
        pw_group = create_group_with_widgets(label="Pulse Width",
                                             widgets=[self.pwm_widget])
        self.pwm_widget.setMaximumHeight(JDXi.UI.Style.PWM_WIDGET_HEIGHT)
        return pw_group

    def _create_pitch_env_group(self) -> QGroupBox:
        """
        Create the pitch envelope group (standardized private method matching Digital)

        :return: QGroupBox
        """
        # --- Pitch Envelope Group
        pitch_env_group = create_group_with_widgets(label="Pitch Envelope",
                                                    widgets=self.pitch_env_widgets)
        return pitch_env_group

    def _update_pw_controls_state(self, waveform: AnalogWaveOsc):
        """
        Update pulse width controls enabled state based on waveform

        :param waveform: AnalogOscWave value
        :return: None
        """
        pw_enabled = waveform == Analog.Wave.Osc.PULSE
        self.pwm_widget.setEnabled(pw_enabled)

    def _on_waveform_selected_local(self, waveform: AnalogWaveOsc):
        """
        Handle waveform button selection locally (for section-level handling)
        This is separate from the editor's callback to avoid conflicts.

        :param waveform: AnalogOscWave value
        :return: None
        """
        if self.midi_helper:
            sysex_message = self.sysex_composer.compose_message(
                address=self.address,
                param=Analog.Param.OSC_WAVEFORM,
                value=waveform.value,
            )
            self.midi_helper.send_midi_message(sysex_message)

            # --- Reset all buttons to default style
            for btn in self.waveform_buttons.values():
                btn.setChecked(False)
                JDXi.UI.Theme.apply_button_rect_analog(btn)

            # --- Apply active style to the selected waveform button
            selected_btn = self.waveform_buttons.get(waveform)
            if selected_btn:
                selected_btn.setChecked(True)
                JDXi.UI.Theme.apply_button_analog_active(selected_btn)
            self._update_pw_controls_state(waveform)

