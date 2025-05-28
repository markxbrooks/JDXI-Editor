"""
Common Section
"""

from typing import Callable

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
import qtawesome as qta

from jdxi_editor.midi.data.parameter.analog import AddressParameterAnalog


class AnalogCommonSection(QWidget):
    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable,
        create_parameter_combo_box: Callable,
        controls: dict,
    ):
        super().__init__()
        """
        Initialize the AnalogCommonSection
        :param create_parameter_slider: Callable
        :param create_parameter_switch: Callable
        :param create_parameter_combo_box: Callable
        :param controls: dict
        """
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._create_parameter_combo_box = create_parameter_combo_box
        self.controls = controls
        self.init_ui()

    def init_ui(self):
        """
        init ui
        """
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Icons
        icons_hlayout = QHBoxLayout()
        for icon_name in [
            "ph.bell-ringing-bold",
            "mdi.call-merge",
            "mdi.account-voice",
            "ri.voiceprint-fill",
            "mdi.piano",
        ]:
            icon_label = QLabel()
            icon = qta.icon(icon_name, color="#666666")
            pixmap = icon.pixmap(24, 24)  # Using fixed icon size
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        layout.addLayout(icons_hlayout)

        # Mono Switch
        self.octave_shift_switch = self._create_parameter_combo_box(
            AddressParameterAnalog.OCTAVE_SHIFT,
            "Octave shift",
            ["-3", "-2", "-1", "0", "+1", "+2", "+3"],
            [61, 62, 63, 64, 65, 66, 67],
        )
        octave_shift_switch_row = QHBoxLayout()
        octave_shift_switch_row.addWidget(self.octave_shift_switch)
        layout.addLayout(octave_shift_switch_row)

        """
        #Mono Switch
        self.mono_switch = self._create_parameter_switch(
            AddressParameterAnalog.MONO_SWITCH, "Mono", ["OFF", "ON"]
        )
        mono_switch_row = QHBoxLayout()
        mono_switch_row.addWidget(self.mono_switch)
        layout.addLayout(mono_switch_row)
        """
        # Pitch Bend
        self.pitch_bend_row = QHBoxLayout()
        self.pitch_bend_up = self._create_parameter_slider(
            AddressParameterAnalog.PITCH_BEND_UP, "Pitch Bend Up"
        )
        self.pitch_bend_down = self._create_parameter_slider(
            AddressParameterAnalog.PITCH_BEND_DOWN, "Pitch Bend Down"
        )
        self.pitch_bend_row.addWidget(self.pitch_bend_up)
        self.pitch_bend_row.addWidget(self.pitch_bend_down)
        layout.addLayout(self.pitch_bend_row)

        """
        # Tone Level
        #self.tone_level_row = QHBoxLayout()
        self.tone_level = self._create_parameter_slider(
            AddressParameterAnalog.TONE_LEVEL, "Tone Level"
        )
        self.tone_level_row.addWidget(self.tone_level)
        layout.addLayout(self.tone_level_row)
        
        # Ring Modulator
        self.ring_switch = self._create_parameter_switch(
            AddressParameterAnalog.RING_SWITCH, "Ring", ["OFF", "---", "ON"]
        )
        ring_row = QHBoxLayout()
        ring_row.addWidget(self.ring_switch)
        layout.addLayout(ring_row)

        # Unison Switch and Size
        self.unison_switch = self._create_parameter_switch(
            AddressParameterAnalog.UNISON_SWITCH, "Unison", ["OFF", "ON"]
        )
        self.unison_size = self._create_parameter_switch(
            AddressParameterAnalog.UNISON_SIZE,
            "Size",
            ["2 VOICE", "3 VOICE", "4 VOICE", "5 VOICE"],
        )
        unison_row = QHBoxLayout()
        unison_row.addWidget(self.unison_switch)
        unison_row.addWidget(self.unison_size)
        layout.addLayout(unison_row)
        """

        # Portamento Switch
        self.portamento_switch = self._create_parameter_switch(
            AddressParameterAnalog.PORTAMENTO_SWITCH, "Portamento", ["OFF", "ON"]
        )
        portamento_row = QHBoxLayout()
        portamento_row.addWidget(self.portamento_switch)
        layout.addLayout(portamento_row)

        # Portamento Time
        self.portamento_time = self._create_parameter_slider(
            AddressParameterAnalog.PORTAMENTO_TIME, "Portamento Time"
        )
        portamento_time_row = QHBoxLayout()
        portamento_time_row.addWidget(self.portamento_time)
        layout.addLayout(portamento_time_row)
        """
        # Portamento Mode and Legato
        self.portamento_mode = self._create_parameter_switch(
            AddressParameterAnalog.PORTAMENTO_MODE,
            "Portamento Mode",
            ["NORMAL", "LEGATO"],
        )
        self.legato_switch = self._create_parameter_switch(
            AddressParameterAnalog.LEGATO_SWITCH, "Legato", ["OFF", "ON"]
        )
        legato_row = QHBoxLayout()
        legato_row.addWidget(self.legato_switch)
        layout.addLayout(legato_row)

        # Analog Feel and Wave Shape
        self.analog_feel = self._create_parameter_slider(
            AddressParameterAnalog.ANALOG_FEEL, "Analog Feel"
        )
        self.wave_shape = self._create_parameter_slider(
            AddressParameterAnalog.WAVE_SHAPE, "Wave Shape"
        )
        layout.addWidget(self.analog_feel)
        layout.addWidget(self.wave_shape)
        """
        self.legato_switch = self._create_parameter_switch(
            AddressParameterAnalog.LEGATO_SWITCH, "Legato", ["OFF", "ON"]
        )
        legato_row = QHBoxLayout()
        legato_row.addWidget(self.legato_switch)
        layout.addLayout(legato_row)

        layout.addStretch()
