from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
import logging


class ChannelButton(QPushButton):
    """Channel indicator button with synth-specific styling"""
    
    CHANNEL_STYLES = {
        0: ("ANALOG", "#00A3F0"),     # Blue for Analog
        1: ("DIGI 1", "#FF0000"),     # Red for Digital 1
        2: ("DIGI 2", "#FF0000"),     # Red for Digital 2
        9: ("DRUMS", "#FF0000"),      # Red for Drums
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 30)  # Horizontal layout
        self.setFlat(True)
        self.current_channel = 0
        self._update_style()
        
    def set_channel(self, channel: int):
        """Set channel and update appearance"""
        self.current_channel = channel
        self._update_style()
        
    def _update_style(self):
        """Update button appearance based on channel"""
        style, color = self.CHANNEL_STYLES.get(
            self.current_channel, 
            (f"CH {self.current_channel + 1}", "#FFFFFF")
        )
        
        # Set button style
        self.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid red;
                font-family: "Consolas", "Fixed";
                border-radius: 3px;
                color: {color};
                font-size: 10px;
                font-weight: bold;
                padding: 2px;
                text-align: center;
            }}
            QPushButton:pressed {{
                background: {color}44;
            }}
        """)
        
        # Set text
        self.setText(style)
