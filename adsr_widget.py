import sys
import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QGridLayout,
    QVBoxLayout,
    QPushButton,
)
from matplotlib.backends.backend_qtagg import FigureCanvas


class ADSRPlot(QWidget):
    def __init__(self):
        super().__init__()
        self.envelope = {
            "attackTime": 100,
            "decayTime": 400,
            "releaseTime": 100,
            "initialAmpl": 0,
            "peakAmpl": 1,
            "sustainAmpl": 0.8,
        }
        self.figure, self.ax = plt.subplots()
        plt.style.use("dark_background")
        self.canvas = FigureCanvas(self.figure)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        self.plot_envelope()

    def plot_envelope(self):
        attack_time = self.envelope["attackTime"] / 1000
        decay_time = self.envelope["decayTime"] / 1000
        release_time = self.envelope["releaseTime"] / 1000
        sustain_amplitude = self.envelope["sustainAmpl"]
        peak_amplitude = self.envelope["peakAmpl"]
        initial_amplitude = self.envelope["initialAmpl"]

        attack_samples = int(attack_time * 44100)
        decay_samples = int(decay_time * 44100)
        sustain_samples = int(44100 * 2)  # Sustain for 2 seconds
        release_samples = int(release_time * 44100)

        envelope = np.concatenate(
            [
                np.linspace(initial_amplitude, peak_amplitude, attack_samples),
                np.linspace(peak_amplitude, sustain_amplitude, decay_samples),
                np.full(sustain_samples, sustain_amplitude),
                np.linspace(sustain_amplitude, 0, release_samples),
            ]
        )

        time = np.linspace(0, len(envelope) / 44100, len(envelope))

        self.ax.clear()
        self.ax.plot(time, envelope)
        self.ax.set_xlabel("Time [s]")
        self.ax.set_ylabel("Amplitude")
        self.ax.set_title("ADSR Envelope")
        self.canvas.draw()

    def set_values(self, envelope):
        self.envelope = envelope
        self.plot_envelope()


class ADSRWidget(QWidget):
    envelopeChanged = Signal(dict)

    def __init__(self):
        super().__init__()
        self.envelope = {
            "attackTime": 100,
            "decayTime": 400,
            "releaseTime": 100,
            "initialAmpl": 0,
            "peakAmpl": 1,
            "sustainAmpl": 0.8,
        }
        self.attackSB = self.create_spinbox(0, 1000, " ms", self.envelope["attackTime"])
        self.decaySB = self.create_spinbox(0, 1000, " ms", self.envelope["decayTime"])
        self.releaseSB = self.create_spinbox(
            0, 1000, " ms", self.envelope["releaseTime"]
        )
        self.initialSB = self.create_double_spinbox(
            0, 1, 0.01, self.envelope["initialAmpl"]
        )
        self.peakSB = self.create_double_spinbox(0, 1, 0.01, self.envelope["peakAmpl"])
        self.sustainSB = self.create_double_spinbox(
            0, 1, 0.01, self.envelope["sustainAmpl"]
        )

        self.plot = ADSRPlot()

        self.layout = QGridLayout(self)
        self.layout.addWidget(QLabel("Attack:"), 0, 0)
        self.layout.addWidget(self.attackSB, 0, 1)
        self.layout.addWidget(QLabel("Decay:"), 1, 0)
        self.layout.addWidget(self.decaySB, 1, 1)
        self.layout.addWidget(QLabel("Release:"), 2, 0)
        self.layout.addWidget(self.releaseSB, 2, 1)
        self.layout.addWidget(QLabel("Initial:"), 0, 2)
        self.layout.addWidget(self.initialSB, 0, 3)
        self.layout.addWidget(QLabel("Peak:"), 1, 2)
        self.layout.addWidget(self.peakSB, 1, 3)
        self.layout.addWidget(QLabel("Sustain:"), 2, 2)
        self.layout.addWidget(self.sustainSB, 2, 3)
        self.layout.addWidget(self.plot, 0, 4, 4, 1)
        self.layout.setColumnMinimumWidth(4, 150)

        self.attackSB.valueChanged.connect(self.valueChanged)
        self.decaySB.valueChanged.connect(self.valueChanged)
        self.releaseSB.valueChanged.connect(self.valueChanged)
        self.initialSB.valueChanged.connect(self.valueChanged)
        self.peakSB.valueChanged.connect(self.valueChanged)
        self.sustainSB.valueChanged.connect(self.valueChanged)

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
        self.envelope["attackTime"] = self.attackSB.value()
        self.envelope["decayTime"] = self.decaySB.value()
        self.envelope["releaseTime"] = self.releaseSB.value()
        self.envelope["initialAmpl"] = self.initialSB.value()
        self.envelope["peakAmpl"] = self.peakSB.value()
        self.envelope["sustainAmpl"] = self.sustainSB.value()
        self.plot.set_values(self.envelope)
        self.envelopeChanged.emit(self.envelope)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ADSRWidget()
    window.setWindowTitle("ADSR Envelope Editor")
    window.show()
    sys.exit(app.exec())
