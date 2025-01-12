from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QPushButton, QGroupBox, QTabWidget,
    QComboBox, QMainWindow
)
from PySide6.QtCore import Qt, Signal
import logging

from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.data.analog import AN_PRESETS, AN_CATEGORIES, AnalogTone
from jdxi_manager.data.digital import DIGITAL_PRESETS, DIGITAL_CATEGORIES
from jdxi_manager.midi.constants import ANALOG_SYNTH_AREA, DIGITAL_SYNTH_AREA, BANK_MSB, BANK_LSB, ANALOG_BANK_MSB, DIGITAL_BANK_MSB, DRUM_BANK_MSB, PRESET_BANK_LSB, PRESET_BANK_2_LSB
from jdxi_manager.data.drums import DRUM_PRESETS, DRUM_CATEGORIES


class PresetEditor(BaseEditor):
    """Editor for loading presets"""
    # Add signal for preset changes
    preset_changed = Signal(int, str, int)  # preset_number, preset_name, channel
    
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(midi_helper, parent)
        self.setWindowTitle("Synth Presets")
        
        # Create main layout
        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Add analog presets tab
        analog_widget = self._create_preset_tab(AN_PRESETS, "Analog")
        self.tab_widget.addTab(analog_widget, "Analog Presets")
        
        # Add digital presets tabs
        digital1_widget = self._create_preset_tab(DIGITAL_PRESETS, "Digital 1")
        self.tab_widget.addTab(digital1_widget, "Digital 1 Presets")
        
        digital2_widget = self._create_preset_tab(DIGITAL_PRESETS, "Digital 2")
        self.tab_widget.addTab(digital2_widget, "Digital 2 Presets")
        
        # Add drum presets tab
        drum_widget = self._create_preset_tab(DRUM_PRESETS, "Drums")
        self.tab_widget.addTab(drum_widget, "Drum Presets")
        
        # Set window properties
        self.setMinimumWidth(400)
        self.setMinimumHeight(500)
        
    def _create_preset_tab(self, presets, synth_type):
        """Create a preset list tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Add category filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Category:"))
        
        category_combo = QComboBox()
        if synth_type.startswith("Digital"):
            categories = DIGITAL_CATEGORIES
        elif synth_type == "Drums":
            categories = DRUM_CATEGORIES
        else:
            categories = AN_CATEGORIES
            
        category_combo.addItem("All")
        category_combo.addItems(sorted(categories.keys()))
        filter_layout.addWidget(category_combo)
        layout.addLayout(filter_layout)
        
        # Create preset list
        preset_list = QListWidget()
        preset_list.addItems(presets)
        preset_list.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(preset_list)
        
        # Create buttons
        button_layout = QHBoxLayout()
        load_button = QPushButton("Load")
        load_button.setEnabled(False)
        button_layout.addWidget(load_button)
        
        init_button = QPushButton("Initialize")
        button_layout.addWidget(init_button)
        layout.addLayout(button_layout)
        
        # Connect signals
        preset_list.currentRowChanged.connect(
            lambda row: load_button.setEnabled(row >= 0)
        )
        load_button.clicked.connect(
            lambda: self._on_load_clicked(synth_type, preset_list.currentRow())
        )
        init_button.clicked.connect(
            lambda: self._on_init_clicked(synth_type)
        )
        
        # Connect category filter
        category_combo.currentTextChanged.connect(
            lambda cat: self._filter_presets(preset_list, cat, categories if cat != "All" else None)
        )
        
        return widget
        
    def _on_load_clicked(self, synth_type, preset_num):
        """Load selected preset"""
        try:
            if self.midi_helper and preset_num >= 0:
                if synth_type == "Digital 1":
                    presets = DIGITAL_PRESETS
                    bank_msb = 0x5F        # 95 for SuperNATURAL
                    bank_lsb = 0x40        # 64 for preset bank
                    program = preset_num + 1  # 1-based program numbers
                    channel = 1            # Digital 1 channel
                    
                elif synth_type == "Digital 2":
                    presets = DIGITAL_PRESETS
                    bank_msb = 0x5F        # 95 for SuperNATURAL
                    bank_lsb = 0x40        # 64 for preset bank
                    program = preset_num + 1  # 1-based program numbers
                    channel = 2            # Digital 2 channel
                    
                elif synth_type == "Analog":
                    presets = AN_PRESETS
                    bank_msb = 0x5E        # 94 for Analog synth
                    bank_lsb = 0x40        # 64 for preset bank
                    program = preset_num + 1  # 1-based program numbers
                    channel = 0            # Analog channel
                    
                else:  # Drums
                    presets = DRUM_PRESETS
                    bank_msb = 0x56        # 86 for Drum kits
                    bank_lsb = 0x40        # 64 for preset bank
                    program = preset_num + 1  # 1-based program numbers
                    channel = 9            # Drum channel
                
                # Send bank select MSB (CC 0)
                self.midi_helper.send_message([0xB0 | channel, 0x00, bank_msb])
                
                # Send bank select LSB (CC 32)
                self.midi_helper.send_message([0xB0 | channel, 0x20, bank_lsb])
                
                # Send program change
                self.midi_helper.send_message([0xC0 | channel, program])
                
                # Add detailed logging
                logging.debug(
                    f"Sending MIDI messages for {synth_type} preset {preset_num + 1}:\n"
                    f"Bank Select MSB: {bank_msb:02X} (CC 0)\n"
                    f"Bank Select LSB: {bank_lsb:02X} (CC 32)\n"
                    f"Program Change: {program:02X}\n"
                    f"Channel: {channel}"
                )
                
                # Emit preset change signal
                preset_name = presets[preset_num]
                self.preset_changed.emit(preset_num + 1, preset_name, channel)
                
                # Save as last used preset
                if isinstance(self.parent(), QMainWindow):
                    self.parent()._save_last_preset(synth_type, preset_num, channel)
                
        except Exception as e:
            logging.error(f"Error loading preset: {str(e)}")
            
    def _on_init_clicked(self, synth_type):
        """Initialize to default patch"""
        try:
            if self.midi_helper:
                if synth_type == "Analog":
                    AnalogTone.send_init_data(self.midi_helper)
                else:
                    # Send init data for digital synth
                    # TODO: Implement digital init data
                    pass
                    
                logging.debug(f"Initialized {synth_type} synth")
                
        except Exception as e:
            logging.error(f"Error initializing: {str(e)}") 
        
    def _filter_presets(self, preset_list: QListWidget, category: str, categories: dict = None):
        """Filter presets by category"""
        preset_list.clear()
        
        if categories and category in categories:
            # Show only presets in selected category
            preset_list.addItems(categories[category])
        else:
            # Show all presets
            if self.tab_widget.currentIndex() == 0:
                presets = AN_PRESETS
            elif self.tab_widget.currentIndex() == 3:  # Drums tab
                presets = DRUM_PRESETS
            else:
                presets = DIGITAL_PRESETS
            preset_list.addItems(presets) 