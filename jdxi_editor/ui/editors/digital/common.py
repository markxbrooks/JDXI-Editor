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

    PITCH_ROW_SLIDERS = [
        SliderSpec(DigitalCommonParam.PITCH_BEND_UP, DigitalDisplayName.PITCH_BEND_UP),
        SliderSpec(
            DigitalCommonParam.PITCH_BEND_DOWN, DigitalDisplayName.PITCH_BEND_DOWN
        ),
        SliderSpec(DigitalCommonParam.TONE_LEVEL, DigitalDisplayName.TONE_LEVEL),
        SliderSpec(
            DigitalCommonParam.PORTAMENTO_TIME, DigitalDisplayName.PORTAMENTO_TIME
        ),
        SliderSpec(DigitalCommonParam.ANALOG_FEEL, DigitalDisplayName.ANALOG_FEEL),
        SliderSpec(DigitalCommonParam.WAVE_SHAPE, DigitalDisplayName.WAVE_SHAPE),
    ]

    PITCH_BEND_ROW_SWITCHES = [
        SwitchSpec(
            DigitalCommonParam.PORTAMENTO_TIME,
            DigitalDisplayName.PORTAMENTO_TIME,
            DigitalDisplayOptions.PORTAMENTO_TIME,
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

    PORTAMENTO_ROW_SWITCHES = [
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

        self.portamento_row_widgets: list | None = None

        super().__init__(icon_type=IconType.GENERIC, analog=False)

        self.build_widgets()
        self.setup_ui()

    def build_widgets(self):
        """Build all widgets before layout."""
        self._create_switches()
        self._create_sliders()
        self._create_portamento_row_widgets()

    def setup_ui(self):
        """init ul"""
        layout = self.get_layout()
        octave_shift_switch_row = create_layout_with_widgets([self.octave_shift_switch])
        layout.addLayout(octave_shift_switch_row)
        mono_switch_row = create_layout_with_widgets([self.mono_switch])
        layout.addLayout(mono_switch_row)

        # --- Pitch Bend
        self.pitch_bend_row = create_layout_with_widgets(
            [
                self.pitch_bend_up,
                self.pitch_bend_down,
                self.tone_level,
                self.portamento_time,
                self.analog_feel,
                self.wave_shape,
            ]
        )
        layout.addLayout(self.pitch_bend_row)
        ring_row = create_layout_with_widgets([self.ring_switch])
        layout.addLayout(ring_row)
        unison_row = create_layout_with_widgets([self.unison_switch, self.unison_size])
        layout.addLayout(unison_row)

        portamento_row = create_layout_with_widgets(self.portamento_row_widgets)
        layout.addLayout(portamento_row)
        layout.addStretch()

    def _create_switches_in_progress(self):
        """Create slider widgets."""
        switches = {
            spec.param: self._create_parameter_switch(
                spec.param,
                spec.label,
                spec.options,
            )
            for spec in self.PORTAMENTO_ROW_SWITCHES
        }

        # --- Portamento row
        self.portamento_switch = switches[DigitalCommonParam.PORTAMENTO_SWITCH]
        self.portamento_mode = switches[DigitalCommonParam.PORTAMENTO_MODE]
        self.legato_switch = switches[DigitalCommonParam.LEGATO_SWITCH]

    def _create_sliders(self):
        """Create slider widgets."""
        sliders = {
            spec.param: self._create_parameter_slider(
                spec.param,
                spec.label,
                vertical=True,
            )
            for spec in self.PITCH_ROW_SLIDERS
        }

        # --- Explicit assignments (legible, grep-friendly)
        self.pitch_bend_up = sliders[DigitalCommonParam.PITCH_BEND_UP]
        self.pitch_bend_down = sliders[DigitalCommonParam.PITCH_BEND_DOWN]
        self.tone_level = sliders[DigitalCommonParam.TONE_LEVEL]
        self.portamento_time = sliders[DigitalCommonParam.PORTAMENTO_TIME]
        self.analog_feel = sliders[DigitalCommonParam.ANALOG_FEEL]
        self.wave_shape = sliders[DigitalCommonParam.WAVE_SHAPE]

    def _create_switches(self):
        # --- Octave Switch
        self.octave_shift_switch = self._create_parameter_combo_box(
            DigitalCommonParam.OCTAVE_SHIFT,
            DigitalDisplayName.OCTAVE_SHIFT,
            options=DigitalDisplayOptions.OCTAVE_SHIFT,
            values=[61, 62, 63, 64, 65, 66, 67],
        )
        # --- Mono Switch
        self.mono_switch = self._create_parameter_switch(
            DigitalCommonParam.MONO_SWITCH,
            DigitalDisplayName.MONO_SWITCH,
            DigitalDisplayOptions.MONO_SWITCH,
        )
        # --- Ring Modulator
        self.ring_switch = self._create_parameter_switch(
            DigitalCommonParam.RING_SWITCH,
            DigitalDisplayName.RING_SWITCH,
            DigitalDisplayOptions.RING_SWITCH,
        )
        # --- Unison Switch and Size
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

    def _create_portamento_row_widgets(self):
        # --- Portamento Switch
        self.portamento_switch = self._create_parameter_switch(
            DigitalCommonParam.PORTAMENTO_SWITCH,
            DigitalDisplayName.PORTAMENTO_SWITCH,
            DigitalDisplayOptions.PORTAMENTO_SWITCH,
        )
        # --- Portamento Mode and Legato
        self.portamento_mode = self._create_parameter_switch(
            DigitalCommonParam.PORTAMENTO_MODE,
            DigitalDisplayName.PORTAMENTO_MODE,
            DigitalDisplayOptions.PORTAMENTO_MODE,
        )
        self.legato_switch = self._create_parameter_switch(
            DigitalCommonParam.LEGATO_SWITCH,
            DigitalDisplayName.LEGATO_SWITCH,
            DigitalDisplayOptions.LEGATO_SWITCH,
        )
        self.portamento_row_widgets = [
            self.portamento_switch,
            self.portamento_mode,
            self.legato_switch,
        ]
