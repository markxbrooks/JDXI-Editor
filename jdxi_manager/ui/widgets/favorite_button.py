from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, Signal, QSettings
from dataclasses import dataclass
import logging

from jdxi_manager.midi import MIDIHelper
from jdxi_manager.midi.preset_loader import PresetLoader
from jdxi_manager.data.preset_type import PresetType


@dataclass
class PresetFavorite:
    """Preset favorite data"""
    synth_type: str  # Using PresetType constants
    preset_num: int
    preset_name: str
    channel: int


class FavoriteButton(QPushButton):
    """Favorite preset button with save/recall functionality"""
    
    preset_selected = Signal(str, int, int)  # synth_type, preset_num, channel
    
    def __init__(self, slot_num: int, midi_helper: MIDIHelper, parent=None):
        super().__init__(parent)
        self.last_preset = None
        self.preset_loader = None
        self.midi_helper = midi_helper
        self.slot_num = slot_num
        self.preset = None
        self.setFixedSize(60, 30)
        self.setFlat(True)
        #self.settings = QSettings("jdxi_manager2", "settings")
        #self._load_from_settings()
        self._update_style()
        
    def save_preset_as_favourite(self, synth_type: str, preset_num: int, preset_name: str, channel: int):
        """Save current preset to this favorite slot"""
        self.preset = PresetFavorite(synth_type, preset_num, preset_name, channel)
        self._update_style()
        #self._save_to_settings()
        logging.debug(f"Saved preset to favorite {self.slot_num}: {preset_name}")
        
    def load_preset_from_favourites(self):
        """Load saved preset"""
        if not self.preset:
            logging.warning(f"No preset saved in favorite slot {self.slot_num}")
            return
        preset_data = {
            'type': self.preset.synth_type,  # Ensure this is a valid type
            'selpreset': self.preset.preset_num + 1,  # Convert to 1-based index
            'modified': 0  # or 1 if modified
        }
        self.load_preset(
            preset_data
        )
        self._update_style()
        # Save as last loaded preset
        # self.settings.setValue('last_preset/synth_type', self.preset.synth_type)
        # self.settings.setValue('last_preset/preset_num', self.preset.preset_num)
        # self.settings.setValue('last_preset/channel', self.preset.channel)
        # self.settings.setValue('last_preset/preset_name', self.preset.preset_name)
        # Update the display
        logging.debug(f"Loading favorite {self.slot_num}: {self.preset.preset_name}")

    def load_preset(self, preset_data):
        """Load preset data into synth"""
        try:
            if self.midi_helper:
                # Use PresetLoader for consistent preset loading
                self.preset_loader = PresetLoader(self.midi_helper)
                self.preset_loader.load_preset(
                    preset_data,
                )
                # Store as last loaded preset
                self.last_preset = preset_data
                #self.settings.setValue("last_preset", preset_data)
        except Exception as e:
            logging.error(f"Error loading preset: {e}")
            
    def _save_to_settings(self):
        """Save preset data to settings"""
        if self.preset:
            self.settings.setValue(f'favorites/slot{self.slot_num}/synth_type', self.preset.synth_type)
            self.settings.setValue(f'favorites/slot{self.slot_num}/preset_num', self.preset.preset_num)
            self.settings.setValue(f'favorites/slot{self.slot_num}/preset_name', self.preset.preset_name)
            self.settings.setValue(f'favorites/slot{self.slot_num}/channel', self.preset.channel)
        else:
            # Clear settings if no preset
            self.settings.remove(f'favorites/slot{self.slot_num}')
            
    def _load_from_settings(self):
        """Load preset data from settings"""
        synth_type = self.settings.value(f'favorites/slot{self.slot_num}/synth_type', '')
        if synth_type:
            preset_num = self.settings.value(f'favorites/slot{self.slot_num}/preset_num', 0, type=int)
            preset_name = self.settings.value(f'favorites/slot{self.slot_num}/preset_name', '')
            channel = self.settings.value(f'favorites/slot{self.slot_num}/channel', 0, type=int)
            self.preset = PresetFavorite(synth_type, preset_num, preset_name, channel)
            
    def clear_preset(self):
        """Clear the saved preset"""
        self.preset = None
        # self._save_to_settings()
        self._update_style()
        
    def _update_style(self):
        """Update button appearance"""
        if self.preset:
            # Get color based on synth type
            if self.preset.synth_type == PresetType.ANALOG:
                color = "#00A3F0"  # Analog blue
            elif self.preset.synth_type in [PresetType.DIGITAL_1, PresetType.DIGITAL_2]:
                color = "#FF0000"  # Red for both digital synths
            elif self.preset.synth_type == PresetType.DRUMS:
                color = "#00FF00"  # Green for drums
            else:
                color = "#666666"  # Gray for unknown types
                
            # Set text to preset name
            # Get just the preset name without the number prefix
            if ':' in self.preset.preset_name:
                preset_display_name = self.preset.preset_name.split(':', 1)[1].strip()
            else:
                preset_display_name = self.preset.preset_name
                
            text = f"FAV {self.slot_num + 1}\n{preset_display_name}"
        else:
            color = "#666666"  # Gray for empty slot
            text = f"FAV {self.slot_num + 1}"
            
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