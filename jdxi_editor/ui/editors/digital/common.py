"""
Common Section
"""

from typing import Callable

from PySide6.QtWidgets import QHBoxLayout

from jdxi_editor.midi.data.parameter.digital.common import DigitalCommonParam
from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.option import DigitalDisplayOptions
from jdxi_editor.ui.editors.widget_specs import SliderSpec, SwitchSpec
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import create_layout_with_widgets
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget


class DigitalCommonSection(SectionBaseWidget):
    """Digital Common Section"""

    SLIDER_GROUPS = {
        "pitch": [
            SliderSpec(DigitalCommonParam.PITCH_BEND_UP, DigitalDisplayName.PITCH_BEND_UP),
            SliderSpec(DigitalCommonParam.PITCH_BEND_DOWN, DigitalDisplayName.PITCH_BEND_DOWN),
            SliderSpec(DigitalCommonParam.TONE_LEVEL, DigitalDisplayName.TONE_LEVEL),
            SliderSpec(DigitalCommonParam.PORTAMENTO_TIME, DigitalDisplayName.PORTAMENTO_TIME),
            SliderSpec(DigitalCommonParam.ANALOG_FEEL, DigitalDisplayName.ANALOG_FEEL),
            SliderSpec(DigitalCommonParam.WAVE_SHAPE, DigitalDisplayName.WAVE_SHAPE),
        ]
    }

    PORTAMENTO_SWITCHES = [
        SwitchSpec(
            DigitalCommonParam.PORTAMENTO_SWITCH,
            DigitalDisplayName.PORTAMENTO_SWITCH,
            DigitalDisplayOptions.PORTAMENTO_SWITCH,
        ),
        SwitchSpec(
            DigitalCommonParam.PORTAMENTO_MODE,
            DigitalDisplayName.PORTAMENTO_MODE,
            DigitalDisplayOptions.PORTAMENTO_MODE,
        ),
        SwitchSpec(
            DigitalCommonParam.LEGATO_SWITCH,
            DigitalDisplayName.LEGATO_SWITCH,
            DigitalDisplayOptions.LEGATO_SWITCH,
        ),
    ]

    def __init__(
            self,
            create_parameter_slider: Callable,
            create_parameter_switch: Callable,
            create_parameter_combo_box: Callable,
            controls: dict,
    ):
        """
        Initialize the DigitalCommonSection

        :param create_parameter_slider: Callable
        :param create_parameter_switch: Callable
        :param create_parameter_combo_box: Callable
        :param controls: dict
        """
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._create_parameter_combo_box = create_parameter_combo_box
        self.controls = controls

        super().__init__(icon_type=IconType.GENERIC, analog=False)

        self.build_widgets()
        self.setup_ui()

    def build_widgets(self) -> None:
        # --- Sliders
        (
            self.pitch_bend_up,
            self.pitch_bend_down,
            self.tone_level,
            self.portamento_time,
            self.analog_feel,
            self.wave_shape,
        ) = self._build_sliders(self.SLIDER_GROUPS["pitch"])

        # --- Portamento switches
        (
            self.portamento_switch,
            self.portamento_mode,
            self.legato_switch,
        ) = self._build_switches(self.PORTAMENTO_SWITCHES)

        # --- Other switches
        self.octave_shift_switch = self._create_parameter_combo_box(
            DigitalCommonParam.OCTAVE_SHIFT,
            DigitalDisplayName.OCTAVE_SHIFT,
            DigitalDisplayOptions.OCTAVE_SHIFT,
            values=[61, 62, 63, 64, 65, 66, 67],
        )

        self.mono_switch = self._create_parameter_switch(
            DigitalCommonParam.MONO_SWITCH,
            DigitalDisplayName.MONO_SWITCH,
            DigitalDisplayOptions.MONO_SWITCH,
        )

        self.ring_switch = self._create_parameter_switch(
            DigitalCommonParam.RING_SWITCH,
            DigitalDisplayName.RING_SWITCH,
            DigitalDisplayOptions.RING_SWITCH,
        )

        self.unison_switch = self._create_parameter_switch(
            DigitalCommonParam.UNISON_SWITCH,
            DigitalDisplayName.UNISON_SWITCH,
            DigitalDisplayOptions.UNISON_SWITCH,
        )

        self.unison_size = self._create_parameter_switch(
            DigitalCommonParam.UNISON_SIZE,
            DigitalDisplayName.UNISON_SIZE,
            DigitalDisplayOptions.UNISON_SIZE,
        )

    def setup_ui(self) -> None:
        layout = self.get_layout()

        layout.addLayout(create_layout_with_widgets([self.octave_shift_switch]))
        layout.addLayout(create_layout_with_widgets([self.mono_switch]))

        layout.addLayout(
            create_layout_with_widgets([
                self.pitch_bend_up,
                self.pitch_bend_down,
                self.tone_level,
                self.portamento_time,
                self.analog_feel,
                self.wave_shape,
            ])
        )

        layout.addLayout(create_layout_with_widgets([self.ring_switch]))
        layout.addLayout(create_layout_with_widgets([self.unison_switch, self.unison_size]))
        layout.addLayout(
            create_layout_with_widgets([
                self.portamento_switch,
                self.portamento_mode,
                self.legato_switch,
            ])
        )

        layout.addStretch()
