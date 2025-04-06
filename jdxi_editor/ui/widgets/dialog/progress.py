from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QApplication


class ProgressDialog(QDialog):
    def __init__(self, title="Loading", message="Please wait...", maximum=100, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        layout = QVBoxLayout()
        self.label = QLabel(message)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(maximum)
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        QApplication.processEvents()