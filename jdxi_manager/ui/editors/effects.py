from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QFrame, QGridLayout, QGroupBox,
    QScrollArea
)
from PySide6.QtCore import Qt

from jdxi_manager.ui.widgets import Slider
from jdxi_manager.ui.editors.base_editor import BaseEditor

class EffectsEditor(BaseEditor):
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(midi_helper, parent)
        self.setWindowTitle("Effects")
        
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create container widget
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        
        # Add effects sections
        container_layout.addWidget(self._create_delay_section())
        container_layout.addWidget(self._create_reverb_section())
        
        # Add container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _create_delay_section(self):
        group = QGroupBox("Delay")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Delay controls
        self.delay_time = Slider("Time", 0, 127)
        self.delay_feedback = Slider("Feedback", 0, 127)
        self.delay_level = Slider("Level", 0, 127)
        
        layout.addWidget(self.delay_time)
        layout.addWidget(self.delay_feedback)
        layout.addWidget(self.delay_level)
        
        return group

    def _create_reverb_section(self):
        group = QGroupBox("Reverb")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Reverb controls
        self.reverb_time = Slider("Time", 0, 127)
        self.reverb_type = QComboBox()
        self.reverb_type.addItems(["ROOM", "HALL", "PLATE"])
        self.reverb_level = Slider("Level", 0, 127)
        
        layout.addWidget(QLabel("Type"))
        layout.addWidget(self.reverb_type)
        layout.addWidget(self.reverb_time)
        layout.addWidget(self.reverb_level)
        
        return group