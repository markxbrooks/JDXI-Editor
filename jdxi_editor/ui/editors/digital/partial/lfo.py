"""
 LFO section of the digital partial editor.
"""
from typing import Callable

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from PySide6.QtCore import Qt
import qtawesome as qta

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.midi.data.parameter.digital.partial import (
    AddressParameterDigitalPartial,
)


class DigitalLFOSection(QWidget):
    """LFO section for the digital partial editor."""

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable,
        create_parameter_combo_box: Callable,
        controls: dict,
    ):
        super().__init__()
        """
        Initialize the DigitalLFOSection

        :param create_parameter_slider: Callable
        :param create_parameter_switch: Callable
        :param controls: dict
        """
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._create_parameter_combo_box = create_parameter_combo_box
        self.controls = controls
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI for the LFO section."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet(JDXiStyle.ADSR)

        # Icons row
        icons_hlayout = QHBoxLayout()
        for icon in [
            "mdi.triangle-wave",
            "mdi.sine-wave",
            "fa5s.wave-square",
            "mdi.cosine-wave",
            "mdi.triangle-wave",
            "mdi.waveform",
        ]:
            icon_label = QLabel()
            pixmap = qta.icon(icon, color="#666666").pixmap(30, 30)
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        layout.addLayout(icons_hlayout)

        # Shape and sync controls
        shape_row_layout = QHBoxLayout()
        shape_row_layout.addStretch()
        self.lfo_shape = self._create_parameter_switch(
            AddressParameterDigitalPartial.LFO_SHAPE,
            "Shape",
            ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"],
        )
        shape_row_layout.addWidget(self.lfo_shape)

        self.lfo_tempo_sync_switch = self._create_parameter_switch(
            AddressParameterDigitalPartial.LFO_TEMPO_SYNC_SWITCH,
            "Tempo Sync",
            ["OFF", "ON"],
        )
        shape_row_layout.addWidget(self.lfo_tempo_sync_switch)
        self.lfo_sync_note = self._create_parameter_combo_box(
            AddressParameterDigitalPartial.LFO_TEMPO_SYNC_NOTE,
            "Sync Note",
            options=["1/1", "1/2", "1/4", "1/8", "1/16"],
        )
        shape_row_layout.addWidget(self.lfo_sync_note)
        layout.addLayout(shape_row_layout)

        rate_fade_row_layout = QHBoxLayout()
        layout.addLayout(rate_fade_row_layout)
        rate_fade_row_layout.addStretch()
        # Rate and fade controls
        rate_fade_row_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.LFO_RATE, "Rate", vertical=True
            )
        )
        rate_fade_row_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.LFO_FADE_TIME, "Fade", vertical=True
            )
        )
        rate_fade_row_layout.addStretch()

        # Key trigger switch
        self.lfo_trigger = self._create_parameter_switch(
            AddressParameterDigitalPartial.LFO_KEY_TRIGGER, "Key Trigger", ["OFF", "ON"]
        )
        shape_row_layout.addWidget(self.lfo_trigger)
        shape_row_layout.addStretch()


        # Modulation depths
        depths_group = QGroupBox("Depths")
        depths_layout = QHBoxLayout()
        depths_layout.addStretch()
        depths_group.setLayout(depths_layout)

        depths_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.LFO_PITCH_DEPTH, "Pitch", vertical=True
            )
        )
        depths_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.LFO_FILTER_DEPTH, "Filter", vertical=True
            )
        )
        depths_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.LFO_AMP_DEPTH, "Amp", vertical=True
            )
        )
        depths_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.LFO_PAN_DEPTH, "Pan", vertical=True
            )
        )
        layout.addWidget(depths_group)
        depths_layout.addStretch()

        layout.addStretch()
