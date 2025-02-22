"""
ADSR Widget
Editing ADSR parameters
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QLabel, QSpinBox, QDoubleSpinBox, QGridLayout, QHBoxLayout

from jdxi_manager.ui.widgets.adsr.plot import ADSRPlot
from jdxi_manager.ui.style import Style


class ADSRWidget(QWidget):
    envelopeChanged = Signal(dict)

    def __init__(self):
        super().__init__()
        self.envelope = {
            "attack_time": 100,
            "decay_time": 400,
            "release_time": 100,
            "initial_level": 0,
            "peak_level": 1,
            "sustain_level": 0.8,
        }
        self.setMinimumHeight(150)  # Adjust height as needed
        self.attack_sb = self.create_spinbox(
            0, 1000, " ms", self.envelope["attack_time"]
        )
        self.decay_sb = self.create_spinbox(0, 1000, " ms", self.envelope["decay_time"])
        self.release_sb = self.create_spinbox(
            0, 1000, " ms", self.envelope["release_time"]
        )
        #self.initial_sb = self.create_double_spinbox(
        #    0, 1, 0.01, self.envelope["initial_level"]
        #)
        # self.peak_sb = self.create_double_spinbox(0, 1, 0.01, self.envelope["peak_level"])
        self.sustain_sb = self.create_double_spinbox(
            0, 1, 0.01, self.envelope["sustain_level"]
        )
        self.setStyleSheet(Style.EDITOR_STYLE)
        self.plot = ADSRPlot()

        self.sliders = QWidget()
        self.sliders_layout = QHBoxLayout(self.sliders)
        self.layout = QGridLayout(self)

        # self.layout.addWidget(QLabel("Attack:"), 0, 0)
        # self.layout.addWidget(self.attack_sb, 0, 1)
        # self.layout.addWidget(QLabel("Decay:"), 1, 0)
        # self.layout.addWidget(self.decay_sb, 1, 1)
        # self.layout.addWidget(QLabel("Release:"), 2, 0)
        # self.layout.addWidget(self.release_sb, 2, 1)
        # self.layout.addWidget(QLabel("Initial:"), 0, 2)
        # self.layout.addWidget(self.initial_sb, 0, 3)
        # self.layout.addWidget(QLabel("Peak:"), 1, 2)
        # self.layout.addWidget(self.peak_sb, 1, 3)
        # self.layout.addWidget(QLabel("Sustain:"), 2, 2)
        # self.layout.addWidget(self.sustain_sb, 2, 3)

        self.layout.addWidget(self.attack_sb, 0, 0)
        self.layout.addWidget(self.decay_sb, 0, 1)
        self.layout.addWidget(self.release_sb, 0, 2)
        self.layout.addWidget(self.sustain_sb, 0, 3)

        # self.layout.addWidget(self.plot, 3, 4, 4, 1)
        self.layout.addLayout(self.sliders_layout, 1, 0, 4, 3)
        self.layout.addWidget(self.plot, 0, 4, 4, 1)

        self.layout.setColumnMinimumWidth(4, 150)

        self.attack_sb.valueChanged.connect(self.valueChanged)
        self.decay_sb.valueChanged.connect(self.valueChanged)
        self.release_sb.valueChanged.connect(self.valueChanged)
        # self.initial_sb.valueChanged.connect(self.valueChanged)
        # self.peak_sb.valueChanged.connect(self.valueChanged)
        self.sustain_sb.valueChanged.connect(self.valueChanged)

        self.setLayout(self.layout)
        self.plot.set_values(self.envelope)

    def create_spinbox(self, min_value, max_value, suffix, value):
        sb = QSpinBox()
        sb.setRange(min_value, max_value)
        sb.setSuffix(suffix)
        sb.setValue(value)
        return sb

    def create_double_spinbox(self, min_value, max_value, step, value):
        sb = QDoubleSpinBox()
        sb.setRange(min_value, max_value)
        sb.setSingleStep(step)
        sb.setValue(value)
        return sb

    def valueChanged(self):
        self.envelope["attack_time"] = self.attack_sb.value()
        self.envelope["decay_time"] = self.decay_sb.value()
        self.envelope["release_time"] = self.release_sb.value()
        # self.envelope["initial_level"] = self.initial_sb.value()
        # self.envelope["peak_level"] = self.peak_sb.value()
        self.envelope["sustain_level"] = self.sustain_sb.value()
        self.plot.set_values(self.envelope)
        self.envelopeChanged.emit(self.envelope)


