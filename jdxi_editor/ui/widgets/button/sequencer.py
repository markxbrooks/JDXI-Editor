import logging
from typing import Optional

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QPainter, QPen, QColor

from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.midi.preset.data import ToneData
from jdxi_editor.midi.preset.helper import PresetHelper
from jdxi_editor.midi.preset.tone import Tone


class SequencerSquare(QPushButton):
    """Square button for sequencer/favorites with illuminated state"""
    
    def __init__(self, slot_num, midi_helper: Optional[MidiIOHelper], parent=None):
        super().__init__(parent)
        self.preset_loader = None  # we will be using this later
        self.midi_helper = midi_helper
        self.settings = QSettings("mabsoft", "jdxi_editor")
        self.slot_num = slot_num
        self.preset = None
        self.last_preset = None
        self.illuminated = False
        self.setFixedSize(30, 30)
        self.setCheckable(True)
        self.clicked.connect(self._handle_toggle)
        self.clicked.connect(self._handle_click)

    def _handle_toggle(self, checked):
        """Handle button toggle"""
        self.illuminated = checked
        self.is_checked = checked
        if self.preset:
            self.setToolTip(f"Program {self.preset.name}, {self.preset.synth_type}")
        self.update()  # Trigger repaint

    def _handle_click(self, checked):
        """Handle button toggle"""
        if self.isChecked():
            if self.preset:
                self.load_preset(self.preset)
            # self._load_from_settings()
        # else:
        #    self.save_preset_as_favourite()
        
    def paintEvent(self, event):
        """Custom paint for illuminated appearance"""
        super().paintEvent(event)
        
        if self.isChecked():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw red outline when illuminated
            pen = QPen(QColor("#FF0000"))  # Roland red
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(1, 1, self.width()-2, self.height()-2)

    def save_preset_as_favourite(self, synth_type: str, preset_num: int, preset_name: str, channel: int):
        """Save current preset to this favorite slot"""
        # Preset(number=0, name='001: JP8 Strings1', preset_type='Digital 1')
        self.preset = Tone(number=preset_num, name=preset_name, synth_type=synth_type)
        # self._save_to_settings()
        logging.debug(f"Saved preset to favorite {self.slot_num}: {preset_name}")

    def clear_preset(self):
        """Clear the saved preset"""
        self.preset = None
        # self._save_to_settings()

    def load_preset(self, preset_data):
        """Load preset data into synth"""
        try:
            if self.midi_helper:
                # Use PresetLoader for consistent preset loading
                self.preset_loader = PresetHelper(self.midi_helper)
                self.preset_loader.load_preset(
                    preset_data,
                )
                # Store as last loaded preset
                self.last_preset = preset_data
                # self.settings.setValue("last_preset", preset_data)
        except Exception as e:
            logging.error(f"Error loading preset: {e}")

    """
    def _save_to_settings(self):
        # Save preset data to settings
        if self.preset:
            self.settings.setValue(f'favorites/slot{self.slot_num}/synth_type', self.preset.synth_type)
            self.settings.setValue(f'favorites/slot{self.slot_num}/preset_num', self.preset.preset_num)
            self.settings.setValue(f'favorites/slot{self.slot_num}/preset_name', self.preset.preset_name)
            self.settings.setValue(f'favorites/slot{self.slot_num}/channel', self.preset.channel)
        else:
            # Clear settings if no preset
            self.settings.remove(f'favorites/slot{self.slot_num}')    
    
    def _load_from_settings(self):
        # Load preset data from settings
        synth_type = self.settings.value(f'favorites/slot{self.slot_num}/synth_type', '')
        if synth_type:
            preset_num = self.settings.value(f'favorites/slot{self.slot_num}/preset_num', 0, type=int)
            preset_name = self.settings.value(f'favorites/slot{self.slot_num}/preset_name', '')
            channel = self.settings.value(f'favorites/slot{self.slot_num}/channel', 0, type=int)
            # self.preset = PresetFavorite(synth_type, preset_num, preset_name, channel)
            self.preset = Preset(number=preset_num, name=preset_name, preset_type=synth_type)
            
        def load_stored_preset(self):
        #""Load saved preset""
        if not self.preset:
            logging.warning(f"No preset saved in favorite slot {self.slot_num}")
            return
        preset_data = PresetData(
            type=self.preset.preset_type,  # Ensure this is address valid preset_type
            current_selection=self.preset.number + 1,  # Convert to 1-based index
            modified=0  # or 1 if modified
        )
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
    """

