from PySide6.QtWidgets import QWidget, QLineEdit, QLabel, QHBoxLayout
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont

class PatchName(QWidget):
    nameChanged = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        self.label = QLabel("Name:")
        self.editor = QLineEdit()
        self.editor.setMaxLength(12)  # JD-Xi patch names are max 12 chars
        self.editor.setFont(QFont("Fixed", 10))  # Monospace font
        self.editor.textChanged.connect(self.nameChanged)
        
        layout.addWidget(self.label)
        layout.addWidget(self.editor)
        
    def setText(self, text):
        self.editor.setText(text)
        
    def text(self):
        return self.editor.text() 