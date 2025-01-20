from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QComboBox, QLabel, QPushButton, QLineEdit, QGroupBox, QMessageBox
)
from PySide6.QtCore import Signal, Qt, QSettings
from PySide6.QtGui import QFont
from typing import Optional, List, Dict
import logging
import time

from jdxi_manager.midi import MIDIHelper
from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.midi.constants import (
    DIGITAL_SYNTH_AREA,
    ANALOG_SYNTH_AREA,
    DRUM_KIT_AREA,
    DT1_COMMAND_12,
    RQ1_COMMAND_11
)
from jdxi_manager.ui.style import Style
from jdxi_manager.data.preset_type import PresetType
from jdxi_manager.midi.preset_loader import PresetLoader
from jdxi_manager.midi.parameter_handler import ParameterHandler

# Preset lists
ANALOG_PRESETS = [
    '001: Toxic Bass 1', '002: Sub Bass 1', '003: Backwards 1', '004: Fat as That1', '005: Saw+Sub Bs 1',
    '006: Saw Bass 1', '007: Pulse Bass 1',
    '008: ResoSaw Bs 1', '009: ResoSaw Bs 2', '010: AcidSaw SEQ1', '011: Psy Bass 1', '012: Dist TB Bs 1',
    '013: Sqr Bass 1', '014: Tri Bass 1',
    '015: Snake Glide1', '016: Soft Bass 1', '017: Tear Drop 1', '018: Slo worn 1', '019: Dist LFO Bs1',
    '020: ResoPulseBs1', '021: Squelchy 1',
    '022: DnB Wobbler1', '023: OffBeat Wob1', '024: Chilled Wob', '025: Bouncy Bass1', '026: PulseOfLife1',
    '027: PWM Base 1', '028: Pumper Bass1',
    '029: ClickerBass1', '030: Psy Bass 2', '031: HooverSuprt1', '032: Celoclip 1', '033: Tri Fall Bs1',
    '034: 808 Bass 1', '035: House Bass 1',
    '036: Psy Bass 3', '037: Reel 1', '038: PortaSaw Ld1', '039: Porta Lead 1', '040: Analog Tp 1', '041: Tri Lead 1',
    '042: Sine Lead 1',
    '043: Saw Buzz 1', '044: Buzz Saw Ld1', '045: Laser Lead 1', '046: Saw & Per 1', '047: Insect 1', '048: Sqr SEQ 1',
    '049: ZipPhase 1',
    '050: Stinger 1', '051: 3 Oh 3', '052: Sus Zap 1', '053: Bowouch 1', '054: Resocut 1', '055: LFO FX',
    '056: Fall Synth 1',
    '057: Twister 1', '058: Analog Kick1', '059: Zippers 1', '060: Zippers 2', '061: Zippers 3', '062: Siren Hell 1',
    '063: SirenFX/Mod1'
]

DIGITAL_PRESETS = [
    '001: JP8 Strings1', '002: Soft Pad 1', '003: JP8 Strings2', '004: JUNO Str 1', '005: Oct Strings',
    '006: Brite Str 1', '007: Boreal Pad',
    '008: JP8 Strings3', '009: JP8 Strings4', '010: Hollow Pad 1', '011: LFO Pad 1', '012: Hybrid Str',
    '013: Awakening 1', '014: Cincosoft 1',
    '015: Bright Pad 1', '016: Analog Str 1', '017: Soft ResoPd1', '018: HPF Poly 1', '019: BPF Poly',
    '020: Sweep Pad 1', '021: Soft Pad 2',
    '022: Sweep JD 1', '023: FltSweep Pd1', '024: HPF Pad', '025: HPF SweepPd1', '026: KOff Pad', '027: Sweep Pad 2',
    '028: TrnsSweepPad',
    '029: Revalation 1', '030: LFO CarvePd1', '031: RETROX 139 1', '032: LFO ResoPad1', '033: PLS Pad 1',
    '034: PLS Pad 2', '035: Trip 2 Mars1',
    '036: Reso S&H Pd1', '037: SideChainPd1', '038: PXZoon 1', '039: Psychoscilo1', '040: Fantasy 1',
    '041: D-50 Stack 1', '042: Organ Pad',
    '043: Bell Pad', '044: Dreaming 1', '045: Syn Sniper 1', '046: Strings 1', '047: D-50 Pizz 1', '048: Super Saw 1',
    '049: S-SawStacLd1',
    '050: Tekno Lead 1', '051: Tekno Lead 2', '052: Tekno Lead 3', '053: OSC-SyncLd 1', '054: WaveShapeLd1',
    '055: JD RingMod 1', '056: Buzz Lead 1',
    '057: Buzz Lead 2', '058: SawBuzz Ld 1', '059: Sqr Buzz Ld1', '060: Tekno Lead 4', '061: Dist Flt TB1',
    '062: Dist TB Sqr1', '063: Glideator 1',
    '064: Vintager 1', '065: Hover Lead 1', '066: Saw Lead 1', '067: Saw+Tri Lead', '068: PortaSaw Ld1',
    '069: Reso Saw Ld', '070: SawTrap Ld 1',
    '071: Fat GR Lead', '072: Pulstar Ld', '073: Slow Lead', '074: AnaVox Lead', '075: Square Ld 1', '076: Square Ld 2',
    '077: Sqr Lead 1',
    '078: Sqr Trap Ld1', '079: Sine Lead 1', '080: Tri Lead', '081: Tri Stac Ld1', '082: 5th SawLead1',
    '083: Sweet 5th 1', '084: 4th Syn Lead',
    '085: Maj Stack Ld', '086: MinStack Ld1', '087: Chubby Lead1', '088: CuttingLead1', '089: Seq Bass 1',
    '090: Reso Bass 1', '091: TB Bass 1',
    '092: 106 Bass 1', '093: FilterEnvBs1', '094: JUNO Sqr Bs1', '095: Reso Bass 2', '096: JUNO Bass', '097: MG Bass 1',
    '098: 106 Bass 3',
    '099: Reso Bass 3', '100: Detune Bs 1', '101: MKS-50 Bass1', '102: Sweep Bass', '103: MG Bass 2', '104: MG Bass 3',
    '105: ResRubber Bs',
    '106: R&B Bass 1', '107: Reso Bass 4', '108: Wide Bass 1', '109: Chow Bass 1', '110: Chow Bass 2',
    '111: SqrFilterBs1', '112: Reso Bass 5',
    '113: Syn Bass 1', '114: ResoSawSynBs', '115: Filter Bass1', '116: SeqFltEnvBs', '117: DnB Bass 1',
    '118: UnisonSynBs1', '119: Modular Bs',
    '120: Monster Bs 1', '121: Monster Bs 2', '122: Monster Bs 3', '123: Monster Bs 4', '124: Square Bs 1',
    '125: 106 Bass 2', '126: 5th Stac Bs1',
    '127: SqrStacSynBs', '128: MC-202 Bs', '129: TB Bass 2', '130: Square Bs 2', '131: SH-101 Bs', '132: R&B Bass 2',
    '133: MG Bass 4',
    '134: Seq Bass 2', '135: Tri Bass 1', '136: BPF Syn Bs 2', '137: BPF Syn Bs 1', '138: Low Bass 1',
    '139: Low Bass 2', '140: Kick Bass 1',
    '141: SinDetuneBs1', '142: Organ Bass 1', '143: Growl Bass 1', '144: Talking Bs 1', '145: LFO Bass 1',
    '146: LFO Bass 2', '147: Crack Bass',
    '148: Wobble Bs 1', '149: Wobble Bs 2', '150: Wobble Bs 3', '151: Wobble Bs 4', '152: SideChainBs1',
    '153: SideChainBs2', '154: House Bass 1',
    '155: FM Bass', '156: 4Op FM Bass1', '157: Ac. Bass', '158: Fingerd Bs 1', '159: Picked Bass', '160: Fretless Bs',
    '161: Slap Bass 1',
    '162: JD Piano 1', '163: E. Grand 1', '164: Trem EP 1', '165: FM E.Piano 1', '166: FM E.Piano 2',
    '167: Vib Wurly 1', '168: Pulse Clav',
    '169: Clav', '170: 70\'s E.Organ', '171: House Org 1', '172: House Org 2', '173: Bell 1', '174: Bell 2',
    '175: Organ Bell',
    '176: Vibraphone 1', '177: Steel Drum', '178: Harp 1', '179: Ac. Guitar', '180: Bright Strat', '181: Funk Guitar1',
    '182: Jazz Guitar',
    '183: Dist Guitar1', '184: D. Mute Gtr1', '185: E. Sitar', '186: Sitar Drone', '187: FX 1', '188: FX 2',
    '189: FX 3',
    '190: Tuned Winds1', '191: Bend Lead 1', '192: RiSER 1', '193: Rising SEQ 1', '194: Scream Saw', '195: Noise SEQ 1',
    '196: Syn Vox 1',
    '197: JD SoftVox', '198: Vox Pad', '199: VP-330 Chr', '200: Orch Hit', '201: Philly Hit', '202: House Hit',
    '203: O\'Skool Hit1',
    '204: Punch Hit', '205: Tao Hit', '206: SEQ Saw 1', '207: SEQ Sqr', '208: SEQ Tri 1', '209: SEQ 1', '210: SEQ 2',
    '211: SEQ 3', '212: SEQ 4', '213: Sqr Reso Plk', '214: Pluck Synth1', '215: Paperclip 1', '216: Sonar Pluck1',
    '217: SqrTrapPlk 1',
    '218: TB Saw Seq 1', '219: TB Sqr Seq 1', '220: JUNO Key', '221: Analog Poly1', '222: Analog Poly2',
    '223: Analog Poly3', '224: Analog Poly4',
    '225: JUNO Octavr1', '226: EDM Synth 1', '227: Super Saw 2', '228: S-Saw Poly', '229: Trance Key 1',
    '230: S-Saw Pad 1', '231: 7th Stac Syn',
    '232: S-SawStc Syn', '233: Trance Key 2', '234: Analog Brass', '235: Reso Brass', '236: Soft Brass 1',
    '237: FM Brass', '238: Syn Brass 1',
    '239: Syn Brass 2', '240: JP8 Brass', '241: Soft SynBrs1', '242: Soft SynBrs2', '243: EpicSlow Brs',
    '244: JUNO Brass', '245: Poly Brass',
    '246: Voc:Ensemble', '247: Voc:5thStack', '248: Voc:Robot', '249: Voc:Saw', '250: Voc:Sqr', '251: Voc:Rise Up',
    '252: Voc:Auto Vib',
    '253: Voc:PitchEnv', '254: Voc:VP-330', '255: Voc:Noise'
]

DRUM_PRESETS = [
    '001: TR-909 Kit 1', '002: TR-808 Kit 1', '003: 707&727 Kit1', '004: CR-78 Kit 1', '005: TR-606 Kit 1',
    '006: TR-626 Kit 1', '007: EDM Kit 1',
    '008: Drum&Bs Kit1', '009: Techno Kit 1', '010: House Kit 1', '011: Hiphop Kit 1', '012: R&B Kit 1',
    '013: TR-909 Kit 2', '014: TR-909 Kit 3',
    '015: TR-808 Kit 2', '016: TR-808 Kit 3', '017: TR-808 Kit 4', '018: 808&909 Kit1', '019: 808&909 Kit2',
    '020: 707&727 Kit2', '021: 909&7*7 Kit1',
    '022: 808&7*7 Kit1', '023: EDM Kit 2', '024: Techno Kit 2', '025: Hiphop Kit 2', '026: 80\'s Kit 1',
    '027: 90\'s Kit 1', '028: Noise Kit 1',
    '029: Pop Kit 1', '030: Pop Kit 2', '031: Rock Kit', '032: Jazz Kit', '033: Latin Kit'
]


class PresetEditor(QMainWindow):
    preset_changed = Signal(int, str, int)

    def __init__(self, midi_helper: Optional[MIDIHelper] = None, parent: Optional[QWidget] = None, preset_type: str = PresetType.ANALOG):
        super().__init__(parent)
        self.setMinimumSize(400, 800)
        self.setWindowTitle("Preset Editor")
        self.midi_helper = midi_helper
        self.channel = 1  # Default channel
        self.preset_type = preset_type
        self.parameter_handler = ParameterHandler()
        
        if midi_helper:
            midi_helper.parameter_received.connect(self.parameter_handler.update_parameter)
            self.parameter_handler.parameters_updated.connect(self._update_ui)
        
        # Set window style
        self.setStyleSheet(Style.EDITOR_STYLE)
        
        # Create central widget and main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)  # Add some padding
        main_layout.setSpacing(10)  # Add spacing between widgets
        main_widget.setLayout(main_layout)
        
        # Create preset control group
        preset_group = QGroupBox("Preset Controls")
        preset_layout = QVBoxLayout()
        preset_group.setLayout(preset_layout)
        
        # Create preset type selector
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type:"))
        self.type_selector = QComboBox()
        self.type_selector.addItems([
            PresetType.ANALOG,
            PresetType.DIGITAL_1,
            PresetType.DIGITAL_2,
            PresetType.DRUMS
        ])
        self.settings = QSettings("jdxi_manager", "settings")
        self.type_selector.setCurrentText(preset_type)
        self.type_selector.currentTextChanged.connect(self._on_type_changed)
        type_row.addWidget(self.type_selector)
        preset_layout.addLayout(type_row)
        
        # Create search box
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search presets...")
        self.search_box.textChanged.connect(self._filter_presets)
        search_row.addWidget(self.search_box)
        preset_layout.addLayout(search_row)
        
        # Create preset selector
        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Preset:"))
        self.preset_selector = QComboBox()
        self.preset_selector.currentIndexChanged.connect(self._on_preset_changed)
        self.preset_selector.setMinimumWidth(200)
        
        # Initialize with first preset selected
        self._update_preset_list()
        if self.preset_selector.count() > 0:
            self.preset_selector.setCurrentIndex(0)
        preset_row.addWidget(self.preset_selector)
        preset_layout.addLayout(preset_row)
        
        # Create bank and slot frame that's only visible when saving
        self.save_frame = QGroupBox("Save Settings")
        save_layout = QVBoxLayout()
        self.save_frame.setLayout(save_layout)
        # self.save_frame.setVisible(False)  # Hidden by default
        
        # Add bank selector to save frame
        bank_row = QHBoxLayout()
        bank_row.addWidget(QLabel("Bank:"))
        self.bank_selector = QComboBox()
        self.bank_selector.addItems(['E', 'F', 'G', 'H'])  # Only show user banks
        bank_row.addWidget(self.bank_selector)
        save_layout.addLayout(bank_row)
        
        # Add slot selector to save frame
        slot_row = QHBoxLayout()
        slot_row.addWidget(QLabel("Slot:"))
        self.slot_selector = QComboBox()
        self.slot_selector.addItems([f"{i:02d}" for i in range(1, 65)])
        slot_row.addWidget(self.slot_selector)
        save_layout.addLayout(slot_row)
        
        # Create button row
        button_row = QHBoxLayout()
        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self._on_load_clicked)
        self.save_button = QPushButton("Save...")
        self.save_button.clicked.connect(self._toggle_save_frame)
        self.confirm_save_button = QPushButton("Confirm Save")
        self.confirm_save_button.clicked.connect(self._on_save_clicked)
        button_row.addWidget(self.load_button)
        button_row.addWidget(self.save_button)
        
        # Add buttons to layouts
        preset_layout.addLayout(button_row)
        save_layout.addWidget(self.confirm_save_button)
        
        # Add save frame to preset layout
        preset_layout.addWidget(self.save_frame)
        
        # Add preset group to main layout
        main_layout.addWidget(preset_group)
        
        # Set as central widget
        self.setCentralWidget(main_widget)
        
        # Adjust window size to fit content
        self.adjustSize()
        self.setFixedHeight(self.sizeHint().height())
        
        # Store the full preset list and mapping
        self.full_preset_list = self._get_preset_list()
        # Create mapping of display index to original index
        self.index_mapping = list(range(len(self.full_preset_list)))

    def _get_preset_list(self) -> List[str]:
        """Get the appropriate preset list based on type"""
        logging.debug(f"Getting preset list for type: {self.preset_type}")
        if self.preset_type == PresetType.ANALOG:
            return ANALOG_PRESETS
        elif self.preset_type == PresetType.DIGITAL_1:
            return DIGITAL_PRESETS
        else:  # PresetType.DRUMS
            return DRUM_PRESETS

    def _filter_presets(self, search_text: str):
        """Filter presets based on search text"""
        # Temporarily disconnect the signal
        self.preset_selector.currentIndexChanged.disconnect(self._on_preset_changed)
        
        if not search_text:
            # If search is empty, show all presets
            filtered_presets = self.full_preset_list
            self.index_mapping = list(range(len(self.full_preset_list)))
        else:
            # Filter presets that contain the search text (case-insensitive)
            search_text = search_text.lower()
            filtered_indices = [
                i for i, preset in enumerate(self.full_preset_list)
                if search_text in preset.lower()
            ]
            filtered_presets = [self.full_preset_list[i] for i in filtered_indices]
            self.index_mapping = filtered_indices
        
        # Update the preset selector with filtered items
        self.preset_selector.clear()
        self.preset_selector.addItems([
            preset.split(': ')[1] for preset in filtered_presets
        ])
        
        # Reconnect the signal and select first item if available
        self.preset_selector.currentIndexChanged.connect(self._on_preset_changed)
        if self.preset_selector.count() > 0:
            self.preset_selector.setCurrentIndex(0)

    def _update_preset_list(self):
        """Update the preset selector with appropriate list"""
        # Temporarily disconnect the signal to prevent -1 index
        self.preset_selector.currentIndexChanged.disconnect(self._on_preset_changed)
        
        self.full_preset_list = self._get_preset_list()
        # Reset the index mapping when updating preset list
        self.index_mapping = list(range(len(self.full_preset_list)))
        
        self.preset_selector.clear()
        self.preset_selector.addItems([
            preset.split(': ')[1] for preset in self.full_preset_list
        ])
        
        # Reconnect the signal
        self.preset_selector.currentIndexChanged.connect(self._on_preset_changed)

    def _on_type_changed(self, preset_type: str):
        """Handle preset type change"""
        logging.debug(f"Changing preset type to {preset_type}")
        self.preset_type = preset_type
        self.search_box.clear()  # Clear search when changing type
        # Update preset list and reset mapping
        self._update_preset_list()
        # Select first preset if available
        if self.preset_selector.count() > 0:
            self.preset_selector.setCurrentIndex(0)

    def _on_preset_changed(self, index: int):
        """Handle preset selection changes"""
        try:
            if index < 0 or index >= len(self.index_mapping):
                logging.warning(f"Invalid preset index {index}, max is {len(self.index_mapping)-1}")
                return
            
            if self.midi_helper:
                # Get the original index from the mapping
                original_index = self.index_mapping[index]
                logging.debug(f"Selected preset index {index} maps to original index {original_index}")
                
                # TODO: Add MIDI handling for preset changes using original_index
                pass
                
            # Get the preset name without the number prefix
            presets = self._get_preset_list()
            if original_index >= len(presets):
                logging.error(f"Original index {original_index} out of range for presets list (max {len(presets)-1})")
                return
            
            preset_name = presets[original_index].split(': ')[1]
            
            # Emit signal with all required information
            self.preset_changed.emit(
                original_index + 1,  # original preset number (1-based)
                preset_name,
                self.channel
            )
        except Exception as e:
            logging.error(f"Error in preset change handler: {str(e)}", exc_info=True)

    def _get_area_for_type(self) -> int:
        """Get MIDI area based on preset type"""
        if self.preset_type == PresetType.ANALOG:
            return ANALOG_SYNTH_AREA
        elif self.preset_type == PresetType.DIGITAL_1:
            return DIGITAL_SYNTH_AREA
        else:
            return DRUM_KIT_AREA

    def _on_load_clicked(self):
        """Handle Load button click"""
        current_index = self.preset_selector.currentIndex()
        PresetLoader.load_preset(
            self.midi_helper,
            self.preset_type,
            current_index + 1  # Convert to 1-based index
        )
        self.settings.setValue('last_preset/synth_type', self.preset_type)
        self.settings.setValue('last_preset/preset_num', current_index + 1)
        # self.settings.setValue('last_preset/channel', self.channel)

    def _toggle_save_frame(self):
        """Toggle visibility of save settings"""
        self.save_frame.setVisible(not self.save_frame.isVisible())
        if self.save_frame.isVisible():
            self.save_button.setText("Cancel Save")
        else:
            self.save_button.setText("Save...")

    def _on_save_clicked(self):
        """Handle Save button click"""
        if not self.midi_helper:
            QMessageBox.warning(self, "Error", "MIDI device not available")
            return

        try:
            bank = self.bank_selector.currentText()
            slot = int(self.slot_selector.currentText())
            
            # Confirm save operation
            reply = QMessageBox.question(
                self, 
                "Confirm Save",
                f"Save current {self.preset_type} preset to Bank {bank} Slot {slot}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return

            logging.debug(f"Saving {self.preset_type} preset to bank {bank} slot {slot}")

            # Convert bank letter to number (E=4, F=5, G=6, H=7)
            bank_num = ord(bank) - ord('A')
            
            # Calculate the appropriate area based on preset type
            area = PresetType.get_area_code(self.preset_type)

            # Send save command sequence
            # First message - Set bank and slot
            data = [0x18, 0x00, area, 0x06, bank_num]
            checksum = self._calculate_checksum(data)
            self.midi_helper.send_message([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                *data, checksum, 0xF7
            ])

            # Second message - Set slot number
            data = [0x18, 0x00, area, 0x07, slot - 1]  # Convert to 0-based index
            checksum = self._calculate_checksum(data)
            self.midi_helper.send_message([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                *data, checksum, 0xF7
            ])

            # Third message - Send save command
            data = [0x18, 0x00, area, 0x09, 0x00]  # 0x09 is save command
            checksum = self._calculate_checksum(data)
            self.midi_helper.send_message([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                *data, checksum, 0xF7
            ])

            QMessageBox.information(
                self,
                "Success",
                f"Successfully saved {self.preset_type} preset to Bank {bank} Slot {slot}"
            )
            
            # Hide save frame after successful save
            self._toggle_save_frame()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error saving preset: {str(e)}"
            )
            logging.error(f"Error saving {self.preset_type} preset: {str(e)}", exc_info=True)

    def request_current_parameters(self):
        """Request current parameters from the synth"""
        if self.midi_helper:
            PresetLoader.request_current_parameters(
                self.midi_helper,
                self.preset_type
            )
            
    def _update_ui(self, parameters: Dict[str, int]):
        """Update UI with new parameter values"""
        try:
            # Example: Update a label or control with a specific parameter
            # Assuming you have a QLabel or similar widget to display parameter values
            if '0.0.8' in parameters:  # Example address for a parameter
                value = parameters['0.0.8']
                self.some_label.setText(f"Parameter 0.0.8: {value}")

            # Update other UI elements as needed
            # if '0.1.0' in parameters:
            #     value = parameters['0.1.0']
            #     self.another_control.setValue(value)

        except Exception as e:
            logging.error(f"Error updating UI: {str(e)}", exc_info=True)