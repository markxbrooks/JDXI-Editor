"""
ADSR Widget
Editing ADSR parameters
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QLabel, QSpinBox, QDoubleSpinBox, QGridLayout
from .ADSRPlot import ADSRPlot  # Assuming ADSRPlot is a separate module


class ADSRWidget(QWidget):
    """A widget for controlling and displaying an ADSR envelope.

    This widget allows users to adjust the attack, decay, sustain, and release
    parameters of an ADSR envelope through spin boxes and displays the envelope
    graphically using an ADSRPlot.

    Attributes:
        envelope (dict): A dictionary containing the ADSR envelope parameters.
        attackSB (QSpinBox): Spin box for adjusting the attack time.
        decaySB (QSpinBox): Spin box for adjusting the decay time.
        releaseSB (QSpinBox): Spin box for adjusting the release time.
        initialSB (QDoubleSpinBox): Spin box for adjusting the initial amplitude.
        peakSB (QDoubleSpinBox): Spin box for adjusting the peak amplitude.
        sustainSB (QDoubleSpinBox): Spin box for adjusting the sustain amplitude.
        plot (ADSRPlot): Widget for displaying the ADSR envelope graphically.
    """

    envelopeChanged = Signal(dict)

    def __init__(self, parent=None):
        """Initialize the ADSRWidget with default envelope parameters."""
        super().__init__(parent)
        self.envelope = {
            "attackTime": 100,
            "decayTime": 400,
            "releaseTime": 100,
            "initialAmpl": 0,
            "peakAmpl": 1,
            "sustainAmpl": 0.8,
        }

        # Create labels
        attackLabel = QLabel("Attack:")
        decayLabel = QLabel("Decay:")
        releaseLabel = QLabel("Release:")
        initialLabel = QLabel("  Initial:")
        peakLabel = QLabel("  Peak:")
        sustainLabel = QLabel("  Sustain:")

        # Create spin boxes
        self.attackSB = QSpinBox()
        self.attackSB.setRange(0, 1000)
        self.attackSB.setSuffix(" ms")
        self.attackSB.setValue(self.envelope["attackTime"])

        self.decaySB = QSpinBox()
        self.decaySB.setRange(0, 1000)
        self.decaySB.setSuffix(" ms")
        self.decaySB.setValue(self.envelope["decayTime"])

        self.releaseSB = QSpinBox()
        self.releaseSB.setRange(0, 1000)
        self.releaseSB.setSuffix(" ms")
        self.releaseSB.setValue(self.envelope["releaseTime"])

        self.initialSB = QDoubleSpinBox()
        self.initialSB.setRange(0, 1)
        self.initialSB.setSingleStep(0.01)
        self.initialSB.setValue(self.envelope["initialAmpl"])

        self.peakSB = QDoubleSpinBox()
        self.peakSB.setRange(0, 1)
        self.peakSB.setSingleStep(0.01)
        self.peakSB.setValue(self.envelope["peakAmpl"])

        self.sustainSB = QDoubleSpinBox()
        self.sustainSB.setRange(0, 1)
        self.sustainSB.setSingleStep(0.01)
        self.sustainSB.setValue(self.envelope["sustainAmpl"])

        # Create layout
        self.gridLayout = QGridLayout(self)
        self.gridLayout.addWidget(attackLabel, 0, 0)
        self.gridLayout.addWidget(self.attackSB, 0, 1)
        self.gridLayout.addWidget(decayLabel, 1, 0)
        self.gridLayout.addWidget(self.decaySB, 1, 1)
        self.gridLayout.addWidget(releaseLabel, 2, 0)
        self.gridLayout.addWidget(self.releaseSB, 2, 1)
        self.gridLayout.addWidget(initialLabel, 0, 2)
        self.gridLayout.addWidget(self.initialSB, 0, 3)
        self.gridLayout.addWidget(peakLabel, 1, 2)
        self.gridLayout.addWidget(self.peakSB, 1, 3)
        self.gridLayout.addWidget(sustainLabel, 2, 2)
        self.gridLayout.addWidget(self.sustainSB, 2, 3)

        # Create and add plot
        self.plot = ADSRPlot()
        self.gridLayout.addWidget(self.plot, 0, 4, 4, 1)
        self.gridLayout.setColumnMinimumWidth(4, 150)

        # Connect signals
        self.attackSB.valueChanged.connect(self.valueChangedInt)
        self.decaySB.valueChanged.connect(self.valueChangedInt)
        self.releaseSB.valueChanged.connect(self.valueChangedInt)
        self.initialSB.valueChanged.connect(self.valueChangedDouble)
        self.peakSB.valueChanged.connect(self.valueChangedDouble)
        self.sustainSB.valueChanged.connect(self.valueChangedDouble)

        # Initialize plot with current envelope values
        self.plot.setValues(self.envelope)

    def valueChangedInt(self, val):
        """Update envelope parameters and emit signal when integer values change."""
        self.envelope["attackTime"] = self.attackSB.value()
        self.envelope["decayTime"] = self.decaySB.value()
        self.envelope["releaseTime"] = self.releaseSB.value()
        self.envelope["initialAmpl"] = self.initialSB.value()
        self.envelope["peakAmpl"] = self.peakSB.value()
        self.envelope["sustainAmpl"] = self.sustainSB.value()
        self.plot.setValues(self.envelope)
        self.envelopeChanged.emit(self.envelope)

    def valueChangedDouble(self, val):
        """Update envelope parameters and emit signal when double values change."""
        self.valueChangedInt(0)

    def on_adsr_envelope_changed(self, envelope):
        """Handle changes to the ADSR envelope."""
        # Example: Send MIDI messages to update the synth's ADSR parameters
        print(f"ADSR Envelope changed: {envelope}")
        # You can send MIDI messages here to update the synth's parameters
