from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QGroupBox
from PySide6.QtCore import Signal

from jdxi_manager.data.digital import DigitalPartial

class PartialSwitch(QWidget):
    """Widget for controlling a single partial's state"""
    
    stateChanged = Signal(DigitalPartial, bool, bool)  # partial, enabled, selected
    
    def __init__(self, partial: DigitalPartial, parent=None):
        super().__init__(parent)
        self.partial = partial
        
        layout = QHBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Enable switch
        self.enable_check = QCheckBox("ON")
        self.enable_check.stateChanged.connect(self._on_state_changed)
        layout.addWidget(self.enable_check)
        
        # Select switch
        self.select_check = QCheckBox("SEL")
        self.select_check.stateChanged.connect(self._on_state_changed)
        layout.addWidget(self.select_check)
        
        # Style
        self.setStyleSheet("""
            QCheckBox {
                color: #CCCCCC;
                font-size: 10px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                background: #333333;
                border: 1px solid #555555;
                border-radius: 2px;
            }
            QCheckBox::indicator:checked {
                background: #CC3333;
                border-color: #FF4444;
            }
        """)

    def _on_state_changed(self, _):
        """Handle checkbox state changes"""
        self.stateChanged.emit(
            self.partial,
            self.enable_check.isChecked(),
            self.select_check.isChecked()
        )

    def setState(self, enabled: bool, selected: bool):
        """Set the partial state"""
        self.enable_check.setChecked(enabled)
        self.select_check.setChecked(selected)

class PartialsPanel(QGroupBox):
    """Panel containing all partial switches"""
    
    def __init__(self, parent=None):
        super().__init__("Partials", parent)
        
        layout = QHBoxLayout()
        layout.setSpacing(10)
        self.setLayout(layout)
        
        # Create switches for each partial (not structure types)
        self.switches = {}
        for partial in DigitalPartial.get_partials():  # Only get actual partials
            switch = PartialSwitch(partial)
            self.switches[partial] = switch
            layout.addWidget(switch)
            
        # Style
        self.setStyleSheet("""
            QGroupBox {
                color: #CCCCCC;
                font-size: 12px;
                border: 1px solid #444444;
                border-radius: 3px;
                margin-top: 1.5ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                background-color: #2D2D2D;
            }
        """) 