"""
Common Section
"""
from typing import Callable

from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.ui.editors.widget_specs import SliderSpec, SwitchSpec, ComboBoxSpec
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import create_layout_with_widgets
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget


class DigitalCommonSection(SectionBaseWidget):
    """Digital Common Section"""

    SLIDER_GROUPS = {
        "pitch": [
            SliderSpec(Digital.Common.PITCH_BEND_UP, Digital.Display.Name.PITCH_BEND_UP),
            SliderSpec(Digital.Common.PITCH_BEND_DOWN, Digital.Display.Name.PITCH_BEND_DOWN),
            SliderSpec(Digital.Common.TONE_LEVEL, Digital.Display.Name.TONE_LEVEL),
            SliderSpec(Digital.Common.PORTAMENTO_TIME, Digital.Display.Name.PORTAMENTO_TIME),
            SliderSpec(Digital.Common.ANALOG_FEEL, Digital.Display.Name.ANALOG_FEEL),
            SliderSpec(Digital.Common.WAVE_SHAPE, Digital.Display.Name.WAVE_SHAPE),
        ]
    }

    PORTAMENTO_SWITCHES = [
        SwitchSpec(
            Digital.Common.PORTAMENTO_SWITCH,
            Digital.Display.Name.PORTAMENTO_SWITCH,
            Digital.Display.Options.PORTAMENTO_SWITCH,
        ),
        SwitchSpec(
            Digital.Common.PORTAMENTO_MODE,
            Digital.Display.Name.PORTAMENTO_MODE,
            Digital.Display.Options.PORTAMENTO_MODE,
        ),
        SwitchSpec(
            Digital.Common.LEGATO_SWITCH,
            Digital.Display.Name.LEGATO_SWITCH,
            Digital.Display.Options.LEGATO_SWITCH,
        ),
        ]
    COMBO_BOXES = [
        ComboBoxSpec(
            Digital.Common.OCTAVE_SHIFT,
            Digital.Display.Name.OCTAVE_SHIFT,
            Digital.Display.Options.OCTAVE_SHIFT,
            [61, 62, 63, 64, 65, 66, 67]
        ),
        ]
    OTHER_SWITCHES = [
        SwitchSpec(
            Digital.Common.MONO_SWITCH,
            Digital.Display.Name.MONO_SWITCH,
            Digital.Display.Options.MONO_SWITCH,
        ),
        SwitchSpec(
            Digital.Common.RING_SWITCH,
            Digital.Display.Name.RING_SWITCH,
            Digital.Display.Options.RING_SWITCH,
        ),
        SwitchSpec(
            Digital.Common.UNISON_SWITCH,
            Digital.Display.Name.UNISON_SWITCH,
            Digital.Display.Options.UNISON_SWITCH,
        ),
        SwitchSpec(
            Digital.Common.UNISON_SIZE,
            Digital.Display.Name.UNISON_SIZE,
            Digital.Display.Options.UNISON_SIZE,
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

        super().__init__(icons_row_type=IconType.GENERIC, analog=False)

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

        (self.octave_shift_switch,) = self._build_combo_boxes(self.COMBO_BOXES)
        # --- Other switches
        (
         self.mono_switch,
         self.ring_switch,
         self.unison_switch,
         self.unison_size)\
            = self._build_switches(self.OTHER_SWITCHES)

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
