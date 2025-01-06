from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFrame, QApplication,
    QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from pathlib import Path
import rtmidi

from ..style import Style
from .midi_config import MidiConfigFrame
from .editors import (
    DigitalSynthEditor,
    AnalogSynthEditor, 
    DrumEditor,
    EffectsEditor,
    ArpeggioEditor,
    VocalFXEditor
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize state
        self.midi_in = None
        self.midi_out = None
        self.editor_windows = {}
        
        # Set window properties
        self.setWindowTitle(f"JDXi Manager ({QApplication.applicationVersion()}) - Control Panel")
        self.setFixedSize(1150, 740)
        
        # Create central widget and main layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        # Create left side layout for MIDI and parts
        left_side = QVBoxLayout()
        main_layout.addLayout(left_side)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create MIDI configuration section
        self.midi_config = MidiConfigFrame()
        self.midi_config.midi_connected.connect(self._on_midi_connected)
        left_side.addWidget(self.midi_config)
        
        # Create parts section
        parts_frame = self._create_parts()
        left_side.addWidget(parts_frame)
        
        # Create other section (right side)
        other_frame = self._create_other()
        main_layout.addWidget(other_frame)
        
        # Apply styling
        Style.apply_to_widget(self)
        
        # Check for updates after a short delay
        QTimer.singleShot(50, self._check_for_updates)

    def _create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Load Program...", self._load_program)
        file_menu.addAction("Save Program...", self._save_program)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Copy", self._copy)
        edit_menu.addAction("Paste", self._paste)
        edit_menu.addSeparator()
        edit_menu.addAction("Initialize Program", self._init_program)
        
        # View menu
        view_menu = menubar.addMenu("View")
        for editor_name in ["Digital Synth 1", "Digital Synth 2", "Drums", 
                          "Analog Synth", "Effects", "Vocal FX", "Arpeggio"]:
            view_menu.addAction(editor_name, lambda n=editor_name: self._show_editor(n))
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("Online Manual", self._show_manual)
        help_menu.addAction("About", self._show_about)
        
    def _create_parts(self):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Create part buttons with proper styling
        parts = [
            ("Digital\nSynth 1", self._open_digital_synth1, Style.BUTTON_SELECTED),
            ("Digital\nSynth 2", self._open_digital_synth2, Style.BUTTON_SELECTED),
            ("Drums", self._open_drums, Style.BUTTON_SELECTED),
            ("Analog\nSynth", self._open_analog, Style.BUTTON_SELECTED)
        ]
        
        for text, slot, color in parts:
            btn = QPushButton(text)
            btn.setFixedHeight(60)
            btn.clicked.connect(slot)
            btn.setStyleSheet(f"""
                QPushButton {{
                    color: {color};
                    font-weight: bold;
                }}
            """)
            layout.addWidget(btn)
            
        return frame
        
    def _create_other(self):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Create other buttons
        others = [
            ("Effects", self._open_effects),
            ("Vocal FX", self._open_vocal_fx),
            ("Arpeggio", self._open_arpeggio)
        ]
        
        for text, slot in others:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.clicked.connect(slot)
            layout.addWidget(btn)
            
        return frame

    def _open_digital_synth1(self):
        self._show_editor("Digital Synth 1", DigitalSynthEditor, synth_num=1)
        
    def _open_digital_synth2(self):
        self._show_editor("Digital Synth 2", DigitalSynthEditor, synth_num=2)
        
    def _open_drums(self):
        self._show_editor("Drums", DrumEditor)
        
    def _open_analog(self):
        self._show_editor("Analog Synth", AnalogSynthEditor)
        
    def _open_effects(self):
        self._show_editor("Effects", EffectsEditor)
        
    def _open_vocal_fx(self):
        self._show_editor("Vocal FX", VocalFXEditor)
        
    def _open_arpeggio(self):
        self._show_editor("Arpeggio", ArpeggioEditor)
        
    def _show_editor(self, name, editor_class=None, **kwargs):
        """Show or create an editor window"""
        if name not in self.editor_windows:
            if editor_class:
                editor = editor_class(midi_out=self.midi_out, **kwargs)
                editor.setWindowTitle(f"JDXi Manager - {name} Editor")
                self.editor_windows[name] = editor
            else:
                return
                
        editor = self.editor_windows[name]
        editor.show()
        editor.raise_()
        
    def _on_midi_connected(self, in_port, out_port):
        """Handle MIDI ports being connected"""
        self.midi_in = in_port
        self.midi_out = out_port
        
        # Update editor windows with new MIDI ports
        for editor in self.editor_windows.values():
            editor.set_midi_ports(self.midi_in, self.midi_out)
            
    def _check_for_updates(self):
        """Check for software updates"""
        # TODO: Implement update checking
        pass
        
    def _show_about(self):
        QMessageBox.about(self,
            "About JDXi Manager",
            f"""<h3>JDXi Manager {QApplication.applicationVersion()}</h3>
            <p>Software Patch Editor for the Roland JD-Xi Synthesizer</p>
            <p>Copyright © 2016-2024 LinuxTECH.NET</p>
            <p>Roland is a registered trademark of Roland Corporation</p>"""
        )
        
    def _load_program(self):
        # TODO: Implement program loading
        pass
        
    def _save_program(self):
        # TODO: Implement program saving
        pass
        
    def _copy(self):
        # TODO: Implement copy functionality
        pass
        
    def _paste(self):
        # TODO: Implement paste functionality
        pass
        
    def _init_program(self):
        # TODO: Implement program initialization
        pass
        
    def _show_manual(self):
        # TODO: Implement manual display
        pass
        
    def closeEvent(self, event):
        """Handle application shutdown"""
        # Close all editor windows
        for editor in self.editor_windows.values():
            editor.close()
            
        # Close MIDI ports
        if self.midi_in:
            self.midi_in.close_port()
        if self.midi_out:
            self.midi_out.close_port()
            
        event.accept() 