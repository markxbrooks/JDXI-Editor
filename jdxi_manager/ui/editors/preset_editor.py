from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from typing import Optional

from jdxi_manager.midi import MIDIHelper
from jdxi_manager.ui.editors.base_editor import BaseEditor

class PresetEditor(QMainWindow):
    def __init__(self, midi_helper: Optional[MIDIHelper] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Preset Editor")
        
        # Create central widget and main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # Create editor widget
        self.editor = BaseEditor(midi_helper, self)
        main_layout.addWidget(self.editor)
        
        # Set as central widget
        self.setCentralWidget(main_widget) 