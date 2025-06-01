import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QSlider, QGroupBox
)
from PySide6.QtCore import Qt

from jdxi_editor.ui.widgets.pitch.pwm_plot import PWMPlot


class PWMWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PWM Widget")
        self.setGeometry(100, 100, 300, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Group box for PWM controls
        group_box = QGroupBox("PWM Controls")
        group_layout = QVBoxLayout()

        # Width slider
        self.width_label = QLabel("Width (% of cycle): 50")
        self.width_slider = QSlider(Qt.Vertical)
        self.width_slider.setRange(0, 100)
        self.width_slider.setValue(50)
        self.width_slider.valueChanged.connect(
            lambda val: self.width_label.setText(f"Width (% of cycle): {val}")
        )

        # Mod Depth slider
        self.mod_label = QLabel("Mod Depth (of LFO applied): 50")
        self.mod_slider = QSlider(Qt.Vertical)
        self.mod_slider.setRange(0, 100)
        self.mod_slider.setValue(50)
        self.mod_slider.valueChanged.connect(
            lambda val: self.mod_label.setText(f"Mod Depth (of LFO applied): {val}")
        )

        # Shift slider
        self.shift_label = QLabel("Shift (range of change): 50")
        self.shift_slider = QSlider(Qt.Vertical)
        self.shift_slider.setRange(0, 100)
        self.shift_slider.setValue(50)
        self.shift_slider.valueChanged.connect(
            lambda val: self.shift_label.setText(f"Shift (range of change): {val}")
        )

        # Add widgets to layout
        for label, slider in [
            (self.width_label, self.width_slider),
            (self.mod_label, self.mod_slider),
            (self.shift_label, self.shift_slider),
        ]:
            group_layout.addWidget(label)
            group_layout.addWidget(slider)
        self.plot = PWMPlot(width=300,
                            height=250,
                            parent=self)
        layout.addWidget(self.plot)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PWMWidget()
    window.show()
    sys.exit(app.exec_())
