"""
Progress Dialog
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QProgressBar,
    QWidget,
    QApplication,
)

from jdxi_editor.jdxi.style import JDXiStyle


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
        self.label = QLabel(message)
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(JDXiStyle.PROGRESS_BAR)
        self.progress_bar.setMaximum(maximum)
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        QApplication.processEvents()
