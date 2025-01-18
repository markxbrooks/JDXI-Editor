from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, Signal
from dataclasses import dataclass
import logging


@dataclass
class PresetFavorite:
    """Preset favorite data"""
    synth_type: str
    preset_num: int
    preset_name: str
    channel: int


class FavoriteButton(QPushButton):
    """Favorite preset button with save/recall functionality"""
    
    preset_selected = Signal(str, int, int)  # synth_type, preset_num, channel
    
    def __init__(self, slot_num: int, parent=None):
        super().__init__(parent)
        self.slot_num = slot_num
        self.preset = None
        self.setFixedSize(60, 30)
        self.setFlat(True)
        self._update_style()
        
    def save_preset_as_favourite(self, synth_type: str, preset_num: int, preset_name: str, channel: int):
        """Save current preset to this favorite slot"""
        self.preset = PresetFavorite(synth_type, preset_num, preset_name, channel)
        self._update_style()
        logging.debug(f"Saved preset to favorite {self.slot_num}: {preset_name}")
        
    def load_preset_from_favourites(self):
        """Load saved preset"""
        if self.preset:
            self.preset_selected.emit(
                self.preset.synth_type,
                self.preset.preset_num,
                self.preset.channel
            )
            logging.debug(f"Loading favorite {self.slot_num}: {self.preset.preset_name}")
            
    def _update_style(self):
        """Update button appearance"""
        if self.preset:
            # Get color based on synth type
            if self.preset.synth_type == "Analog":
                color = "#00A3F0"  # Analog blue
            elif self.preset.synth_type == "Digital 1":
                color = "#FF0000"  # Red
            elif self.preset.synth_type == "Digital 2":
                color = "#FF0000"  # Red
            else:  # Drums
                color = "#FF0000"  # Red
                
            # Set text to preset name
            text = f"FAV {self.slot_num + 1}\n{self.preset.preset_name[4:]}"
        else:
            color = "#666666"  # Gray for empty slot
            text = f"Fav {self.slot_num + 1}"
            
        # Create gradient background
        gradient = f"""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {color}22,
                stop:0.5 {color}11,
                stop:1 {color}22
            );
        """
        
        # Set button style
        self.setStyleSheet(f"""
            QPushButton {{
                {gradient}
                font-family: "Consolas", "Fixed";
                border: 1px solid red;
                border-radius: 3px;
                color: {color};
                font-size: 9px;
                font-weight: bold;
                padding: 2px;
                text-align: center;
            }}
            QPushButton:hover {{
                background: {color}33;
            }}
            QPushButton:pressed {{
                background: {color}44;
            }}
        """)
        
        self.setText(text) 