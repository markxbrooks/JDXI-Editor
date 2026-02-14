from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSlider, QVBoxLayout, QWidget


class DrumLevelStrip(QWidget):
    STRIP_WIDTH = 46

    def __init__(self, label, param_index):
        super().__init__()

        self.setFixedWidth(self.STRIP_WIDTH)

        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(2, 2, 2, 2)

        self.name = QLabel(label)
        self.name.setAlignment(Qt.AlignHCenter)

        self.slider = QSlider(Qt.Vertical)
        self.slider.setMinimumHeight(140)

        self.value = QLabel("0")
        self.value.setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.name)
        layout.addWidget(self.slider, 1)
        layout.addWidget(self.value)


class MasterLevelStrip(DrumLevelStrip):
    def __init__(self):
        super().__init__("KIT", 0)
        self.name.setText("MASTER")
