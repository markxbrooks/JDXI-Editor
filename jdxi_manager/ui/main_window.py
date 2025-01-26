import logging
import re
from pathlib import Path
from pubsub import pub

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QMessageBox, QLabel, QPushButton,
    QFrame, QGridLayout, QGroupBox, QButtonGroup
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QAction, QFont, QPixmap, QImage, QPainter, QPen, QColor, QFontDatabase

from jdxi_manager.data.analog import AN_PRESETS
from jdxi_manager.data.preset_data import ANALOG_PRESETS, DIGITAL_PRESETS, DRUM_PRESETS
from jdxi_manager.data.preset_type import PresetType
from jdxi_manager.ui.editors import (
    AnalogSynthEditor,
    DigitalSynthEditor,
    DrumEditor,
    ArpeggioEditor,
    EffectsEditor,
    VocalFXEditor
)
from jdxi_manager.ui.editors.preset_editor import PresetEditor
from jdxi_manager.ui.midi_config import MIDIConfigDialog
from jdxi_manager.ui.midi_debugger import MIDIDebugger
from jdxi_manager.ui.midi_message_debug import MIDIMessageDebug
from jdxi_manager.ui.patch_name_editor import PatchNameEditor
from jdxi_manager.ui.patch_manager import PatchManager
from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets.piano_keyboard import PianoKeyboard
from jdxi_manager.ui.widgets.channel_button import ChannelButton
from jdxi_manager.ui.widgets import MIDIIndicator, LogViewer, LEDIndicator
from jdxi_manager.ui.widgets.favorite_button import FavoriteButton, PresetFavorite
from jdxi_manager.midi import MIDIHelper, MIDIConnection
from jdxi_manager.midi.constants import (
    START_OF_SYSEX, ROLAND_ID, DEVICE_ID, MODEL_ID_1, MODEL_ID_2,
    MODEL_ID, JD_XI_ID, DT1_COMMAND_12, END_OF_SYSEX, ANALOG_SYNTH_AREA
)
from jdxi_manager.midi.messages import IdentityRequest
from jdxi_manager.midi.messages import ParameterMessage
from jdxi_manager.midi.preset_loader import PresetLoader
#from jdxi_manager.data.preset_favorite import PresetFavorite


def draw_jdxi(digital_font_family=None, current_octave=0, preset_num=1, preset_name="INIT PATCH"):
    """Create a QPixmap of the JD-Xi"""
    # Create a black background image with correct aspect ratio
    width = 1000
    height = 400
    image = QImage(width, height, QImage.Format_RGB32)
    image.fill(Qt.black)
    
    pixmap = QPixmap.fromImage(image)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Use smaller margins without border
    margin = 15
    
    # Define display position and size first
    display_x = margin + 20
    display_y = margin + 20
    display_width = 220
    display_height = 45
    
    # Title above display (moved down)
    title_x = display_x
    title_y = margin + 15
    painter.setPen(QPen(Qt.white))
    painter.setFont(QFont("Myriad Pro, Arial", 28, QFont.Bold))
    painter.drawText(title_x, title_y, "JD-Xi Manager")
    
    # LED display area (enlarged for 2 rows)
    display_x = margin + 20
    display_y = title_y + 30
    display_width = 215
    display_height = 70
    
    # Draw dark grey background for display
    painter.setBrush(QColor("#1A1A1A"))
    painter.setPen(QPen(QColor("#FF8C00"), 1))
    painter.drawRect(display_x, display_y, display_width, display_height)
    
    # Set up font for digital display
    if digital_font_family:
        display_font = QFont(digital_font_family, 16)
    else:
        display_font = QFont("Consolas", 12)
    painter.setFont(display_font)
    painter.setPen(QPen(QColor("#FF8C00")))  # Orange color for text
    
    # Draw preset number and name
    preset_text = f"{preset_num:03d}:{preset_name}"
    # Truncate if too long for display
    if len(preset_text) > 20:  # Adjust based on display width
        preset_text = preset_text[:19] + "…"
    text_y = display_y + 25
    painter.drawText(
        display_x + 10,
        text_y,
        preset_text
    )
    
    # Draw octave display below preset name
    oct_x = display_x + display_width - 60  # Position from right edge
    oct_y = text_y + 25  # Position below preset text
    
    # Format octave text
    if current_octave == 0:
        oct_text = "Octave 0"
    elif current_octave > 0:
        oct_text = f"Octave +{current_octave}"
    else:
        oct_text = f"Octave {current_octave}"
        
    painter.drawText(oct_x, oct_y, oct_text)
    
    # Load/Save buttons in display (without boxes)
    button_width = 70
    button_height = 25
    button_margin = 10
    button_y = display_y + (display_height - button_height*2 - button_margin) / 2
    
    # Load button (text only)
    load_x = display_x + button_margin
    painter.setPen(QPen(QColor("#FF8C00")))
    if digital_font_family:
        painter.setFont(QFont(digital_font_family, 22))
    else:
        painter.setFont(QFont("Consolas", 22))  # Fallback font
 
    
    # Save button (text only)
    save_x = display_x + button_margin

    
    # Keyboard section (moved up and taller)
    keyboard_width = 800
    keyboard_start = width - keyboard_width - margin - 20
    key_width = keyboard_width / 32  # Increased from 25 to 32 keys
    white_keys = 32  # Increased total white keys
    black_key_width = key_width * 0.6
    black_key_height = 80
    white_key_height = 127
    keyboard_y = height - white_key_height - (height * 0.1) + (white_key_height * 0.3)
    
    # Draw control sections
    section_margin = 40
    section_width = (keyboard_start - margin - section_margin) / 2
    section_height = 200
    section_y = margin + 100
    
    # Remove the red box borders for effects sections
    # (Delete or comment out these lines)
    """
    # Draw horizontal Effects section above keyboard
    effects_y = keyboard_y - 60  # Position above keyboard
    effects_width = 120  # Width for each section
    effects_height = 40
    effects_spacing = 20
    
    # Arpeggiator section
    arp_x = keyboard_start + (keyboard_width - (effects_width * 2 + effects_spacing)) / 2
    painter.drawRect(arp_x, effects_y, effects_width, effects_height)
    
    # Effects section
    fx_x = arp_x + effects_width + effects_spacing
    painter.drawRect(fx_x, effects_y, effects_width, effects_height)
    """
    
    # Draw sequencer section
    seq_y = keyboard_y - 50  # Keep same distance above keyboard
    seq_height = 30
    seq_width = keyboard_width * 0.5  # Use roughly half keyboard width
    seq_x = width - margin - 20 - seq_width  # Align with right edge of keyboard
    
    # Calculate step dimensions
    step_count = 16
    step_size = 20  # Smaller square size
    total_spacing = seq_width - (step_count * step_size)
    step_spacing = total_spacing / (step_count - 1)
    
    # Draw horizontal measure lines (white)
    painter.setPen(QPen(Qt.white, 1))
    line_y = seq_y - 10  # Move lines above buttons
    measure_width = (step_size + step_spacing) * 4  # Width of 4 steps
    line_spacing = step_size / 3  # Space between lines
    
    beats_list = [2, 3, 4]
    # Draw 4 separate measure lines
    for beats in beats_list:
        for measure in range(beats):
            measure_x = seq_x + measure * measure_width
            for i in range(beats):  # 2, 3 or 4 horizontal lines per measure
                y = line_y - 25 + i * line_spacing
                painter.drawLine(
                    int(measure_x),
                    int(y),
                    int(measure_x + measure_width - step_spacing),  # Stop before next measure
                    int(y)
                )

    
    # Draw sequence steps
    for i in range(step_count):
        x = seq_x + i * (step_size + step_spacing)
        
        # Draw step squares with double grey border
        painter.setPen(QPen(QColor("#666666"), 2))  # Mid-grey, doubled width
        painter.setBrush(Qt.black)  # All steps unlit
        
        painter.drawRect(
            int(x),
            seq_y,
            step_size,
            step_size
        )
    
    painter.end()
    return pixmap


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.channel = 1
        self.analog_editor = None
        self.last_preset = None
        self.preset_loader = None
        self.log_file = None
        self.setWindowTitle("JD-Xi Manager")
        self.setMinimumSize(1000, 400)
        # self.setMaximumSize(1000, 440)
        # Store window dimensions
        self.width = 1000
        self.height = 400
        self.margin = 15
        self.preset_type = PresetType.DIGITAL_1
        # Store display coordinates as class variables
        self.display_x = 35  # margin + 20
        self.display_y = 50  # margin + 20 + title height
        self.display_width = 180
        self.display_height = 70
        
        # Initialize state variables
        self.current_synth_type = PresetType.DIGITAL_1
        self.current_octave = 0  # Initialize octave tracking first
        self.current_preset_num = 1  # Initialize preset number
        self.current_preset_name = "JD Xi"  # Initialize preset name
        self.midi_in = None
        self.midi_out = None
        self.midi_in_port_name = ""  # Store input port name
        self.midi_out_port_name = ""  # Store output port name
        
        # Initialize MIDI helper
        self.midi_helper = MIDIHelper(parent=self)
        #self.preset_loader = PresetLoader(self.midi_helper)
        
        # Initialize windows to None
        self.log_viewer = None
        self.midi_debugger = None
        self.midi_message_debug = None
        
        # Try to auto-connect to JD-Xi
        self._auto_connect_jdxi()
        
        # Show MIDI config if auto-connect failed
        if not self.midi_helper.current_in_port or not self.midi_helper.current_out_port:
            self._show_midi_config()
        
        # Initialize MIDI indicators
        self.midi_in_indicator = MIDIIndicator()
        self.midi_out_indicator = MIDIIndicator()

        pub.subscribe(self._update_display_preset, "update_display_preset")
        
        # Set black background for entire application
        self.setStyleSheet(Style.JDXI_STYLE)
        
        # Load custom font
        self._load_digital_font()
        
        # Create UI
        self._create_menu_bar()
        self._create_status_bar()
        self._create_main_layout()
        
        # Load settings
        self.settings = QSettings("jdxi_manager2", "settings")
        self._load_settings()
        
        # Show window
        self.show()
        
        # Add debug menu
        debug_menu = self.menuBar().addMenu("Debug")
        
        # Add MIDI debugger action (SysEx decoder)
        midi_debugger_action = QAction("MIDI SysEx Debugger", self)
        midi_debugger_action.triggered.connect(self._open_midi_debugger)
        debug_menu.addAction(midi_debugger_action)
        
        # Add MIDI message monitor action
        midi_monitor_action = QAction("MIDI Monitor", self)
        midi_monitor_action.triggered.connect(self._open_midi_message_debug)
        debug_menu.addAction(midi_monitor_action)
        
        # Add log viewer action
        log_viewer_action = QAction("Log Viewer", self)
        log_viewer_action.triggered.connect(self._show_log_viewer)
        debug_menu.addAction(log_viewer_action)
        
        # Add preset tracking
        self.current_preset_num = 1
        self.current_preset_name = "INIT PATCH"
        
        # Add piano keyboard at bottom
        self.piano_keyboard = PianoKeyboard(parent=self)
        self.statusBar().addPermanentWidget(self.piano_keyboard)
        
        # Create display label
        self.display_label = QLabel()
        self.display_label.setMinimumSize(220, 100)  # Adjust size as needed
        
        # Initial display
        self._update_display_image()
        
        # Add display to layout
        if hasattr(self, 'main_layout'):
            self.main_layout.addWidget(self.display_label)
        
        # Create channel indicator
        self.channel_button = ChannelButton()
        
        # Add to status bar before piano keyboard
        self.statusBar().addPermanentWidget(self.channel_button)
        self.statusBar().addPermanentWidget(self.piano_keyboard)
        
        # Load last used preset settings
        self._load_last_preset()

        # Initialize synth type
        self.current_synth_type = PresetType.DIGITAL_1

        # Set default styles
        self._update_synth_button_styles()
        
        # Create favorite buttons container
        favorites_widget = QWidget()
        favorites_layout = QVBoxLayout(favorites_widget)
        favorites_layout.setSpacing(4)
        favorites_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create favorite buttons
        self.favorite_buttons = []
        for i in range(4):  # Create 4 favorite slots
            button = FavoriteButton(i, self.midi_helper)
            button.clicked.connect(lambda checked, b=button: self._load_favorite(b))
            button.setContextMenuPolicy(Qt.CustomContextMenu)
            button.customContextMenuRequested.connect(
                lambda pos, b=button: self._show_favorite_context_menu(pos, b)
            )
            favorites_layout.addWidget(button)
            self.favorite_buttons.append(button)
            
        # Add to status bar
        self.statusBar().addPermanentWidget(favorites_widget)
        self.statusBar().addPermanentWidget(self.channel_button)
        self.statusBar().addPermanentWidget(self.piano_keyboard)
        
        # Load saved favorites
        self._load_saved_favorites()
        
        # Create editors menu
        editors_menu = self.menuBar().addMenu("Editors")
        
        # Add menu items for each editor
        digital1_action = editors_menu.addAction("Digital Synth 1")
        digital1_action.triggered.connect(lambda: self.show_editor('digital1'))
        
        digital2_action = editors_menu.addAction("Digital Synth 2")
        digital2_action.triggered.connect(lambda: self.show_editor('digital2'))
        
        analog_action = editors_menu.addAction("Analog Synth")
        analog_action.triggered.connect(lambda: self.show_editor('analog'))
        
        drums_action = editors_menu.addAction("Drums")
        drums_action.triggered.connect(lambda: self.show_editor('drums'))
        
        arp_action = editors_menu.addAction("Arpeggio")
        arp_action.triggered.connect(lambda: self.show_editor('arpeggio'))
        
        effects_action = editors_menu.addAction("Effects")
        effects_action.triggered.connect(lambda: self.show_editor('effects'))
        
        # Add Vocal FX menu item
        vocal_fx_action = editors_menu.addAction("Vocal FX")
        vocal_fx_action.triggered.connect(lambda: self.show_editor('vocal_fx'))

        # Create Tone navigation buttons
        self.tone_down_button = QPushButton("-")
        self.tone_up_button = QPushButton("+")

        # Connect buttons to functions
        self.tone_down_button.clicked.connect(self._decrease_tone)
        self.tone_up_button.clicked.connect(self._increase_tone)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.tone_down_button)
        button_layout.addWidget(self.tone_up_button)
        button_layout.addStretch()



        # Add button layout to main layout
        #main_layout.addStretch()
        #main_layout.addLayout(button_layout)
        #main_layout.addStretch()

        # Initialize current preset index
        self.current_preset_index = 0

        # Initialize current preset index
        self.current_preset_index = 0

        # Example size for the arpeggiator button


        # Add buttons to layout
        #layout = QVBoxLayout()
        #layout.addWidget(self.tone_up_button)
        #layout.addWidget(self.tone_down_button)
        #self.setLayout(layout)

    def _select_synth(self, synth_type):
        """Select a synth and update button styles."""
        print(f"Selected synth: {synth_type}")
        self.current_synth_type = synth_type
        self._update_synth_button_styles()

    def _update_synth_button_styles(self):
        """Update styles for synth buttons based on selection."""
        buttons = {
            PresetType.ANALOG: self.analog_button,
            PresetType.DIGITAL_1: self.digital1_button,
            PresetType.DIGITAL_2: self.digital2_button,
            PresetType.DRUMS: self.drums_button
        }

        for synth_type, button in buttons.items():
            if synth_type == self.current_synth_type:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #333333;
                        border: 4px solid #d51e35;
                        border-radius: 15px;
                        padding: 0px;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #000000;
                        border: 4px solid #666666;
                        border-radius: 15px;
                        padding: 0px;
                    }
                """)

    def _decrease_tone(self):
        """Decrease the tone index and update the display."""
        if self.current_preset_index > 0:
            self.current_preset_index -= 1
            presets = DIGITAL_PRESETS
            if self.current_synth_type == PresetType.ANALOG:
                presets = AN_PRESETS
            elif self.current_synth_type == PresetType.DIGITAL_1:
                presets = DIGITAL_PRESETS
            elif self.current_synth_type == PresetType.DIGITAL_2:
                presets = DIGITAL_PRESETS
            elif self.current_synth_type == PresetType.DRUMS:
                presets = DRUM_PRESETS
            self._update_display_preset(self.current_preset_index, presets[self.current_preset_index], self.channel)
            preset_data = {
                'type': self.current_synth_type,  # Ensure this is a valid type
                'selpreset': self.current_preset_index + 1,  # Convert to 1-based index
                'modified': 0  # or 1, depending on your logic
            }
            self.load_preset(preset_data)

    def _increase_tone(self):
        """Increase the tone index and update the display."""
        if self.current_preset_index < len(DIGITAL_PRESETS) - 1:
            self.current_preset_index += 1
            presets = DIGITAL_PRESETS
            if self.preset_type == PresetType.ANALOG:
                presets = AN_PRESETS
            elif self.preset_type == PresetType.DIGITAL_1:
                presets = DIGITAL_PRESETS
            elif self.preset_type == PresetType.DIGITAL_2:
                presets = DIGITAL_PRESETS
            elif self.preset_type == PresetType.DRUMS:
                presets = DRUM_PRESETS
            self._update_display_preset(self.current_preset_index, presets[self.current_preset_index],
                                        self.channel)
            preset_data = {
                'type': self.preset_type,  # Ensure this is a valid type
                'selpreset': self.current_preset_index + 1,  # Convert to 1-based index
                'modified': 0  # or 1, depending on your logic
            }
            self.load_preset(preset_data)

    #def _update_display_preset(self):
    #    """Update the display with the current preset."""
    #    preset_name = DIGITAL_PRESETS[self.current_preset_index]
    #    print(f"Current Preset: {self.current_preset_index}: {preset_name}")


    def show_editor(self, editor_type: str):
        """Show the specified editor window"""
        # self.midi_helper = MIDIHelper(parent=self)
        try:
            if editor_type == 'vocal_fx':
                if not hasattr(self, 'vocal_fx_editor'):
                    self.vocal_fx_editor = VocalFXEditor(self.midi_helper, self)
                self.vocal_fx_editor.show()
                self.vocal_fx_editor.raise_()
            elif editor_type == 'digital1':
                self._show_editor("Digital Synth 1", DigitalSynthEditor, synth_num=1)
                self.preset_type = PresetType.DIGITAL_1
            elif editor_type == 'digital2':
                self._show_editor("Digital Synth 2", DigitalSynthEditor, synth_num=2)
                self.preset_type = PresetType.DIGITAL_2
            elif editor_type == 'analog':
                self._show_editor("Analog Synth", AnalogSynthEditor)
                self.preset_type = PresetType.ANALOG
            elif editor_type == 'drums':
                self._show_drums_editor()
                self.preset_type = PresetType.DRUMS
            elif editor_type == 'arpeggio':
                self._show_arpeggio_editor()
            elif editor_type == 'effects':
                self._open_effects()
            elif editor_type == 'vocal_fx':
                self._open_vocal_fx()
            
        except Exception as e:
            logging.error(f"Error showing {editor_type} editor: {str(e)}")

    def _create_main_layout(self):
        """Create the main dashboard"""
        central = QWidget()
        self.setCentralWidget(central)
        
        # Single layout to hold the image and overlays
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create container for image and overlays
        container = QWidget()
        container.setLayout(QVBoxLayout())
        container.layout().setContentsMargins(0, 0, 0, 0)
        
        # Store reference to image label
        self.image_label = QLabel()
        self.image_label.setPixmap(draw_jdxi(
            self.digital_font_family if hasattr(self, 'digital_font_family') else None,
            self.current_octave
        ))
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container.layout().addWidget(self.image_label)
        
        # Add overlaid controls
        self._add_overlaid_controls(container)
        
        layout.addWidget(container)

        # Initialize current preset index
        self.current_preset_index = 0

    def _create_tone_buttons_row(self):
        # Create Tone navigation buttons
        self.tone_label = QLabel("Tone")
        self.tone_down_button = QPushButton("-")
        self.spacer = QLabel(" ")
        self.tone_up_button = QPushButton("+")

        # Calculate size for tone buttons
        tone_button_diameter = 25

        # Create tone up button
        self.tone_up_button.setFixedSize(tone_button_diameter, tone_button_diameter)
        self.tone_up_button.setStyleSheet("""
            QPushButton {
                background-color: #333333;  /* Dark grey */
                border-radius: %dpx;  /* Half of the diameter for circular shape */
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #444444;  /* Slightly lighter grey on hover */
            }
            QPushButton:pressed {
                background-color: #555555;  /* Even lighter grey when pressed */
            }
        """ % (tone_button_diameter // 2))

        # Create tone down button
        # self.tone_down_button = QPushButton("-", self)
        self.tone_down_button.setFixedSize(tone_button_diameter, tone_button_diameter)
        self.tone_down_button.setStyleSheet("""
            QPushButton {
                background-color: #333333;  /* Dark grey */
                border-radius: %dpx;  /* Half of the diameter for circular shape */
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #444444;  /* Slightly lighter grey on hover */
            }
            QPushButton:pressed {
                background-color: #555555;  /* Even lighter grey when pressed */
            }
        """ % (tone_button_diameter // 2))

        # Connect buttons to functions
        self.tone_down_button.clicked.connect(self._decrease_tone)
        self.tone_up_button.clicked.connect(self._increase_tone)

        button_label_layout = QHBoxLayout()
        button_label_layout.addStretch()
        button_label_layout.addWidget(self.tone_label)
        button_label_layout.addStretch()
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.tone_down_button)
        button_layout.addWidget(self.spacer)
        button_layout.addWidget(self.tone_up_button)
        button_layout.addStretch()

        # Add button layout to main layout
        #layout.addStretch()
        #layout.addLayout(button_label_layout)
        #layout.addLayout(button_layout)
        #layout.addStretch()
        return button_layout


    def _create_section(self, title):
        """Create a section frame with title"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setMinimumHeight(150)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont(self.font().family(), 12, QFont.Bold))
        layout.addWidget(title_label)
        
        return frame

    def _create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        load_action = QAction("Load Patch...", self)
        load_action.triggered.connect(self._load_patch)
        file_menu.addAction(load_action)
        
        save_action = QAction("Save Patch...", self)
        save_action.triggered.connect(self._save_patch)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        midi_config_action = QAction("MIDI Configuration...", self)
        midi_config_action.triggered.connect(self._show_midi_config)
        edit_menu.addAction(midi_config_action)
        
        # Synth menu - reordered to match buttons
        synth_menu = menubar.addMenu("Synth")
        
        digital1_action = QAction("Digital Synth 1", self)
        digital1_action.triggered.connect(self._open_digital_synth1)
        synth_menu.addAction(digital1_action)
        
        digital2_action = QAction("Digital Synth 2", self)
        digital2_action.triggered.connect(self._open_digital_synth2)
        synth_menu.addAction(digital2_action)
        
        drums_action = QAction("Drums", self)
        drums_action.triggered.connect(self._open_drums)
        synth_menu.addAction(drums_action)
        
        analog_action = QAction("Analog Synth", self)
        analog_action.triggered.connect(self._open_analog_synth)
        synth_menu.addAction(analog_action)
        
        # Effects menu
        fx_menu = menubar.addMenu("Effects")
        
        arp_action = QAction("Arpeggiator", self)
        arp_action.triggered.connect(self._open_arpeggiator)
        fx_menu.addAction(arp_action)
        
        effects_action = QAction("Effects", self)
        effects_action.triggered.connect(self._open_effects)
        fx_menu.addAction(effects_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        log_viewer_action = QAction("Log Viewer", self)
        log_viewer_action.triggered.connect(self._show_log_viewer)
        help_menu.addAction(log_viewer_action)
        
        # Add Edit menu
        # edit_menu = menubar.addMenu("Edit")
        
        # Add Patch Name action
        edit_name_action = QAction("Edit Patch Name", self)
        edit_name_action.triggered.connect(self._edit_patch_name)
        edit_menu.addAction(edit_name_action)
        
        # Add Presets menu
        # presets_menu = self.menuBar().addMenu("&Presets")
        
        presets_action = edit_menu.addAction("&Presets")
        presets_action.triggered.connect(self._show_analog_presets)
        
    def _create_status_bar(self):
        """Create status bar with MIDI indicators"""
        status_bar = self.statusBar()
        
        # Create MIDI indicators
        self.midi_in_indicator = LEDIndicator()
        self.midi_out_indicator = LEDIndicator()
        
        # Add labels and indicators
        status_bar.addPermanentWidget(QLabel("MIDI IN:"))
        status_bar.addPermanentWidget(self.midi_in_indicator)
        status_bar.addPermanentWidget(QLabel("MIDI OUT:"))
        status_bar.addPermanentWidget(self.midi_out_indicator)
        
        # Set initial indicator states
        self.midi_in_indicator.set_state(self.midi_helper.is_input_open)
        self.midi_out_indicator.set_state(self.midi_helper.is_output_open)
        
    def _show_midi_config(self):
        """Show MIDI configuration dialog"""
        try:
            # Get available ports using instance method
            input_ports = self.midi_helper.get_input_ports()  # Use instance method
            output_ports = self.midi_helper.get_output_ports()  # Use instance method
            
            dialog = MIDIConfigDialog(
                input_ports,
                output_ports,
                self.midi_helper.current_in_port,
                self.midi_helper.current_out_port,
                parent=self
            )
            
            if dialog.exec():
                in_port = dialog.get_input_port()
                out_port = dialog.get_output_port()
                
                # Open selected ports using instance methods
                if in_port:
                    self.midi_helper.open_input_port(in_port)
                if out_port:
                    self.midi_helper.open_output_port(out_port)
                    
        except Exception as e:
            logging.error(f"Error showing MIDI configuration: {str(e)}")
            self.show_error("MIDI Configuration Error", str(e))
        
    def _update_midi_ports(self, midi_in, midi_out):
        """Update MIDI port connections"""
        self.midi_in = midi_in
        self.midi_out = midi_out
        
        # Save settings
        if midi_in and midi_out:
            self.settings.setValue("midi/input_port", midi_in.port_name)
            self.settings.setValue("midi/output_port", midi_out.port_name)
            
    def _load_settings(self):
        """Load application settings"""
        try:
            if hasattr(self, 'settings'):
                # Load MIDI port settings
                input_port = self.settings.value("midi_in", "")
                output_port = self.settings.value("midi_out", "")
                
                # Load window geometry
                geometry = self.settings.value("geometry")
                if geometry:
                    self.restoreGeometry(geometry)
                    
                # Load preset info
                self.current_preset_num = int(self.settings.value("preset_num", 1))
                self.current_preset_name = self.settings.value("preset_name", "INIT PATCH")
                
                # Try to open MIDI ports if they were saved
                if input_port and output_port:
                    self._set_midi_ports(input_port, output_port)
                    
                logging.debug("Settings loaded successfully")
                
        except Exception as e:
            logging.error(f"Error loading settings: {str(e)}")

    def _show_editor(self, title, editor_class, **kwargs):
        """Show editor window"""
        try:
            # Create editor with proper initialization
            if editor_class in [DigitalSynthEditor, DrumEditor, AnalogSynthEditor]:
                editor = editor_class(
                    midi_helper=self.midi_helper,
                    parent=self,
                    **kwargs
                )
            else:
                # For other editors, use existing initialization
                editor = editor_class(midi_out=self.midi_out, **kwargs)
                
            # Set window title
            editor.setWindowTitle(title)
            
            # Store reference and show
            if title == "Digital Synth 1":
                self.digital_synth1 = editor
            elif title == "Digital Synth 2":
                self.digital_synth2 = editor
            elif title == "Analog Synth":
                self.analog_synth = editor
            elif title == "Drum Kit":
                self.drum_kit = editor
            elif title == "Effects":
                self.effects = editor
                
            # Show editor
            editor.show()
            editor.raise_()
            
        except Exception as e:
            logging.error(f"Error showing {title} editor: {str(e)}")
        
    def _handle_midi_input(self, message, timestamp):
        """Handle incoming MIDI messages and flash indicator"""
        self.midi_in_indicator.flash()
        
    def _open_analog_synth(self):
        self._show_editor("Analog Synth", AnalogSynthEditor)
        self.preset_type = PresetType.ANALOG
        
    def _open_digital_synth1(self):
        self._show_editor("Digital Synth 1", DigitalSynthEditor, synth_num=1)
        self.preset_type = PresetType.DIGITAL_1
        
    def _open_digital_synth2(self):
        self._show_editor("Digital Synth 2", DigitalSynthEditor, synth_num=2)
        self.preset_type = PresetType.DIGITAL_2
        
    def _open_drums(self):
        self._show_drums_editor()
        self.preset_type = PresetType.DRUMS
        
    def _open_arpeggiator(self):
        """Show the arpeggiator editor window"""
        try:
            if not hasattr(self, 'arpeggiator'):
                self.arpeggiator = ArpeggioEditor(
                    midi_helper=self.midi_helper,  # Pass midi_helper instance
                    parent=self
                )
            self.arpeggiator.show()
            self.arpeggiator.raise_()
            
        except Exception as e:
            logging.error(f"Error showing Arpeggiator editor: {str(e)}")
        
    def _open_effects(self):
        """Show the effects editor window"""
        try:
            if not hasattr(self, 'effects_editor'):
                self.effects_editor = EffectsEditor(
                    midi_helper=self.midi_helper,  # Pass midi_helper instead of midi_out
                    parent=self
                )
            self.effects_editor.show()
            self.effects_editor.raise_()
            
        except Exception as e:
            logging.error(f"Error showing Effects editor: {str(e)}")
        
    def _load_patch(self):
        """Show load patch dialog"""
        try:
            patch_manager = PatchManager(
                midi_helper=self.midi_helper,
                parent=self,
                save_mode=False
            )
            patch_manager.show()
        except Exception as e:
            logging.error(f"Error loading patch: {str(e)}")

    def _save_patch(self):
        """Show save patch dialog"""
        try:
            patch_manager = PatchManager(
                midi_helper=self.midi_helper,
                parent=self,
                save_mode=True
            )
            patch_manager.show()
        except Exception as e:
            logging.error(f"Error saving patch: {str(e)}")

    def _apply_patch(self, patch_data):
        """Apply loaded patch data"""
        # TODO: Implement patch loading
        pass
        
    def closeEvent(self, event):
        """Handle window close event"""
        try:
            # Properly delete MIDI ports
            if self.midi_in:
                self.midi_in.delete()  # Use delete() instead of close()
            if self.midi_out:
                self.midi_out.delete()  # Use delete() instead of close()
            
            # Save settings
            self._save_settings()
            
            # Accept the event
            event.accept()
            
        except Exception as e:
            logging.error(f"Error during close event: {str(e)}")
            event.ignore()

    def set_log_file(self, log_file: str):
        """
        :param log_file: str
        """
        self.log_file = log_file

    def _show_log_viewer(self):
        """Show log viewer window"""
        if not self.log_viewer:
            self.log_viewer = LogViewer(midi_helper=self.midi_helper, parent=self)
        self.log_viewer.show()
        self.log_viewer.raise_()
        logging.debug("Showing LogViewer window")
        
    def _create_button_row(self, text, slot):
        """Create a row with label and circular button"""
        row = QHBoxLayout()
        row.setSpacing(10)
        
        # Add label with color based on text
        label = QLabel(text)
        if text == "Analog Synth":
            label.setStyleSheet("""
                font-family: "Myriad Pro", Arial;
                font-size: 13px;
                color: #00A0E9;  /* Blue for Analog */
                font-weight: bold;
            """)
        else:
            label.setStyleSheet("""
                font-family: "Myriad Pro", Arial;
                font-size: 13px;
                color: #d51e35;  /* Base red */
                font-weight: bold;
            """)
        row.addWidget(label)
        
        # Add spacer to push button to right
        row.addStretch()
        
        # Add button
        button = QPushButton()
        button.setFixedSize(30, 30)
        button.setCheckable(True)
        button.clicked.connect(slot)
        
        # Style the button with brighter hover/pressed/selected  states
        button.setStyleSheet("""
            QPushButton {
                background-color: black;
                border: 4px solid #666666;
                border-radius: 15px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #1A1A1A;
                border-color: #ff4d4d;
            }
            QPushButton:pressed {
                background-color: #333333;
                border-color: #ff6666;
            }
            QPushButton:checked {
                background-color: black;
                border: 4px solid #d51e35;
                border-radius: 15px;
                padding: 0px;
            }
        """)
        
        row.addWidget(button)
        return row, button

    def add_arpeggiator_buttons(self, widget):
        """Add arpeggiator up/down buttons to the interface"""
        # Create container
        arpeggiator_buttons_container = QWidget(widget)

        # Position to align with sequencer but 25% higher (increased from 20%)
        seq_y = self.height - 50 - self.height * 0.1  # Base sequencer Y position
        offset_y = self.height * 0.25  # 25% of window height (increased from 0.2)
        arpeggiator_x = self.width - self.width * 0.8 - 60  # Position left of sequencer

        # Apply the height offset to the Y position
        arpeggiator_buttons_container.setGeometry(
            arpeggiator_x,
            seq_y - 60 - offset_y,  # Move up by offset_y (now 25% instead of 20%)
            100,
            100
        )

        arpeggiator_layout = QVBoxLayout(arpeggiator_buttons_container)
        arpeggiator_layout.setSpacing(5)

        # Add "ARPEGGIO" label at the top
        arpeggiator_label = QLabel("ARPEGGIO")
        arpeggiator_label.setStyleSheet("""
            font-family: "Myriad Pro", Arial;
            font-size: 14px;
            color: #d51e35;
            font-weight: bold;
            background: transparent;
        """)
        arpeggiator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arpeggiator_layout.addWidget(arpeggiator_label)

        # Create horizontal layout for Down/Up labels
        labels_row = QHBoxLayout()
        labels_row.setSpacing(20)  # Space between labels

        # On label
        on_label = QLabel("On")
        on_label.setStyleSheet("""
            font-family: "Myriad Pro", Arial;
            font-size: 13px;
            color: #d51e35;
            font-weight: bold;
        """)
        labels_row.addWidget(on_label)

        # Add labels row
        arpeggiator_layout.addLayout(labels_row)

        # Create horizontal layout for buttons
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(20)  # Space between buttons

        # Down label
        key_hold_label = QLabel("Key Hold")
        key_hold_label.setStyleSheet("""
            font-family: "Myriad Pro", Arial;
            font-size: 13px;
            color: #d51e35;
            font-weight: bold;
        """)
        labels_row.addWidget(key_hold_label)

        # Create and store arpeggiator  button
        self.arpeggiator_button = QPushButton()
        self.arpeggiator_button.setFixedSize(30, 30)
        self.arpeggiator_button.setCheckable(True)
        self.arpeggiator_button.clicked.connect(
            lambda checked: self._send_arp_on_off(checked)
        )
        self.arpeggiator_button.setStyleSheet("""
            QPushButton {
                background-color: black;
                border: 4px solid #d51e35;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #1A1A1A;
                border-color: #ff4d4d;
            }
            QPushButton:pressed, QPushButton:checked {
                background-color: #333333;
                border-color: #ff6666;
            }
        """)
        buttons_row.addWidget(self.arpeggiator_button)

        # Create and store octave down button
        self.key_hold = QPushButton()
        self.key_hold.setFixedSize(30, 30)
        self.key_hold.setCheckable(True)
        self.key_hold.clicked.connect(
            lambda checked: self._send_arp_key_hold(checked)
        )
        self.key_hold.setStyleSheet("""
            QPushButton {
                background-color: black;
                border: 4px solid #d51e35;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #1A1A1A;
                border-color: #ff4d4d;
            }
            QPushButton:pressed, QPushButton:checked {
                background-color: #333333;
                border-color: #ff6666;
            }
        """)
        buttons_row.addWidget(self.key_hold)

        # Add buttons row
        arpeggiator_layout.addLayout(buttons_row)

        # Make container transparent
        arpeggiator_buttons_container.setStyleSheet("background: transparent;")

    def add_octave_buttons(self, widget):
        """Add octave up/down buttons to the interface"""
        # Create container
        octave_buttons_container = QWidget(widget)
        
        # Position to align with sequencer but 25% higher (increased from 20%)
        seq_y = self.height - 50 - self.height * 0.1  # Base sequencer Y position
        offset_y = self.height * 0.25  # 25% of window height (increased from 0.2)
        octave_x = self.width - self.width * 0.8 - 150  # Position left of sequencer
        
        # Apply the height offset to the Y position
        octave_buttons_container.setGeometry(
            octave_x, 
            seq_y - 60 - offset_y,  # Move up by offset_y (now 25% instead of 20%)
            100, 
            100
        )
        
        octave_layout = QVBoxLayout(octave_buttons_container)
        octave_layout.setSpacing(5)


        # Create horizontal layout for Down/Up labels
        labels_row = QHBoxLayout()
        labels_row.setSpacing(20)  # Space between labels

        # Add "OCTAVE" label at the top
        octave_label = QLabel("OCTAVE")
        octave_label.setStyleSheet("""
            font-family: "Myriad Pro", Arial;
            font-size: 14px;
            color: #d51e35;
            font-weight: bold;
            background: transparent;
        """)
        octave_label.setAlignment(Qt.AlignCenter)
        octave_layout.addWidget(octave_label)
        
        # Down label
        down_label = QLabel("Down")
        down_label.setStyleSheet("""
            font-family: "Myriad Pro", Arial;
            font-size: 13px;
            color: #d51e35;
            font-weight: bold;
        """)
        labels_row.addWidget(down_label)

        # Up label
        up_label = QLabel("Up")
        up_label.setStyleSheet("""
            font-family: "Myriad Pro", Arial;
            font-size: 13px;
            color: #d51e35;
            font-weight: bold;
        """)
        labels_row.addWidget(up_label)
        
        # Add labels row
        octave_layout.addLayout(labels_row)

        # Create horizontal layout for buttons
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(20)  # Space between buttons
        
        # Create and store octave down button
        self.octave_down = QPushButton()
        self.octave_down.setFixedSize(30, 30)
        self.octave_down.setCheckable(True)
        self.octave_down.clicked.connect(lambda: self._send_octave(-1))
        self.octave_down.setStyleSheet("""
            QPushButton {
                background-color: black;
                border: 4px solid #d51e35;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #1A1A1A;
                border-color: #ff4d4d;
            }
            QPushButton:pressed, QPushButton:checked {
                background-color: #333333;
                border-color: #ff6666;
            }
        """)
        buttons_row.addWidget(self.octave_down)
        
        # Create and store octave up button
        self.octave_up = QPushButton()
        self.octave_up.setFixedSize(30, 30)
        self.octave_up.setCheckable(True)
        self.octave_up.clicked.connect(lambda: self._send_octave(1))
        self.octave_up.setStyleSheet("""
            QPushButton {
                background-color: black;
                border: 4px solid #d51e35;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #1A1A1A;
                border-color: #ff4d4d;
            }
        """)
        buttons_row.addWidget(self.octave_up)

        # Add buttons row
        octave_layout.addLayout(buttons_row)

        # Make container transparent
        octave_buttons_container.setStyleSheet("background: transparent;")

    def _add_overlaid_controls(self, widget):
        """Add interactive controls overlaid on the JD-Xi image"""
        # Create absolute positioning layout
        widget.setLayout(QVBoxLayout())
        
        # Parts Select section with Arpeggiator
        parts_container = QWidget(widget)
        parts_x = self.display_x + self.display_width + 30
        parts_y = self.display_y - (self.height * 0.15)  # Move up by 20% of window height
        
        parts_container.setGeometry(parts_x, parts_y, 220, 250)
        parts_layout = QVBoxLayout(parts_container)
        parts_layout.setSpacing(15)  # Increased from 5 to 15 for more vertical spacing
        
        # Add Parts Select label
        parts_label = QLabel("Parts Select")
        parts_label.setStyleSheet("""
            font-family: "Myriad Pro", Arial;
            font-size: 14px;
            color: #d51e35;
            font-weight: bold;
            background: transparent;
            padding-bottom: 10px;
        """)
        parts_label.setAlignment(Qt.AlignCenter)
        parts_layout.addWidget(parts_label)
        
        # Parts buttons
        digital1_row, self.digital1_button = self._create_button_row("Digital Synth 1", self._open_digital_synth1)
        digital2_row, self.digital2_button  = self._create_button_row("Digital Synth 2", self._open_digital_synth2)
        drums_row, self.drums_button = self._create_button_row("Drums", self._open_drums)
        analog_row, self.analog_button = self._create_button_row("Analog Synth", self._open_analog_synth)
        arp_row, self.arp_button = self._create_button_row("Arpeggiator", self._open_arpeggiator)

        self.analog_button.clicked.connect(lambda: self._select_synth(PresetType.ANALOG))
        self.digital1_button.clicked.connect(lambda: self._select_synth(PresetType.DIGITAL_1))
        self.digital2_button.clicked.connect(lambda: self._select_synth(PresetType.DIGITAL_2))
        self.drums_button.clicked.connect(lambda: self._select_synth(PresetType.DRUMS))

        # Create a button group
        button_group = QButtonGroup()
        button_group.addButton(self.digital1_button)
        button_group.addButton(self.digital2_button)
        button_group.addButton(self.analog_button)
        button_group.addButton(self.drums_button)

        # Ensure only one button can be checked at a time
        button_group.setExclusive(True)

        parts_layout.addLayout(digital1_row)
        parts_layout.addLayout(digital2_row)
        parts_layout.addLayout(drums_row)
        parts_layout.addLayout(analog_row)
        parts_layout.addLayout(arp_row)

        self.add_octave_buttons(widget)
        self.add_arpeggiator_buttons(widget)

        # Effects button in top row
        fx_container = QWidget(widget)
        fx_container.setGeometry(self.width - 200, self.margin + 25, 150, 50)
        fx_layout = QHBoxLayout(fx_container)
        
        effects_row, self.effects_button = self._create_button_row("Effects", self._open_effects)
        fx_layout.addLayout(effects_row)

        ###### For tone buttons ######
        # Effects button in top row
        tone_container = QWidget(widget)
        tone_container.setGeometry(self.width - 525, self.margin + 15, 150, 100)
        tone_container_layout = QVBoxLayout(tone_container)
        tone_label_layout = QHBoxLayout()
        tone_label = QLabel("Tone")
        tone_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tone_label.setStyleSheet("""
            font-family: "Myriad Pro", Arial;
            font-size: 14px;
            color: #d51e35;
            font-weight: bold;
            background: transparent;
        """)
        tone_label_layout.addWidget(tone_label)
        tone_container_layout.addLayout(tone_label_layout)
        tone_layout = QHBoxLayout()
        tone_row = self._create_tone_buttons_row()
        tone_layout.addLayout(tone_row)
        tone_container_layout.addLayout(tone_layout)
        
        # Make containers transparent
        parts_container.setStyleSheet("background: transparent;")
        fx_container.setStyleSheet("background: transparent;") 
        
        # Calculate keyboard dimensions
        key_width = self.width * 0.8 / 25  # keyboard_width/25
        key_height = 127  # white_key_height
        keyboard_y = self.height - key_height - (self.height * 0.1) + (key_height * 0.3)
        keyboard_start = self.width - (self.width * 0.8) - self.margin - 20
        
        # Add white keys C1 to F5
        white_notes = [
            36, 38, 40, 41, 43, 45, 47,  # C1 to B1
            48, 50, 52, 53, 55, 57, 59,  # C2 to B2
            60, 62, 64, 65, 67, 69, 71,  # C3 to B3
            72, 74, 76, 77, 79, 81, 83,  # C4 to B4
            84, 86, 88, 89              # C5 to F5
        ]
        
        #for i, note in enumerate(white_notes):
        #    x_pos = keyboard_start + i * key_width
        #    self._add_piano_key(widget, False, note, x_pos, keyboard_y, key_width, key_height)
            
        # Add black keys
        black_notes = [
            37, 39, None, 42, 44, 46,     # C#1 to B1
            49, 51, None, 54, 56, 58,     # C#2 to B2
            61, 63, None, 66, 68, 70,     # C#3 to B3
            73, 75, None, 78, 80, 82,     # C#4 to B4
            85, 87, None, 90              # C#5 to F#5
        ]
        
        black_positions = [0, 1, 3, 4, 5, 7, 8, 10, 11, 12, 14, 15, 17, 18, 19, 
                         21, 22, 24, 25, 26, 28, 29, 31, 32]  # Extended positions
        
        #for pos, note in zip(black_positions, [n for n in black_notes if n is not None]):
        #    x_pos = keyboard_start + pos * key_width + key_width/2
        #    self._add_piano_key(widget, True, note, x_pos, keyboard_y, key_width, key_height)
        
    def _add_piano_key(self, widget, is_black, note_number, x_pos, keyboard_y, key_width, key_height):
        """Helper to create a piano key button"""
        button = QPushButton(widget)
        
        if is_black:
            width = key_width * 0.6
            height = 80
            style = """
                QPushButton {
                    background-color: black;
                    border: 1px solid black;
                    border-radius: 0px;
                }
                QPushButton:hover {
                    background-color: #1a1a1a;
                }
                QPushButton:pressed {
                    background-color: #333333;
                }
            """
        else:
            width = key_width - 1
            height = key_height
            style = """
                QPushButton {
                    background-color: white;
                    border: 1px solid black;
                    border-radius: 0px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
                QPushButton:pressed {
                    background-color: #e0e0e0;
                }
            """
            
        button.setGeometry(
            int(x_pos),
            int(keyboard_y),
            int(width),
            int(height)
        )
        button.setStyleSheet(style)
        
        def key_pressed():
            if self.midi_out:
                self.midi_out.send_message([0x90, note_number, 1])  # Note On
                logging.debug(f"Sent MIDI Note On {note_number} velocity 1")
        
        def key_released():
            if self.midi_out:
                self.midi_out.send_message([0x80, note_number, 5])  # Note Off
                logging.debug(f"Sent MIDI Note Off {note_number} velocity 5")
        
        # Connect to mouse events instead of clicked
        button.pressed.connect(key_pressed)
        button.released.connect(key_released) 
        
    def _send_octave(self, direction):
        """Send octave change MIDI message"""
        if self.midi_helper:
            # Update octave tracking
            self.current_octave = max(-3, min(3, self.current_octave + direction))
            
            # Update button states
            self.octave_down.setChecked(self.current_octave < 0)
            self.octave_up.setChecked(self.current_octave > 0)
            
            # Update display
            self._update_display()
            
            # Map octave value to correct SysEx value
            # -3 = 0x3D, -2 = 0x3E, -1 = 0x3F, 0 = 0x40, +1 = 0x41, +2 = 0x42, +3 = 0x43
            octave_value = 0x40 + self.current_octave  # 0x40 is center octave
            
            # Calculate checksum
            checksum = (0x19 + 0x01 + 0x00 + 0x15 + octave_value)
            checksum = (0x80 - (checksum & 0x7F)) & 0x7F
            
            # Create SysEx message
            sysex_msg = [
                0xF0,   # Start of SysEx
                0x41,   # Roland ID
                0x10,   # Device ID
                0x00, 0x00, 0x00, 0x0E,  # Model ID
                0x12,   # Command ID (DT1)
                0x19,   # Address 1
                0x01,   # Address 2
                0x00,   # Address 3
                0x15,   # Address 4
                octave_value,  # Parameter value
                checksum,  # Checksum
                0xF7    # End of SysEx
            ]
            
            self.midi_helper.send_message(sysex_msg)
            logging.debug(f"Sent octave change SysEx, new octave: {self.current_octave} (value: {hex(octave_value)})")

    def _create_other(self):
        """Create other controls section"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        
        # Create buttons for Effects and Vocal FX
        others = [
            ("Effects", self._open_effects),
            ("Vocal FX", self._open_vocal_fx),
        ]
        
        for text, slot in others:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.clicked.connect(slot)
            layout.addWidget(btn)
        
        # Create horizontal layout for Arpeggiator
        arp_row = QHBoxLayout()
        
        # Arpeggiator button
        arp_btn = QPushButton("Arpeggio")
        arp_btn.setFixedHeight(40)
        arp_btn.clicked.connect(self._open_arpeggiator)
        arp_row.addWidget(arp_btn)
        
        # Add the horizontal row to the main layout
        layout.addLayout(arp_row)
        
        # Add stretch at the bottom
        layout.addStretch()
        
        return frame 

    def _update_display(self):
        """Update the JD-Xi display image"""
        pixmap = draw_jdxi(
            digital_font_family=self.digital_font_family if hasattr(self, 'digital_font_family') else None,
            current_octave=self.current_octave,
            preset_num=self.current_preset_num,
            preset_name=self.current_preset_name
        )
        if hasattr(self, 'image_label'):
            self.image_label.setPixmap(pixmap) 

    def _load_digital_font(self):
        """Load the digital LCD font for the display"""
        import os
        font_name = "JdLCD.ttf"
        font_path = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "fonts", font_name)
        if os.path.exists(font_path):
            logging.debug(f"Found file, Loading {font_name}font from {font_path}")
            try:
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id < 0:
                    logging.debug("Error loading {font_name} font")
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    self.digital_font_family = font_families[0]
                    logging.debug(f"Successfully loaded font family: {self.digital_font_family}")
                else:
                    logging.debug("No font families found after loading font")
            except Exception as e:
                logging.exception(f"Error loading {font_name} font from {font_path}: {e}")
        else:
            logging.debug(f"File not found: {font_path}") 

    def _send_arp_key_hold(self, state):
        """Send arpeggiator key hold (latch) command"""
        try:
            if self.midi_helper:
                # Value: 0 = OFF, 1 = ON
                value = 0x01 if state else 0x00
                
                # Create SysEx message using constants
                sysex_msg = [
                    START_OF_SYSEX,
                    ROLAND_ID,
                    DEVICE_ID,
                    MODEL_ID_1, MODEL_ID_2, MODEL_ID, JD_XI_ID,
                    DT1_COMMAND_12,
                    0x15,   # Arpeggio area
                    0x00,   # Subgroup
                    0x00,   # Part
                    0x02,   # Key Hold parameter
                    value,  # Parameter value
                ]
                
                # Calculate checksum (sum all data bytes)
                checksum = sum(sysex_msg[8:-1]) & 0x7F  # From address to value
                checksum = (128 - checksum) & 0x7F
                
                # Add checksum and end of sysex
                sysex_msg.extend([checksum, END_OF_SYSEX])
                
                # Send message
                self.midi_helper.send_message(bytes(sysex_msg))
                logging.debug(f"Sent arpeggiator key hold: {'ON' if state else 'OFF'}")
                
        except Exception as e:
            logging.error(f"Error sending arp key hold: {str(e)}")

    def _send_arp_on_off(self, state):
        """Send arpeggiator on/off command"""
        try:
            if self.midi_helper:
                # Value: 0 = OFF, 1 = ON
                value = 0x01 if state else 0x00
                
                # Create SysEx message using constants
                sysex_msg = [
                    START_OF_SYSEX,
                    ROLAND_ID,
                    DEVICE_ID,
                    MODEL_ID_1, MODEL_ID_2, MODEL_ID, JD_XI_ID,
                    DT1_COMMAND_12,
                    0x15,   # Arpeggio area
                    0x00,   # Subgroup
                    0x00,   # Part
                    0x00,   # On/Off parameter
                    value,  # Parameter value
                ]
                
                # Calculate checksum (sum all data bytes)
                checksum = sum(sysex_msg[8:-1]) & 0x7F  # From address to value
                checksum = (128 - checksum) & 0x7F
                
                # Add checksum and end of sysex
                sysex_msg.extend([checksum, END_OF_SYSEX])
                
                # Send message
                self.midi_helper.send_message(bytes(sysex_msg))
                logging.debug(f"Sent arpeggiator on/off: {'ON' if state else 'OFF'}")
                
        except Exception as e:
            logging.error(f"Error sending arp on/off: {str(e)}")

    def _open_midi_debugger(self):
        """Open MIDI debugger window"""
        if not self.midi_helper:
            logging.error("MIDI helper not initialized")
            return
        """    
        if not self.midi_helper.midi_out:
            logging.warning("No MIDI output port set")
            # Show MIDI config dialog
            self._show_midi_config()
            return
        """    
        if not self.midi_debugger:
            self.midi_debugger = MIDIDebugger(self.midi_helper)
            # Clean up reference when window is closed
            self.midi_debugger.setAttribute(Qt.WA_DeleteOnClose)
            self.midi_debugger.destroyed.connect(self._midi_debugger_closed)
            logging.debug("Created new MIDI debugger window")
        self.midi_debugger.show()
        self.midi_debugger.raise_()
        
    def _midi_debugger_closed(self):
        """Handle MIDI debugger window closure"""
        self.midi_debugger = None
        
    def _open_log_viewer(self):
        """Show log viewer window"""
        if not self.log_viewer:
            self.log_viewer = LogViewer(midi_helper=self.midi_helper, parent=self)
        self.log_viewer.show()
        self.log_viewer.raise_()
        logging.debug("Showing LogViewer window")
        
    def _log_viewer_closed(self):
        """Handle log viewer window closure"""
        self.log_viewer = None 

    def _set_midi_ports(self, in_port, out_port):
        """Set MIDI input and output ports"""
        try:
            # Close existing ports
            if self.midi_in:
                self.midi_in.delete()  # Use delete() instead of close()
            if self.midi_out:
                self.midi_out.delete()  # Use delete() instead of close()

            # Open new ports
            self.midi_in = MIDIHelper.open_input(in_port, self)
            self.midi_out = MIDIHelper.open_output(out_port, self)
            
            # Store port names
            self.midi_in_port_name = in_port
            self.midi_out_port_name = out_port
            
            # Initialize singleton connection
            MIDIConnection().initialize(self.midi_in, self.midi_out, self)
            
            # Update MIDI helper
            self.midi_helper.midi_in = self.midi_in
            self.midi_helper.midi_out = self.midi_out
            
            # Set up MIDI input callback
            if self.midi_in:
                self.midi_in.set_callback(self._handle_midi_message)
            
            # Update indicators
            self.midi_in_indicator.set_active(self.midi_in is not None)
            self.midi_out_indicator.set_active(self.midi_out is not None)
            
            # Save settings
            if self.midi_in and self.midi_out:
                self.settings.setValue("midi_in", in_port)
                self.settings.setValue("midi_out", out_port)
                logging.info(f"MIDI ports configured - In: {in_port}, Out: {out_port}")
            else:
                logging.warning("Failed to configure MIDI ports")
                
        except Exception as e:
            logging.error(f"Error setting MIDI ports: {str(e)}")

    def _open_midi_message_debug(self):
        """Open MIDI message debug window"""
        if not self.midi_message_debug:
            self.midi_message_debug = MIDIMessageDebug()
            self.midi_message_debug.setAttribute(Qt.WA_DeleteOnClose)
            self.midi_message_debug.destroyed.connect(self._midi_message_debug_closed)
        self.midi_message_debug.show()
        self.midi_message_debug.raise_()
        
    def _midi_message_debug_closed(self):
        """Handle MIDI message debug window closure"""
        self.midi_message_debug = None 

    def _handle_midi_message(self, message, timestamp):
        """Handle incoming MIDI message"""
        data = message[0]  # Get the raw MIDI data
        
        # Check if it's a SysEx message
        if data[0] == START_OF_SYSEX and len(data) > 8:
            # Verify it's a Roland message for JD-Xi
            if (data[1] == DEVICE_ID and  # Roland ID
                data[4:8] == bytes([MODEL_ID_1, MODEL_ID_2, MODEL_ID, JD_XI_ID])):  # JD-Xi ID
                # Blink the input indicator
                if hasattr(self, 'midi_in_indicator'):
                    self.midi_in_indicator.blink()
                
                # Forward to MIDI helper
                if hasattr(self, 'midi_helper'):
                    self.midi_helper.handle_midi_message(message, timestamp)

    def _send_midi_message(self, message):
        """Send MIDI message and blink indicator"""
        if self.midi_out:
            self.midi_out.send_message(message)
            # Blink the output indicator
            if hasattr(self, 'midi_out_indicator'):
                self.midi_out_indicator.blink() 

    def _show_drums_editor(self):
        """Show the drum editor window"""
        try:
            if not hasattr(self, 'drums_editor'):
                self.drums_editor = DrumEditor(midi_helper=self.midi_helper, 
                                               parent=self)  # Pass midi_helper instance
            self.drums_editor.show()
            self.drums_editor.raise_()
            
        except Exception as e:
            logging.error(f"Error showing Drums editor: {str(e)}") 

    def update_preset_display(self, preset_num, preset_name):
        """Update the current preset display"""
        self.current_preset_num = preset_num
        self.current_preset_name = preset_name
        self._update_display() 

    def _edit_patch_name(self):
        """Edit current patch name"""
        try:
            dialog = PatchNameEditor(self.current_preset_name, self)
            if dialog.exec_():
                new_name = dialog.get_name()
                
                # Update display
                self.update_preset_display(self.current_preset_num, new_name)
                
                # Send MIDI message to update patch name
                if self.midi_out:
                    msg = MIDIHelper.create_patch_name_message(
                        self.current_preset_num, 
                        new_name
                    )
                    self.midi_out.send_message(msg)
                    logging.debug(f"Updated patch {self.current_preset_num} name to: {new_name}")
                    
                    # Blink indicator
                    if hasattr(self, 'midi_out_indicator'):
                        self.midi_out_indicator.blink()
                        
        except Exception as e:
            logging.error(f"Error editing patch name: {str(e)}") 

    def _save_settings(self):
        """Save application settings"""
        try:
            # Save MIDI port settings
            if hasattr(self, 'settings'):
                self.settings.setValue("midi_in", self.midi_in_port_name)
                self.settings.setValue("midi_out", self.midi_out_port_name)
                
                # Save window geometry
                self.settings.setValue("geometry", self.saveGeometry())
                
                # Save current preset info
                self.settings.setValue("preset_num", self.current_preset_num)
                self.settings.setValue("preset_name", self.current_preset_name)
                
                logging.debug("Settings saved successfully")
                
        except Exception as e:
            logging.error(f"Error saving settings: {str(e)}") 

    def show_error(self, title: str, message: str):
        """Show error message dialog
        
        Args:
            title: Dialog title
            message: Error message
        """
        QMessageBox.critical(self, title, message)

    def show_warning(self, title: str, message: str):
        """Show warning message dialog
        
        Args:
            title: Dialog title
            message: Warning message
        """
        QMessageBox.warning(self, title, message)

    def show_info(self, title: str, message: str):
        """Show info message dialog
        
        Args:
            title: Dialog title
            message: Info message
        """
        QMessageBox.information(self, title, message) 

    def _auto_connect_jdxi(self):
        """Attempt to automatically connect to JD-Xi MIDI ports"""
        try:
            # Get available ports
            input_ports = self.midi_helper.get_input_ports()
            output_ports = self.midi_helper.get_output_ports()
            
            # Look for JD-Xi in port names (case insensitive)
            jdxi_names = ['jd-xi', 'jdxi', 'roland jd-xi']
            
            # Find input port
            for port in input_ports:
                if any(name in port.lower() for name in jdxi_names):
                    self.midi_helper.open_input_port(port)
                    logging.info(f"Auto-connected to JD-Xi input: {port}")
                    break
                
            # Find output port
            for port in output_ports:
                if any(name in port.lower() for name in jdxi_names):
                    self.midi_helper.open_output_port(port)
                    logging.info(f"Auto-connected to JD-Xi output: {port}")
                    break
                
            # Verify connection
            if self.midi_helper.current_in_port and self.midi_helper.current_out_port:
                # Send identity request to confirm it's a JD-Xi
                self._verify_jdxi_connection()
                return True
                
        except Exception as e:
            logging.error(f"Error auto-connecting to JD-Xi: {str(e)}")
            
        return False

    def _verify_jdxi_connection(self):
        """Verify connected device is a JD-Xi by sending identity request"""
        try:
            # Create identity request message using dataclass
            identity_request = IdentityRequest()
            
            # Send request
            if self.midi_helper:
                self.midi_helper.send_message(identity_request.to_list())
                logging.debug("Sent JD-Xi identity request")
                
        except Exception as e:
            logging.error(f"Error sending identity request: {str(e)}") 

    def show_digital_synth_editor(self, synth_num=1):
        """Show digital synth editor window"""
        try:
            if not hasattr(self, f'digital_synth_{synth_num}_editor'):
                # Create new editor instance
                editor = DigitalSynthEditor(
                    synth_num=synth_num,
                    midi_helper=self.midi_helper,
                    parent=self
                )
                setattr(self, f'digital_synth_{synth_num}_editor', editor)
            
            # Get editor instance
            editor = getattr(self, f'digital_synth_{synth_num}_editor')
            
            # Show editor window
            editor.show()
            editor.raise_()
            editor.activateWindow()
            
            logging.debug(f"Showing Digital Synth {synth_num} editor")
            
        except Exception as e:
            logging.error(f"Error showing Digital Synth {synth_num} editor: {str(e)}")
            self.show_error("Editor Error", str(e)) 

    def _handle_piano_note_on(self, note_num):
        """Handle piano key press"""
        if self.midi_helper:
            # Note on message: 0x90 (Note On, channel 1), note number, velocity 100
            msg = [0x90, note_num, 100]
            self.midi_helper.send_message(msg)
            logging.debug(f"Sent Note On: {note_num}")

    def _handle_piano_note_off(self, note_num):
        """Handle piano key release"""
        if self.midi_helper:
            # Note off message: 0x80 (Note Off, channel 1), note number, velocity 0
            msg = [0x80, note_num, 0]
            self.midi_helper.send_message(msg)
            logging.debug(f"Sent Note Off: {note_num}")

    def _create_midi_indicators(self):
        """Create MIDI activity indicators"""
        # Create indicators
        self.midi_in_indicator = MIDIIndicator()
        self.midi_out_indicator = MIDIIndicator()
        
        # Create labels
        in_label = QLabel("MIDI IN")
        out_label = QLabel("MIDI OUT")
        in_label.setStyleSheet("color: white; font-size: 10px;")
        out_label.setStyleSheet("color: white; font-size: 10px;")
        
        # Create container widget
        indicator_widget = QWidget(self)
        indicator_layout = QVBoxLayout(indicator_widget)
        indicator_layout.setSpacing(4)
        indicator_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add indicators with labels
        for label, indicator in [(in_label, self.midi_in_indicator), 
                               (out_label, self.midi_out_indicator)]:
            row = QHBoxLayout()
            row.addWidget(label)
            row.addWidget(indicator)
            indicator_layout.addLayout(row)
        
        # Position the container - moved right by 20px and down by 50px from original position
        indicator_widget.move(self.width() - 80, 120)  # Original was (self.width() - 100, 70)
        
        return indicator_widget 

    def _handle_octave_shift(self, direction: int):
        """Handle octave shift button press"""
        try:
            if self.midi_helper:
                # Get current octave from UI (-3 to +3)
                current = self.current_octave
                
                # Calculate new octave value
                new_octave = max(min(current + direction, 3), -3)
                
                # Convert to MIDI value (61-67 maps to -3 to +3)
                midi_value = new_octave + 64  # Center at 64
                
                # Send parameter change using new dataclass
                msg = ParameterMessage(
                    area=ANALOG_SYNTH_AREA,
                    part=0x00,
                    group=0x00,
                    param=0x34,  # Octave Shift parameter address
                    value=midi_value
                ).to_list()
                
                self.midi_helper.send_message(msg)
                
                # Update UI state
                self.current_octave = new_octave
                self._update_octave_display()
                
                logging.debug(f"Octave shifted to {new_octave} (MIDI value: {midi_value})")
                
        except Exception as e:
            logging.error(f"Error shifting octave: {str(e)}") 

    def _show_analog_presets(self):
        """Show the analog preset editor window"""
        self.preset_editor = PresetEditor(
            midi_helper=self.midi_helper,
            parent=self,
            preset_type=PresetType.ANALOG
        )
        self.preset_editor.preset_changed.connect(self._update_display_preset)
        self.midi_helper.preset_changed.connect(self._update_display_preset)
        self.preset_editor.show()

    def _update_display_preset(self, preset_number: int, preset_name: str, channel: int):
        """Update the display with the new preset information"""
        print(f"Updating display preset: # {preset_number}, name: {preset_name}, channel: {channel}")
        self.current_preset_index = preset_number
        self.preset_name = preset_name
        self.channel = channel
        if re.search(r"^\d{3}:", preset_name):
            preset_number = int(preset_name[:3])
            preset_name = preset_name[4:]
        try:
            # Update display
            self.update_preset_display(preset_number, preset_name)
            
            # Update piano keyboard channel if it exists
            if hasattr(self, 'piano_keyboard'):
                self.piano_keyboard.set_midi_channel(channel)
                
            # Update channel indicator if it exists
            if hasattr(self, 'channel_button'):
                self.channel_button.set_channel(channel)
            
            logging.debug(f"Updated display: {preset_number:03d}:{preset_name} (channel {channel})")
            
        except Exception as e:
            logging.error(f"Error updating display: {str(e)}")

    def _update_display_image(self, preset_num: int = 1, preset_name: str = "INIT PATCH"):
        """Update the digital display image
        
        Args:
            preset_num: Preset number to display (1-128)
            preset_name: Name of preset to display
        """
        try:
            # Create new image with updated preset info
            image = draw_jdxi(
                digital_font_family=self.digital_font_family,
                current_octave=self.current_octave,
                preset_num=preset_num,
                preset_name=preset_name
            )
            
            # Update display label
            if hasattr(self, 'display_label'):
                self.display_label.setPixmap(image)
            
            logging.debug(f"Updated display: {preset_num:03d}:{preset_name}")
            
        except Exception as e:
            logging.error(f"Error updating display image: {str(e)}") 

    def _load_last_preset(self):
        """Load the last used preset from settings"""
        try:
            # Get last preset info from settings
            synth_type = self.settings.value('last_preset/synth_type', PresetType.DIGITAL_1)
            preset_num = self.settings.value('last_preset/preset_num', 0, type=int)
            channel = self.settings.value('last_preset/channel', 0, type=int)
            
            # Get preset list based on synth type
            if synth_type == PresetType.ANALOG:
                presets = AN_PRESETS
                bank_msb = 0
                bank_lsb = preset_num // 7
                program = preset_num % 7
            elif synth_type == PresetType.DIGITAL_1:
                presets = DIGITAL_PRESETS
                bank_msb = 1
                bank_lsb = preset_num // 16
                program = preset_num % 16
            elif synth_type == PresetType.DIGITAL_2:
                presets = DIGITAL_PRESETS
                bank_msb = 2
                bank_lsb = preset_num // 16
                program = preset_num % 16
            else:  # Drums
                presets = DRUM_PRESETS
                bank_msb = 3
                bank_lsb = preset_num // 16
                program = preset_num % 16
            
            # Send MIDI messages to load preset
            if hasattr(self, 'midi_helper') and self.midi_helper:
                self.midi_helper.send_bank_select(bank_msb, bank_lsb, channel)
                self.midi_helper.send_program_change(program, channel)
                
                # Update display and channel
                preset_name = presets[preset_num - 1]  # Adjust index to be 0-based
                self._update_display_preset(preset_num, preset_name, channel)
                
                logging.debug(f"Loaded last preset: {preset_name} on channel {channel}")
            
        except Exception as e:
            logging.error(f"Error loading last preset: {str(e)}")
            
    def _save_last_preset(self, synth_type: str, preset_num: int, channel: int):
        """Save the last used preset to settings
        
        Args:
            synth_type: Type of synth ('Analog', 'Digital 1', 'Digital 2', 'Drums')
            preset_num: Preset number (0-based index)
            channel: MIDI channel
        """
        try:
            self.settings.setValue('last_preset/synth_type', synth_type)
            self.settings.setValue('last_preset/preset_num', preset_num)
            self.settings.setValue('last_preset/channel', channel)
            logging.debug(f"Saved last preset: {synth_type} #{preset_num} on channel {channel}")
            
        except Exception as e:
            logging.error(f"Error saving last preset: {str(e)}") 

    def _load_favorite(self, button: FavoriteButton):
        """Load preset from favorite button"""
        if button.preset:
            if self.midi_helper:
                # Get preset info from button
                self.preset_type = button.preset.synth_type
                self.current_preset_index = button.preset.preset_num
                self.channel = button.preset.channel
                # Update display - REMOVED the preset_num + 1
                self._update_display_preset(
                    self.current_preset_index + 1, # Convert to 1-based index
                    button.preset.preset_name,
                    self.channel
                )
                preset_data = {
                    'type': self.preset_type,  # Ensure this is a valid type
                    'selpreset': self.current_preset_index + 1,  # Convert to 1-based index
                    'modified': 0  # or 1, depending on your logic
                }
                # Send MIDI messages to load preset
                self.load_preset(preset_data)
                
    def _show_favorite_context_menu(self, pos, button: FavoriteButton):
        """Show context menu for favorite button"""
        menu = QMenu()
        
        # Add save action if we have a current preset
        if hasattr(self, 'current_preset_num'):
            save_action = menu.addAction("Save Current Preset")
            save_action.triggered.connect(
                lambda: self._save_to_favorite(button)
            )
            
        # Add clear action if slot has a preset
        if button.preset:
            clear_action = menu.addAction("Clear Slot")
            clear_action.triggered.connect(
                lambda: self._clear_favorite(button)
            )
            
        menu.exec_(button.mapToGlobal(pos))
        
    def _save_to_favorite(self, button: FavoriteButton):
        """Save current preset to favorite slot"""
        if hasattr(self, 'current_preset_num'):
            # Get current preset info from settings
            synth_type = self.settings.value('last_preset/synth_type', PresetType.ANALOG)
            preset_num = self.settings.value('last_preset/preset_num', 0, type=int)
            channel = self.settings.value('last_preset/channel', 0, type=int)
            
            try:
                # Get the current preset name
                preset_name = self._get_current_preset_name()
                
                # Save to button (which will also save to settings)
                button.save_preset_as_favourite(synth_type, preset_num, preset_name, channel)
                
                # Update display to show the saved preset
                self._update_display_preset(preset_num, preset_name, channel)
                
            except Exception as e:
                logging.error(f"Error saving to favorite: {str(e)}")
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Error saving preset: {str(e)}"
                )

    def _clear_favorite(self, button: FavoriteButton):
        """Clear favorite slot"""
        button.clear_preset()

    def _load_saved_favorites(self):
        """Load saved favorites from settings"""
        for button in self.favorite_buttons:
            # Check if slot has saved preset
            synth_type = self.settings.value(f'favorites/slot{button.slot_num}/synth_type', '')
            if synth_type:
                preset_num = self.settings.value(f'favorites/slot{button.slot_num}/preset_num', 0, type=int)
                preset_name = self.settings.value(f'favorites/slot{button.slot_num}/preset_name', '')
                channel = self.settings.value(f'favorites/slot{button.slot_num}/channel', 0, type=int)
                
                button.save_preset_as_favourite(synth_type, preset_num, preset_name, channel)

    def load_preset(self, preset_data):
        """Load preset data into synth"""
        try:
            # self.preset_type = PresetType.DIGITAL_1
            if self.midi_helper:
                # Use PresetLoader for consistent preset loading
                self.preset_loader = PresetLoader(self.midi_helper)
                self.preset_loader.load_preset(
                    preset_data,
                )
                # Store as last loaded preset
                self.last_preset = preset_data
                # self.settings.setValue("last_preset", preset_data)
                
        except Exception as e:
            logging.error(f"Error loading preset: {str(e)}")

    def show_analog_editor(self):
        """Show analog synth editor"""
        try:
            if not hasattr(self, 'analog_editor'):
                self.analog_editor = AnalogSynthEditor(
                    midi_helper=self.midi_helper
                )
            self.analog_editor.show()
            self.analog_editor.raise_()
            
        except Exception as e:
            logging.error(f"Error showing Analog Synth editor: {str(e)}")

    def set_midi_ports(self, in_port: str, out_port: str) -> bool:
        """Set MIDI input and output ports
        
        Args:
            in_port: Input port name
            out_port: Output port name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Open ports
            if not self.midi_helper.open_input_port(in_port):
                return False
                
            if not self.midi_helper.open_output_port(out_port):
                return False
                
            # Update indicators
            self.midi_in_indicator.set_state(self.midi_helper.is_input_open)
            self.midi_out_indicator.set_state(self.midi_helper.is_output_open)
            
            return True
            
        except Exception as e:
            logging.error(f"Error setting MIDI ports: {str(e)}")
            return False

    def _connect_midi(self):
        """Connect to MIDI ports"""
        try:
            # Find JD-Xi ports
            in_port, out_port = self.midi_helper.find_jdxi_ports()
            
            if in_port and out_port:
                # Open ports
                if self.midi_helper.open_ports(in_port, out_port):
                    logging.info(f"Connected to JD-Xi ({in_port}, {out_port})")
                    self.statusBar().showMessage(f"Connected to JD-Xi")
                    
                    # Remove or comment out any initialization messages
                    # self.midi_helper.send_identity_request()  # Remove this
                    return True
                    
            logging.warning("JD-Xi not found")
            self.statusBar().showMessage("JD-Xi not found")
            return False
            
        except Exception as e:
            logging.error(f"Error connecting to MIDI: {str(e)}")
            self.statusBar().showMessage("MIDI connection error")
            return False

    def _open_vocal_fx(self):
        """Show the vocal FX editor window"""
        try:
            if not hasattr(self, 'vocal_fx_editor'):
                self.vocal_fx_editor = VocalFXEditor(
                    midi_helper=self.midi_helper,
                    parent=self
                )
            self.vocal_fx_editor.show()
            self.vocal_fx_editor.raise_()
            
        except Exception as e:
            logging.error(f"Error showing Vocal FX editor: {str(e)}")

    def _send_octave_bak(self, direction):
        """Send octave change MIDI message"""
        if self.midi_out:
            # Update octave tracking
            self.current_octave = max(-3, min(3, self.current_octave + direction))

            # Update button states
            self.octave_down.setChecked(self.current_octave < 0)
            self.octave_up.setChecked(self.current_octave > 0)

            # Update display
            self._update_display()

            # Map octave value to correct SysEx value
            # -3 = 0x3D, -2 = 0x3E, -1 = 0x3F, 0 = 0x40, +1 = 0x41, +2 = 0x42, +3 = 0x43
            octave_value = 0x40 + self.current_octave  # 0x40 is center octave

            # Calculate checksum
            checksum = (0x19 + 0x01 + 0x00 + 0x15 + octave_value)
            checksum = (0x80 - (checksum & 0x7F)) & 0x7F

            # Create SysEx message
            sysex_msg = [
                0xF0,  # Start of SysEx
                0x41,  # Roland ID
                0x10,  # Device ID
                0x00, 0x00, 0x00, 0x0E,  # Model ID
                0x12,  # Command ID (DT1)
                0x19,  # Address 1
                0x01,  # Address 2
                0x00,  # Address 3
                0x15,  # Address 4
                octave_value,  # Parameter value
                checksum,  # Checksum
                0xF7  # End of SysEx
            ]

            self.midi_helper.send_message(sysex_msg)
            logging.debug(f"Sent octave change SysEx, new octave: {self.current_octave} (value: {hex(octave_value)})")

    def _create_global_controls(self):
        """Create global controls section"""
        group = QGroupBox("Global Controls")
        layout = QHBoxLayout()
        group.setLayout(layout)
        
        # Octave controls
        octave_group = QGroupBox("Octave")
        octave_layout = QHBoxLayout()
        octave_group.setLayout(octave_layout)
        
        self.octave_down = QPushButton("Down")
        self.octave_up = QPushButton("Up")
        self.octave_display = QLabel("0")  # Display current octave
        self.octave_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.octave_down.clicked.connect(lambda: self._send_octave(-1))
        self.octave_up.clicked.connect(lambda: self._send_octave(1))
        octave_button_stylesheet = """
            QPushButton {
                background-color: black;
                border: 4px solid #d51e35;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #1A1A1A;
                border-color: #ff4d4d;
            }
            QPushButton:pressed, QPushButton:checked {
                background-color: #333333;
                border-color: #ff6666;
            }
        """
        self.octave_up.setStyleSheet(octave_button_stylesheet)
        self.octave_down.setStyleSheet(octave_button_stylesheet)

        octave_layout.addWidget(self.octave_down)
        octave_layout.addWidget(self.octave_display)
        octave_layout.addWidget(self.octave_up)
        
        # Arpeggiator controls
        arp_group = QGroupBox("Arpeggiator")
        arp_layout = QHBoxLayout()
        arp_group.setLayout(arp_layout)
        
        self.arp_switch = QPushButton("On")
        self.arp_switch.setCheckable(True)
        self.arp_switch.clicked.connect(self._toggle_arpeggiator)
        
        arp_layout.addWidget(self.arp_switch)
        
        # Add groups to main layout
        layout.addWidget(octave_group)
        layout.addWidget(arp_group)
        
        return group

    def _change_octave(self, direction: int):
        """Change octave up/down
        
        Args:
            direction: +1 for up, -1 for down
        """
        if not self.midi_helper:
            return
            
        try:
            # Get current octave from display
            current = int(self.octave_display.text())
            
            # Calculate new octave (-3 to +3 range)
            new_octave = max(min(current + direction, 3), -3)
            
            # Convert to MIDI value (61-67 range)
            midi_value = new_octave + 64
            
            # Send parameter change
            self.midi_helper.send_parameter(
                area=0x00,  # Program zone area
                part=0x00,
                group=0x00,
                param=0x19,  # Zone Octave Shift parameter
                value=midi_value
            )
            
            # Update display
            self.octave_display.setText(str(new_octave))
            
        except Exception as e:
            logging.error(f"Error changing octave: {str(e)}")

    def _toggle_arpeggiator(self, checked: bool):
        """Toggle arpeggiator on/off"""
        if not self.midi_helper:
            return
            
        try:
            # Send parameter change (0x00 = Program zone area, 0x03 = Arpeggio Switch)
            self.midi_helper.send_parameter(
                area=0x00,  # Program zone area
                part=0x00,  # Common part
                group=0x00, # Common group
                param=0x03, # Arpeggio Switch parameter
                value=1 if checked else 0  # 0 = OFF, 1 = ON
            )
            
            # Update button text
            self.arp_switch.setText("Off" if not checked else "On")
            
        except Exception as e:
            logging.error(f"Error toggling arpeggiator: {str(e)}")

    def _show_arpeggio_editor(self):
        """Show the arpeggio editor window"""
        try:
            if not hasattr(self, 'arpeggio_editor'):
                logging.debug("Creating new arpeggio editor")
                self.arpeggio_editor = ArpeggioEditor(midi_helper=self.midi_helper)
            logging.debug("Showing arpeggio editor")
            self.arpeggio_editor.show()
        except Exception as e:
            logging.error(f"Error showing Arpeggiator editor: {str(e)}")

    def _get_current_preset_name(self):
        """Get the name of the currently selected preset"""
        try:
            synth_type = self.settings.value('last_preset/synth_type', PresetType.ANALOG)
            preset_num = self.settings.value('last_preset/preset_num', 0, type=int)
            
            # Get preset name - adjust index to be 0-based
            if synth_type == PresetType.ANALOG:
                return AN_PRESETS[preset_num - 1]  # Convert 1-based to 0-based
            elif synth_type == PresetType.DIGITAL_1:
                return DIGITAL_PRESETS[preset_num - 1]
            elif synth_type == PresetType.DIGITAL_2:
                return DIGITAL_PRESETS[preset_num - 1]
            else:
                return DRUM_PRESETS[preset_num - 1]
        except IndexError:
            return "INIT PATCH"

    def save_preset_as_favourite(self, synth_type: str, preset_num: int, preset_name: str, channel: int):
        """Save current preset to this favorite slot"""
        logging.debug(f"Saving preset: {synth_type}, {preset_num}, {preset_name}, {channel}")
        self.preset = PresetFavorite(synth_type, preset_num, preset_name, channel)
        # self._update_style()
        # self._save_to_settings()
        logging.debug(f"Saved preset to favorite {self.slot_num}: {preset_name}")

    def load_preset_from_favourites(self):
        """Load saved preset"""
        if not self.preset:
            logging.warning(f"No preset saved in favorite slot {self.slot_num}")
            return
        logging.debug(f"Loading preset: {self.preset.synth_type}, {self.preset.preset_num}, {self.preset.preset_name}, {self.preset.channel}")
        preset_data = {
            'type': self.preset.synth_type,
            'selpreset': self.preset.preset_num + 1,
            'modified': 0
        }
        self.load_preset(preset_data)
        # self._update_style()
        logging.debug(f"Loaded favorite {self.slot_num}: {self.preset.preset_name}")