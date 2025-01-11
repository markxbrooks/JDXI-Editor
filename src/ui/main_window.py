from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QMessageBox, QLabel, QPushButton,
    QFrame, QGridLayout, QGroupBox
)
from PySide6.QtCore import Qt, QSettings, QByteArray, QTimer
from PySide6.QtGui import QIcon, QAction, QFont, QPixmap, QImage, QPainter, QPen, QColor, QFontDatabase
import logging

from .editors import (
    AnalogSynthEditor,
    DigitalSynthEditor,
    DrumEditor,
    ArpeggioEditor,
    EffectsEditor
)
from .midi_config import MidiConfigFrame
from .patch_manager import PatchManager
from .widgets import MIDIIndicator, LogViewer
from ..midi import MIDIHelper

def get_jdxi_image(digital_font_family=None):
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
    display_width = 180
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
    display_width = 180
    display_height = 70
    
    # Draw dark grey background for display
    painter.setBrush(QColor("#1A1A1A"))
    painter.setPen(QPen(QColor("#FF8C00"), 1))
    painter.drawRect(display_x, display_y, display_width, display_height)
    
    # Load/Save buttons in display (without boxes)
    button_width = 70
    button_height = 25
    button_margin = 10
    button_y = display_y + (display_height - button_height*2 - button_margin) / 2
    
    # Load button (text only)
    load_x = display_x + button_margin
    painter.setPen(QPen(QColor("#FF8C00")))
    if digital_font_family:
        painter.setFont(QFont(digital_font_family, 18))
    else:
        painter.setFont(QFont("Consolas", 18))  # Fallback font
    painter.drawText(
        load_x, 
        button_y + button_height - 8, 
        "Load Part"
    )
    
    # Save button (text only)
    save_x = display_x + button_margin
    painter.drawText(
        save_x, 
        button_y + button_height*2 + button_margin - 8, 
        "Save Part"
    )
    
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
        self.setWindowTitle("JD-Xi Manager")
        self.setMinimumSize(620, 248)
        
        # Store window dimensions
        self.width = 1000
        self.height = 400
        self.margin = 15
        
        # Store display coordinates as class variables
        self.display_x = self.margin + 20
        self.display_y = self.margin + 15 + 30  # title_y + 30
        self.display_width = 180
        self.display_height = 70
        
        # Initialize MIDI indicators
        self.midi_in_indicator = MIDIIndicator()
        self.midi_out_indicator = MIDIIndicator()
        
        # Set black background for entire application
        self.setStyleSheet("""
            QMainWindow {
                background-color: black;
            }
            QWidget {
                background-color: black;
                color: white;
            }
            QMenuBar {
                background-color: black;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #333333;
            }
            QMenu {
                background-color: black;
                color: white;
            }
            QMenu::item:selected {
                background-color: #333333;
            }
            QGroupBox {
                border: 1px solid #333333;
            }
            QLabel {
                background-color: transparent;
            }
            QStatusBar {
                background-color: black;
                color: white;
            }
        """)
        
        # Initialize MIDI ports
        self.midi_in = None
        self.midi_out = None
        
        # Load custom font with relative path
        import os
        font_path = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "fonts", "DS-DIGI.TTF")
        if os.path.exists(font_path):
            logging.debug(f"Found file, Loading DS-DIGI font from {font_path}")
            try:
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id < 0:
                    logging.debug(f"Error loading DS-DIGI font from {font_path} : {e}")
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    self.digital_font_family = font_families[0]
                    logging.debug(f"Successfully loaded font family: {self.digital_font_family}")
                else:
                    logging.debug("No font families found after loading font")
            except Exception as e:
                logging.exception(f"Error loading DS-DIGI font from {font_path}: {e}")
        else:
            logging.debug(f"File not found: {font_path}")
        
        # Create UI
        self._create_menu_bar()
        self._create_central_widget()
        self._create_status_bar()
        
        # Load settings
        self.settings = QSettings("jdxi_manager", "settings")
        self._load_settings()
        
        # Show MIDI config if no ports configured
        if not self.midi_in or not self.midi_out:
            self._show_midi_config()
            
    def _create_central_widget(self):
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
        
        # Get the JD-Xi image with digital font
        pixmap = get_jdxi_image(self.digital_font_family if hasattr(self, 'digital_font_family') else None)
        
        # Create label for image
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        container.layout().addWidget(image_label)
        
        # Add overlaid controls
        self._add_overlaid_controls(container)
        
        layout.addWidget(container)
        
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
        
    def _create_status_bar(self):
        status_bar = self.statusBar()
        
        # Add MIDI activity indicators at left side
        status_bar.addWidget(QLabel("MIDI In:"))
        status_bar.addWidget(self.midi_in_indicator)
        status_bar.addWidget(QLabel("MIDI Out:"))
        status_bar.addWidget(self.midi_out_indicator)
        status_bar.addWidget(QLabel(""))  # Spacer
        
    def _show_midi_config(self):
        """Show MIDI configuration dialog"""
        dialog = MidiConfigFrame(self)
        if self.midi_in and self.midi_out:
            dialog.set_settings({
                'input_port': self.midi_in.port_name,
                'output_port': self.midi_out.port_name
            })
            
        dialog.portsChanged.connect(self._update_midi_ports)
        dialog.exec_()
        
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
        input_port = self.settings.value("midi/input_port")
        output_port = self.settings.value("midi/output_port")
        
        if input_port and output_port:
            try:
                self.midi_in = MIDIHelper.open_input(input_port)
                self.midi_out = MIDIHelper.open_output(output_port)
            except Exception as e:
                QMessageBox.warning(self, "Error",
                    "Failed to open MIDI ports from saved settings")

def _send_octave(self, direction):
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
            
            self.midi_out.send_message(sysex_msg)
            logging.debug(f"Sent octave change SysEx, new octave: {self.current_octave} (value: {hex(octave_value)})")
             
    def _show_editor(self, title, editor_class, **kwargs):
        """Show a synth editor window"""
        editor = editor_class(midi_out=self.midi_out, **kwargs)
        editor.setWindowTitle(title)
        editor.show()
        
        # Connect MIDI ports and indicators
        if self.midi_in:
            self.midi_in.set_callback(self._handle_midi_input)
        if self.midi_out:
            original_send = self.midi_out.send_message
            def send_with_indicator(msg):
                original_send(msg)
                self.midi_out_indicator.flash()
            self.midi_out.send_message = send_with_indicator
            
        editor.set_midi_ports(self.midi_in, self.midi_out)
        
    def _handle_midi_input(self, message, timestamp):
        """Handle incoming MIDI messages and flash indicator"""
        self.midi_in_indicator.flash()
        
    def _open_analog_synth(self):
        self._show_editor("Analog Synth", AnalogSynthEditor)
        
    def _open_digital_synth1(self):
        self._show_editor("Digital Synth 1", DigitalSynthEditor, synth_num=1)
        
    def _open_digital_synth2(self):
        self._show_editor("Digital Synth 2", DigitalSynthEditor, synth_num=2)
        
    def _open_drums(self):
        self._show_editor("Drums", DrumEditor)
        
    def _open_arpeggiator(self):
        self._show_editor("Arpeggiator", ArpeggioEditor)
        
    def _open_effects(self):
        self._show_editor("Effects", EffectsEditor)
        
    def _load_patch(self):
        """Show patch manager for loading"""
        dialog = PatchManager(self)
        dialog.patchSelected.connect(self._apply_patch)
        dialog.exec_()
        
    def _save_patch(self):
        """Show patch manager for saving"""
        # TODO: Implement patch saving
        pass
        
    def _apply_patch(self, patch_data):
        """Apply loaded patch data"""
        # TODO: Implement patch loading
        pass
        
    def closeEvent(self, event):
        """Handle application shutdown"""
        # Close MIDI ports
        if self.midi_in:
            self.midi_in.close()
        if self.midi_out:
            self.midi_out.close()
            
        super().closeEvent(event) 
        
    def _show_log_viewer(self):
        """Show log viewer dialog"""
        viewer = LogViewer(self)
        viewer.exec_() 
        
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
        button.clicked.connect(slot)
        
        # Style the button with brighter hover/pressed states
        button.setStyleSheet("""
            QPushButton {
                background-color: black;
                border: 4px solid #d51e35;
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
        """)
        
        row.addWidget(button)
        return row 
        
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
        digital1_row = self._create_button_row("Digital Synth 1", self._open_digital_synth1)
        digital2_row = self._create_button_row("Digital Synth 2", self._open_digital_synth2)
        drums_row = self._create_button_row("Drums", self._open_drums)
        analog_row = self._create_button_row("Analog Synth", self._open_analog_synth)
        arp_row = self._create_button_row("Arpeggiator", self._open_arpeggiator)
        
        parts_layout.addLayout(digital1_row)
        parts_layout.addLayout(digital2_row)
        parts_layout.addLayout(drums_row)
        parts_layout.addLayout(analog_row)
        parts_layout.addLayout(arp_row)
        
        # Effects button in top row
        fx_container = QWidget(widget)
        fx_container.setGeometry(self.width - 200, self.margin + 25, 150, 50)
        fx_layout = QHBoxLayout(fx_container)
        
        effects_row = self._create_button_row("Effects", self._open_effects)
        fx_layout.addLayout(effects_row)
        
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
        
        for i, note in enumerate(white_notes):
            x_pos = keyboard_start + i * key_width
            self._add_piano_key(widget, False, note, x_pos, keyboard_y, key_width, key_height)
            
        # Add black keys
        black_notes = [
            37, 39, None, 42, 44, 46,     # C#1 to B1
            49, 51, None, 54, 56, 58,     # C#2 to B2
            61, 63, None, 66, 68, 70,     # C#3 to B3
            73, 75, None, 78, 80, 82,     # C#4 to B4
            85, 87, None, 90              # C#5 to F#5
        ]
        
        for i, note in enumerate(black_notes):
            x_pos = keyboard_start + i * key_width
            self._add_piano_key(widget, False, note, x_pos, keyboard_y, key_width, key_height)

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
            if self.midi_helper.midi_out:
                self.midi_helper.midi_out.send_message([0x90, note_number, 1])  # Note On
                logging.debug(f"Sent MIDI Note On {note_number} velocity 1")
        
        def key_released():
            if self.midi_helper.midi_out:
                self.midi_helper.midi_out.send_message([0x80, note_number, 5])  # Note Off
                logging.debug(f"Sent MIDI Note Off {note_number} velocity 5")
        
        # Connect to mouse events instead of clicked
        button.pressed.connect(key_pressed)
        button.released.connect(key_released) 
