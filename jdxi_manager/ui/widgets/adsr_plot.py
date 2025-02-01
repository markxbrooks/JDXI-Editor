"""
ADSR Plot
==========

This module defines the `ADSRPlot` class, a QWidget subclass that visualizes an ADSR (Attack,
Decay, Sustain, Release) envelope using Matplotlib. The plot displays the envelope's progression
over time, with adjustable parameters for attack, decay, sustain, and release times, as well as
initial, peak, and sustain amplitudes.

The plot is rendered in a QWidget, and the background and text colors are customized for better
visibility, with the envelope plotted in orange on a dark gray background.

Classes:
--------
- `ADSRPlot`: A QWidget subclass that generates and displays an ADSR envelope plot.

Methods:
--------
- `__init__(self)`: Initializes the widget and sets up the figure and layout for the plot.
- `plot_envelope(self)`: Generates and plots the ADSR envelope based on the current envelope parameters.
- `set_values(self, envelope)`: Updates the envelope parameters and refreshes the plot.

Customization:
-------------
- The plot background is dark gray (`#333333`), with all plot elements (ticks, labels, title) in
  orange for better visibility against the dark background.
- The time is represented in seconds, and the amplitude in a range from 0 to 1.
"""


import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


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

        # Set font globally
        plt.rcParams["font.family"] = "Consolas"

        # Create the figure and axis
        self.figure, self.ax = plt.subplots(figsize=(4, 4))
        self.ax.set_facecolor("#333333")  # Dark gray background
        self.figure.patch.set_facecolor("#333333")  # Background color for the figure

        # Create canvas and layout
        self.canvas = FigureCanvas(self.figure)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

        # Plot the envelope
        self.plot_envelope()

    def plot_envelope(self):
        """ Draw matplotlib plot in JDXI style"""
        self.ax.clear()  # Clear previous plot
        self.ax.set_facecolor("#333333")  # Ensure background stays dark gray

        # Adjust tick and label colors for visibility
        self.ax.tick_params(axis="both", colors="orange")
        self.ax.xaxis.label.set_color("orange")
        self.ax.yaxis.label.set_color("orange")
        self.ax.title.set_color("orange")

        # Extract envelope parameters
        attack_time = self.envelope["attackTime"] / 1000
        decay_time = self.envelope["decayTime"] / 1000
        release_time = self.envelope["releaseTime"] / 1000
        sustain_amplitude = self.envelope["sustainAmpl"]
        peak_amplitude = self.envelope["peakAmpl"]
        initial_amplitude = self.envelope["initialAmpl"]

        # Convert to samples (assuming a 44.1 kHz sample rate)
        attack_samples = int(attack_time * 44100)
        decay_samples = int(decay_time * 44100)
        sustain_samples = int(44100 * 2)  # Sustain for 2 seconds
        release_samples = int(release_time * 44100)

        # Construct ADSR envelope
        envelope = np.concatenate([
            np.linspace(initial_amplitude, peak_amplitude, attack_samples),
            np.linspace(peak_amplitude, sustain_amplitude, decay_samples),
            np.full(sustain_samples, sustain_amplitude),
            np.linspace(sustain_amplitude, 0, release_samples)
        ])

        time = np.linspace(0, len(envelope) / 44100, len(envelope))

        # Plot envelope with orange color
        self.ax.plot(time, envelope, color="orange", linewidth=2)
        self.ax.set_xlabel("Time [s]")
        self.ax.set_ylabel("Amplitude")
        self.ax.set_title("ADSR Envelope")

        self.canvas.draw()

    def set_values(self, envelope):
        """Update envelope values and refresh the plot."""
        self.envelope = envelope
        self.plot_envelope()
