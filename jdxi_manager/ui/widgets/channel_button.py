from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
import logging

class ChannelButton(QPushButton):
    """Channel indicator button with synth-specific styling"""
    
    CHANNEL_STYLES = {
        0: ("ANALOG", "#FF8C00"),     # Orange for Analog
        1: ("DIGI 1", "#00FF00"),     # Green for Digital 1
        2: ("DIGI 2", "#00FFFF"),     # Cyan for Digital 2
        9: ("DRUMS", "#FF00FF"),      # Magenta for Drums
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
        
        # Create gradient background
        gradient = f"""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {color}33,
                stop:0.5 {color}22,
                stop:1 {color}33
            );
        """
        
        # Set button style
        self.setStyleSheet(f"""
            QPushButton {{
                {gradient}
                border: 1px solid {color};
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