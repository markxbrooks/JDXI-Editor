from PySide6.QtWidgets import QWidget

from jdxi_editor.ui.widgets.wheel.wheel import WheelWidget


class ModWheel(WheelWidget):
    """
    Modulation Wheel
    """

    def __init__(self, label="Mod", bidirectional=True, parent=None):
        super().__init__(parent)
        self.label = label
        self.bidirectional = bidirectional
        self.parent = parent
        self.value = 0.0
