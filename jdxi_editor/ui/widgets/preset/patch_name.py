from PySide6.QtWidgets import QWidget, QLineEdit, QLabel, QHBoxLayout, QGroupBox
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont


class PatchName(QWidget):
    nameChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QHBoxLayout(self)
        group = QGroupBox("Patch Name")
        layout = QHBoxLayout(group)
        layout.setContentsMargins(4, 4, 4, 4)

        self.label = QLabel("Name:")
        self.editor = QLineEdit()
        self.editor.setMaxLength(12)  # JD-Xi patch names are max 12 chars
        self.editor.setFont(QFont("Fixed", 10))  # Monospace font
        self.editor.textChanged.connect(self.nameChanged)

        layout.addWidget(self.label)

        layout.addWidget(self.editor)
        group.addLayout(layout)
        main_layout.addWidget(group)
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #2E2E2E;
            }
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
                font-family: 'Myriad Pro';
            }
            QLineEdit {
                font-family: 'Myriad Pro';
                background-color: #1A1A1A;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 5px;
                font-family: 'Consolas';
            }
            QLabel {
                background-color: #3D3D3D;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 5px 15px;
                font-family: 'Myriad Pro';
            }
            QPushButton:hover {
                background-color: #4D4D4D;
                border: 1px solid #FF3333;
            }
            QPushButton:border_pressed {
                background-color: #2D2D2D;
            }
        """
        )

    def setText(self, text):
        self.editor.setText(text)

    def text(self):
        return self.editor.text()
