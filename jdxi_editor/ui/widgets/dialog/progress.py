"""
Progress Dialog
"""

from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.widgets.display.digital import DigitalTitle


class ProgressDialog(QDialog):
    def __init__(
        self,
        title: str = "Loading",
        message: str = "Please wait...",
        maximum: int = 100,
        parent: QWidget = None,
    ):
        super().__init__(parent)
        """Initialize the ProgressDialog

        :param title: str
        :param message: str
        :param maximum: int
        :param parent: QWidget
        """
        self.setWindowTitle(title)
        self.setModal(True)
        layout = QVBoxLayout()
        self.label = DigitalTitle(message)
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(JDXi.UI.Style.PROGRESS_BAR)
        self.progress_bar.setMaximum(maximum)
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        QApplication.processEvents()
