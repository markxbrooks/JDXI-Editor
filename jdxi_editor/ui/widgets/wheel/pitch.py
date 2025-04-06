from PySide6.QtWidgets import QWidget

from jdxi_editor.ui.widgets.wheel.wheel import WheelWidget


class PitchWheel(WheelWidget):
    """
    Modulation Wheel
    """

    def __init__(self, label="Pitch", bidirectional=True, parent=None):
        super().__init__(parent)
        self.bidirectional = bidirectional
        self.label = label
        self.parent = parent
        self.value = 0.0
