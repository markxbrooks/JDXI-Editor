"""
Common Section
"""

from typing import Callable

from PySide6.QtWidgets import QHBoxLayout

from jdxi_editor.midi.data.parameter.digital.common import DigitalCommonParam
from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.option import DigitalDisplayOptions
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import create_layout_with_widgets
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget


class DigitalCommonSection(SectionBaseWidget):
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
        self.init_ui()

    def init_ui(self):
        layout = self.get_layout()

        # --- Octave Switch
        self.octave_shift_switch = self._create_parameter_combo_box(
            DigitalCommonParam.OCTAVE_SHIFT,
            DigitalDisplayName.OCTAVE_SHIFT,
            options=DigitalDisplayOptions.OCTAVE_SHIFT,
            values=[61, 62, 63, 64, 65, 66, 67],
        )
        octave_shift_switch_row = create_layout_with_widgets([self.octave_shift_switch])
        layout.addLayout(octave_shift_switch_row)

        # --- Mono Switch
        self.mono_switch = self._create_parameter_switch(
            DigitalCommonParam.MONO_SWITCH,
            DigitalDisplayName.MONO_SWITCH,
            DigitalDisplayOptions.MONO_SWITCH,
        )
        mono_switch_row = create_layout_with_widgets([self.mono_switch])
        layout.addLayout(mono_switch_row)

        # --- Pitch Bend
        self.pitch_bend_row = QHBoxLayout()
        self.pitch_bend_row.addStretch()
        self.pitch_bend_up = self._create_parameter_slider(
            DigitalCommonParam.PITCH_BEND_UP,
            DigitalDisplayName.PITCH_BEND_UP,
            vertical=True,
        )
        self.pitch_bend_down = self._create_parameter_slider(
            DigitalCommonParam.PITCH_BEND_DOWN,
            DigitalDisplayName.PITCH_BEND_DOWN,
            vertical=True,
        )
        self.tone_level = self._create_parameter_slider(
            DigitalCommonParam.TONE_LEVEL, DigitalDisplayName.TONE_LEVEL, vertical=True
        )
        self.portamento_time = self._create_parameter_slider(
            DigitalCommonParam.PORTAMENTO_TIME,
            DigitalDisplayName.PORTAMENTO_TIME,
            vertical=True,
        )
        # --- Analog Feel and Wave Shape
        self.analog_feel = self._create_parameter_slider(
            DigitalCommonParam.ANALOG_FEEL,
            DigitalDisplayName.ANALOG_FEEL,
            vertical=True,
        )
        self.wave_shape = self._create_parameter_slider(
            DigitalCommonParam.WAVE_SHAPE, DigitalDisplayName.WAVE_SHAPE, vertical=True
        )
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

        # --- Ring Modulator
        self.ring_switch = self._create_parameter_switch(
            DigitalCommonParam.RING_SWITCH,
            DigitalDisplayName.RING_SWITCH,
            DigitalDisplayOptions.RING_SWITCH,
        )
        ring_row = create_layout_with_widgets([self.ring_switch])
        layout.addLayout(ring_row)

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
        unison_row = create_layout_with_widgets([self.unison_switch, self.unison_size])
        layout.addLayout(unison_row)

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
        portamento_row = create_layout_with_widgets(
            [self.portamento_switch, self.legato_switch]
        )
        layout.addLayout(portamento_row)
        layout.addStretch()
