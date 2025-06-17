"""
Analog LFO Section
"""


from typing import Callable
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import QSize
import qtawesome as qta

from jdxi_editor.midi.data.parameter.analog import AddressParameterAnalog
from jdxi_editor.jdxi.style import JDXiStyle


class AnalogLFOSection(QWidget):
    """Analog LFO Section"""

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable,
        create_parameter_combo_box: Callable,
        on_lfo_shape_changed: Callable,
        lfo_shape_buttons: dict,
    ):
        super().__init__()
        """
        Initialize the AnalogLFOSection

        :param create_parameter_slider: Callable
        :param create_parameter_switch: Callable
        :param create_parameter_combo_box: Callable
        :param on_lfo_shape_changed: Callable
        :param lfo_shape_buttons: dict
        """
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._create_parameter_combo_box = create_parameter_combo_box
        self._on_lfo_shape_changed = on_lfo_shape_changed
        self.lfo_shape_buttons = lfo_shape_buttons
        self.setStyleSheet(JDXiStyle.ADSR_ANALOG)
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI"""
        main_rows_vlayout = QVBoxLayout()
        self.setLayout(main_rows_vlayout)

        # Shape row
        shape_row_layout = QHBoxLayout()
        shape_row_layout.addStretch()
        shape_row_layout.addWidget(QLabel("Shape"))
        lfo_shapes = [
            ("TRI", "mdi.triangle-wave", 0),
            ("SIN", "mdi.sine-wave", 1),
            ("SAW", "mdi.sawtooth-wave", 2),
            ("SQR", "mdi.square-wave", 3),
            ("S&H", "mdi.waveform", 4),
            ("RND", "mdi.wave", 5),
        ]

        for name, icon_name, value in lfo_shapes:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setProperty("value", value)
            btn.setIcon(qta.icon(icon_name, color="#FFFFFF", icon_size=0.7))
            btn.setStyleSheet(JDXiStyle.BUTTON_RECT_ANALOG)
            btn.setIconSize(QSize(20, 20))
            btn.setFixedSize(60, 30)
            btn.setToolTip(name)
            btn.clicked.connect(lambda checked, v=value: self._on_lfo_shape_changed(v))
            self.lfo_shape_buttons[value] = btn
            shape_row_layout.addWidget(btn)
            shape_row_layout.addStretch()

        main_rows_vlayout.addLayout(shape_row_layout)

        # Tempo Sync controls
        sync_row_layout = QHBoxLayout()
        sync_row_layout.addStretch()
        self.lfo_sync_switch = self._create_parameter_switch(
            AddressParameterAnalog.LFO_TEMPO_SYNC_SWITCH, "Tempo Sync", ["OFF", "ON"]
        )
        sync_row_layout.addWidget(self.lfo_sync_switch)
        self.lfo_sync_note = self._create_parameter_combo_box(
            AddressParameterAnalog.LFO_TEMPO_SYNC_NOTE,
            "Sync Note",
            options=["1/1", "1/2", "1/4", "1/8", "1/16"],
        )
        sync_row_layout.addWidget(self.lfo_sync_note)
        # Key Trigger switch
        self.key_trigger_switch = self._create_parameter_switch(
            AddressParameterAnalog.LFO_KEY_TRIGGER, "Key Trigger", ["OFF", "ON"]
        )
        sync_row_layout.addWidget(self.key_trigger_switch)
        sync_row_layout.addStretch()

        main_rows_vlayout.addLayout(sync_row_layout)

        # Rate and Fade Time
        self.lfo_rate = self._create_parameter_slider(
            AddressParameterAnalog.LFO_RATE, "Rate", vertical=True
        )
        self.lfo_rate_modulation = self._create_parameter_slider(
            AddressParameterAnalog.LFO_RATE_MODULATION_CONTROL, "Rate Modulation", vertical=True
        )
        self.lfo_fade = self._create_parameter_slider(
            AddressParameterAnalog.LFO_FADE_TIME, "Fade Time", vertical=True
        )

        fade_rate_controls_row_layout = QHBoxLayout()
        depth_controls_row_layout = QHBoxLayout()

        main_rows_vlayout.addLayout(fade_rate_controls_row_layout)
        main_rows_vlayout.addLayout(depth_controls_row_layout)

        # Depth controls
        self.lfo_pitch = self._create_parameter_slider(
            AddressParameterAnalog.LFO_PITCH_DEPTH, "Pitch Depth", vertical=True
        )
        self.lfo_pitch_modulation = self._create_parameter_slider(
            AddressParameterAnalog.LFO_PITCH_MODULATION_CONTROL, "Pitch Modulation", vertical=True
        )
        self.lfo_filter = self._create_parameter_slider(
            AddressParameterAnalog.LFO_FILTER_DEPTH, "Filter Depth", vertical=True
        )
        self.lfo_filter_modulation = self._create_parameter_slider(
            AddressParameterAnalog.LFO_FILTER_MODULATION_CONTROL, "Filter Modulation", vertical=True
        )
        self.lfo_amp = self._create_parameter_slider(
            AddressParameterAnalog.LFO_AMP_DEPTH, "Amp Depth", vertical=True
        )
        self.lfo_amp_modulation = self._create_parameter_slider(
            AddressParameterAnalog.LFO_AMP_MODULATION_CONTROL, "AMP Modulation", vertical=True
        )
        # Add all controls to layout
        fade_rate_controls_row_layout.addStretch()
        fade_rate_controls_row_layout.addWidget(self.lfo_rate)
        fade_rate_controls_row_layout.addWidget(self.lfo_rate_modulation)
        fade_rate_controls_row_layout.addWidget(self.lfo_fade)
        fade_rate_controls_row_layout.addStretch()

        depth_controls_row_layout.addStretch()
        depth_controls_row_layout.addWidget(self.lfo_pitch)
        depth_controls_row_layout.addWidget(self.lfo_pitch_modulation)
        depth_controls_row_layout.addWidget(self.lfo_filter)
        depth_controls_row_layout.addWidget(self.lfo_filter_modulation)
        depth_controls_row_layout.addWidget(self.lfo_amp)
        depth_controls_row_layout.addWidget(self.lfo_amp_modulation)
        depth_controls_row_layout.addStretch()

        main_rows_vlayout.addStretch()
