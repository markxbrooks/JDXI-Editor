from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QPushButton, QGroupBox, QTabWidget,
    QComboBox, QMainWindow
)
from PySide6.QtCore import Qt, Signal
import logging
from PySide6.QtCore import QThread
from typing import List

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
        
        # Add response handling
        if midi_helper:
            midi_helper.register_callback(self._handle_midi_response)
        self.waiting_for_response = False
        self.response_data = {}
        
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
                # Clear any previous response data
                self.response_data = {}
                
                # Determine bank MSB/LSB based on synth type
                if synth_type == "Digital 1":
                    bank_msb = 0x5F  # 95 SuperNATURAL
                    bank_lsb = 0x40  # 64 Preset bank
                    channel = 1
                    area = 0x19  # Digital 1 area
                elif synth_type == "Digital 2":
                    bank_msb = 0x5F  # 95 SuperNATURAL
                    bank_lsb = 0x40  # 64 Preset bank
                    channel = 2
                    area = 0x1A  # Digital 2 area
                elif synth_type == "Analog":
                    bank_msb = 0x5E  # 94 Analog
                    bank_lsb = 0x40  # 64 Preset bank
                    channel = 0
                    area = 0x18  # Program area
                else:  # Drums
                    bank_msb = 0x56  # 86 Drums
                    bank_lsb = 0x40  # 64 Preset bank
                    channel = 9
                    area = 0x18  # Program area

                # Create SysEx messages sequence
                messages = [
                    # Bank MSB
                    [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x18, 0x00, 0x20, 0x06, bank_msb, self._calculate_checksum([0x18, 0x00, 0x20, 0x06, bank_msb]), 0xF7],
                    # Bank LSB
                    [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x18, 0x00, 0x20, 0x07, bank_lsb, self._calculate_checksum([0x18, 0x00, 0x20, 0x07, bank_lsb]), 0xF7],
                    # Program Number
                    [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x18, 0x00, 0x20, 0x08, preset_num, self._calculate_checksum([0x18, 0x00, 0x20, 0x08, preset_num]), 0xF7],
                    # Request Common data
                    [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x11, area, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, self._calculate_checksum([area, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40]), 0xF7],
                    # Request OSC data
                    [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x11, area, 0x01, 0x20, 0x00, 0x00, 0x00, 0x00, 0x3D, self._calculate_checksum([area, 0x01, 0x20, 0x00, 0x00, 0x00, 0x00, 0x3D]), 0xF7]
                ]

                # Send messages with small delay between each
                for msg in messages:
                    self.midi_helper.send_message(msg)
                    QThread.msleep(20)  # 20ms delay

                # Get preset name
                if synth_type == "Digital 1" or synth_type == "Digital 2":
                    presets = DIGITAL_PRESETS
                elif synth_type == "Analog":
                    presets = AN_PRESETS
                else:
                    presets = DRUM_PRESETS
                preset_name = presets[preset_num]

                # Emit preset change signal
                self.preset_changed.emit(preset_num + 1, preset_name, channel)

                # Save as last used preset
                if isinstance(self.parent(), QMainWindow):
                    self.parent()._save_last_preset(synth_type, preset_num, channel)

                logging.debug(f"Loaded {synth_type} preset {preset_num + 1}: {preset_name}")

        except Exception as e:
            logging.error(f"Error loading preset: {str(e)}")

    def _calculate_checksum(self, data: List[int]) -> int:
        """Calculate Roland checksum for SysEx message
        
        Checksum = 128 - (sum of address and data bytes % 128)
        """
        checksum = sum(data) % 128
        return (128 - checksum) & 0x7F

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

    def _handle_midi_response(self, message, timestamp):
        """Handle MIDI response from JD-Xi"""
        try:
            if not message or message[0] != 0xF0:  # Not SysEx
                return
                
            if len(message) < 8:  # Too short
                return
                
            command = message[7]
            if command == 0x12:  # DT1 Response
                area = message[8]
                section = message[10]
                
                # Store response data
                if area not in self.response_data:
                    self.response_data[area] = {}
                self.response_data[area][section] = message[12:-2]  # Store data without header/checksum
                
                # Log received data
                area_name = {
                    0x19: "Digital 1",
                    0x1A: "Digital 2",
                    0x18: "Program"
                }.get(area, f"Unknown ({area:02X})")
                
                section_name = {
                    0x00: "Common",
                    0x20: "OSC",
                    0x21: "Filter",
                    0x22: "Amp",
                    0x50: "Modify"
                }.get(section, f"Unknown ({section:02X})")
                
                logging.debug(f"Received {area_name} {section_name} data: " + 
                            " ".join([f"{b:02X}" for b in message[12:-2]]))
                
                # Process complete patch data if we have all sections
                if area in self.response_data and len(self.response_data[area]) >= 5:
                    self._process_complete_patch(area)
                    self.response_data[area] = {}  # Clear stored data
                    
        except Exception as e:
            logging.error(f"Error handling MIDI response: {str(e)}")

    def _process_complete_patch(self, area: int):
        """Process complete patch data once all sections received"""
        try:
            if area == 0x19:  # Digital 1
                synth_type = "Digital 1"
            elif area == 0x1A:  # Digital 2
                synth_type = "Digital 2"
            else:
                return  # Not a synth patch area
                
            patch_data = self.response_data[area]
            
            # Extract key parameters
            if 0x20 in patch_data:  # OSC section
                osc_data = patch_data[0x20]
                waveform = osc_data[0] if osc_data else 0
                
                wave_names = {
                    0: "Saw",
                    1: "Square",
                    2: "Pulse",
                    3: "Triangle",
                    4: "Sine",
                    5: "Noise",
                    6: "Super Saw",
                    7: "PCM"
                }
                wave_name = wave_names.get(waveform, f"Unknown ({waveform})")
                
                logging.debug(f"{synth_type} Waveform: {wave_name}")
                
            if 0x21 in patch_data:  # Filter section
                filter_data = patch_data[0x21]
                cutoff = filter_data[0] if filter_data else 0
                resonance = filter_data[1] if len(filter_data) > 1 else 0
                
                logging.debug(f"{synth_type} Filter - Cutoff: {cutoff}, Resonance: {resonance}")
                
            # Could add more parameter processing here...
            
        except Exception as e:
            logging.error(f"Error processing patch data: {str(e)}") 