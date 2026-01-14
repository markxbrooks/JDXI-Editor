"""
Common Section
"""

from typing import Callable

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from jdxi_editor.jdxi.style import JDXiStyle, JDXiThemeManager
from jdxi_editor.midi.data.parameter.digital.common import DigitalCommonParam
from jdxi_editor.ui.editors.synth.simple import create_hrow_layout
from jdxi_editor.ui.widgets.editor.section_base import IconType, SectionBaseWidget


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
            "Octave shift",
            ["-3", "-2", "-1", "0", "+1", "+2", "+3"],
            [61, 62, 63, 64, 65, 66, 67],
        )
        octave_shift_switch_row = create_hrow_layout([self.octave_shift_switch])
        layout.addLayout(octave_shift_switch_row)

        # --- Mono Switch
        self.mono_switch = self._create_parameter_switch(
            DigitalCommonParam.MONO_SWITCH, "Mono", ["OFF", "ON"]
        )
        mono_switch_row = create_hrow_layout([self.mono_switch])
        layout.addLayout(mono_switch_row)

        # --- Pitch Bend
        self.pitch_bend_row = QHBoxLayout()
        self.pitch_bend_row.addStretch()
        self.pitch_bend_up = self._create_parameter_slider(
            DigitalCommonParam.PITCH_BEND_UP, "Pitch Bend Up", vertical=True
        )
        self.pitch_bend_down = self._create_parameter_slider(
            DigitalCommonParam.PITCH_BEND_DOWN, "Pitch Bend Down", vertical=True
        )
        self.tone_level = self._create_parameter_slider(
            DigitalCommonParam.TONE_LEVEL, "Tone Level", vertical=True
        )
        self.portamento_time = self._create_parameter_slider(
            DigitalCommonParam.PORTAMENTO_TIME, "Portamento Time", vertical=True
        )
        # --- Analog Feel and Wave Shape
        self.analog_feel = self._create_parameter_slider(
            DigitalCommonParam.ANALOG_FEEL, "Analog Feel", vertical=True
        )
        self.wave_shape = self._create_parameter_slider(
            DigitalCommonParam.WAVE_SHAPE, "Wave Shape", vertical=True
        )
        self.pitch_bend_row = create_hrow_layout([self.pitch_bend_up,
                                                       self.pitch_bend_down,
                                                       self.tone_level,
                                                       self.portamento_time,
                                                       self.analog_feel,
                                                       self.wave_shape])
        layout.addLayout(self.pitch_bend_row)

        # --- Ring Modulator
        self.ring_switch = self._create_parameter_switch(
            DigitalCommonParam.RING_SWITCH, "Ring", ["OFF", "---", "ON"]
        )
        ring_row = create_hrow_layout([self.ring_switch])
        layout.addLayout(ring_row)

        # --- Unison Switch and Size
        self.unison_switch = self._create_parameter_switch(
            DigitalCommonParam.UNISON_SWITCH, "Unison", ["OFF", "ON"]
        )
        self.unison_size = self._create_parameter_switch(
            DigitalCommonParam.UNISON_SIZE,
            "Size",
            ["2 VOICE", "3 VOICE", "4 VOICE", "5 VOICE"],
        )
        unison_row = create_hrow_layout([self.unison_switch,
                                              self.unison_size])
        layout.addLayout(unison_row)

        # --- Portamento Switch
        self.portamento_switch = self._create_parameter_switch(
            DigitalCommonParam.PORTAMENTO_SWITCH, "Portamento", ["OFF", "ON"]
        )
        # --- Portamento Mode and Legato
        self.portamento_mode = self._create_parameter_switch(
            DigitalCommonParam.PORTAMENTO_MODE,
            "Portamento Mode",
            ["NORMAL", "LEGATO"],
        )
        self.legato_switch = self._create_parameter_switch(
            DigitalCommonParam.LEGATO_SWITCH, "Legato", ["OFF", "ON"]
        )
        portamento_row = create_hrow_layout([self.portamento_switch,
                                                  self.legato_switch])
        layout.addLayout(portamento_row)
        layout.addStretch()
