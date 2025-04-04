from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from PySide6.QtCore import Qt
import qtawesome as qta

from jdxi_editor.midi.data.constants.digital import DIGITAL_SYNTH_1_AREA
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParameter
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
#from jdxi_editor.midi.data.parameter.analog import DigiParameter
from jdxi_editor.ui.style import Style
from jdxi_editor.ui.widgets.adsr.adsr import ADSR


class DigitalLFOSection(QWidget):
    def __init__(self, create_parameter_slider, create_parameter_switch, controls, parent=None):
        super().__init__()
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self.controls = controls
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

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
        top_row = QHBoxLayout()
        self.lfo_shape = self._create_parameter_switch(DigitalPartialParameter.LFO_SHAPE,
                                                       "Shape",
                                                       ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"])
        top_row.addWidget(self.lfo_shape)

        self.lfo_tempo_sync_switch = self._create_parameter_switch(DigitalPartialParameter.LFO_TEMPO_SYNC_SWITCH,
                                                                   "Tempo Sync",
                                                                   ["OFF", "ON"])
        top_row.addWidget(self.lfo_tempo_sync_switch)
        layout.addLayout(top_row)

        # Rate and fade controls
        layout.addWidget(self._create_parameter_slider(DigitalPartialParameter.LFO_RATE,
                                                       "Rate"))
        layout.addWidget(self._create_parameter_slider(DigitalPartialParameter.LFO_FADE_TIME,
                                                       "Fade"))

        # Key trigger switch
        self.lfo_trigger = self._create_parameter_switch(DigitalPartialParameter.LFO_KEY_TRIGGER,
                                                         "Key Trigger",
                                                         ["OFF", "ON"])
        layout.addWidget(self.lfo_trigger)

        # Modulation depths
        depths_group = QGroupBox("Depths")
        depths_layout = QVBoxLayout()
        depths_group.setLayout(depths_layout)

        depths_layout.addWidget(self._create_parameter_slider(DigitalPartialParameter.LFO_PITCH_DEPTH, "Pitch"))
        depths_layout.addWidget(self._create_parameter_slider(DigitalPartialParameter.LFO_FILTER_DEPTH, "Filter"))
        depths_layout.addWidget(self._create_parameter_slider(DigitalPartialParameter.LFO_AMP_DEPTH, "Amp"))
        depths_layout.addWidget(self._create_parameter_slider(DigitalPartialParameter.LFO_PAN_DEPTH, "Pan"))
        layout.addWidget(depths_group)

        layout.addStretch()
