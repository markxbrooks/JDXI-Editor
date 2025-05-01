"""
Analog LFO Section
"""
from typing import Callable
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import QSize
import qtawesome as qta

from jdxi_editor.midi.data.parameter.analog import AddressParameterAnalog
from jdxi_editor.jdxi.style import JDXIStyle


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
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._create_parameter_combo_box = create_parameter_combo_box
        self._on_lfo_shape_changed = on_lfo_shape_changed
        self.lfo_shape_buttons = lfo_shape_buttons
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Shape row
        shape_row = QHBoxLayout()
        shape_row.addWidget(QLabel("Shape"))
        shape_row.addStretch(1)

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
            btn.setStyleSheet(JDXIStyle.BUTTON_RECT_ANALOG)
            btn.setIconSize(QSize(20, 20))
            btn.setFixedSize(60, 30)
            btn.setToolTip(name)
            btn.clicked.connect(lambda checked, v=value: self._on_lfo_shape_changed(v))
            self.lfo_shape_buttons[value] = btn
            shape_row.addWidget(btn)
            shape_row.addStretch(1)

        layout.addLayout(shape_row)

        # Rate and Fade Time
        self.lfo_rate = self._create_parameter_slider(AddressParameterAnalog.LFO_RATE, "Rate")
        self.lfo_fade = self._create_parameter_slider(
            AddressParameterAnalog.LFO_FADE_TIME, "Fade Time"
        )

        # Tempo Sync controls
        sync_row = QHBoxLayout()
        self.lfo_sync_switch = self._create_parameter_switch(
            AddressParameterAnalog.LFO_TEMPO_SYNC_SWITCH, "Tempo Sync", ["OFF", "ON"]
        )
        sync_row.addWidget(self.lfo_sync_switch)
        self.lfo_sync_note = self._create_parameter_combo_box(
            AddressParameterAnalog.LFO_TEMPO_SYNC_NOTE,
            "Sync Note",
            options=["1/1", "1/2", "1/4", "1/8", "1/16"],
        )
        sync_row.addWidget(self.lfo_sync_note)

        # Depth controls
        self.lfo_pitch = self._create_parameter_slider(
            AddressParameterAnalog.LFO_PITCH_DEPTH, "Pitch Depth"
        )
        self.lfo_filter = self._create_parameter_slider(
            AddressParameterAnalog.LFO_FILTER_DEPTH, "Filter Depth"
        )
        self.lfo_amp = self._create_parameter_slider(
            AddressParameterAnalog.LFO_AMP_DEPTH, "Amp Depth"
        )

        # Key Trigger switch
        self.key_trigger_switch = self._create_parameter_switch(
            AddressParameterAnalog.LFO_KEY_TRIGGER, "Key Trigger", ["OFF", "ON"]
        )

        # Add all controls to layout
        layout.addWidget(self.lfo_rate)
        layout.addWidget(self.lfo_fade)
        layout.addLayout(sync_row)
        layout.addWidget(self.lfo_pitch)
        layout.addWidget(self.lfo_filter)
        layout.addWidget(self.lfo_amp)
        layout.addWidget(self.key_trigger_switch)
        layout.addStretch()
