"""
Patch Manager Module
====================s

This module defines the `PatchManager` class, a PySide6-based GUI for loading
and saving MIDI patch files for the Roland JD-Xi synthesizer.

Features:
- Allows users to browse for patch files using a file dialog.
- Supports both saving and loading patches, depending on the mode.
- Integrates with `MIDIHelper` for handling MIDI patch operations.
- Implements a simple, dark-themed UI with action buttons.

Classes:
- PatchManager: A QMainWindow that provides a user interface for managing patch files.

Dependencies:
- PySide6
- jdxi_editor.midi.io.MIDIHelper
- jdxi_editor.ui.style.Style

"""

from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QLineEdit,
)
import logging

from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.ui.io.controls import save_all_controls_to_single_file


class PatchManager(QMainWindow):
    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        parent=None,
        save_mode=False,
        editors=None,
    ):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.save_mode = save_mode
        self.editors = editors

        # Set window properties
        self.setWindowTitle("Save Patch" if save_mode else "Load Patch")
        self.setMinimumSize(400, 200)

        # Apply dark theme styling
        self.setStyleSheet(JDXiStyle.PATCH_MANAGER)

        # Create central widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)

        # Create file path row
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select file location...")
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self._browse_file)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_button)
        layout.addLayout(path_layout)

        # Create action buttons
        button_layout = QHBoxLayout()
        action_button = QPushButton("Save" if save_mode else "Load")
        action_button.clicked.connect(self._handle_action)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(action_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Set central widget
        self.setCentralWidget(main_widget)

    def _browse_file(self):
        """Open file dialog for selecting patch file"""
        try:
            if self.save_mode:
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Patch File",
                    "",
                    "Patch Files (*.syx);(*.json);All Files (*.*)",
                )
            else:
                file_path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Load Patch File",
                    "",
                    "Patch Files (*.syx);(*.json);All Files (*.*)",
                )
            if file_path:
                self.path_input.setText(file_path)
        except Exception as ex:
            log.error(f"Error browsing for file: {str(ex)}")

    def _handle_action(self):
        """Handle save/load action"""
        try:
            file_path = self.path_input.text()
            if not file_path:
                logging.warning("No file selected.")
                return

            if self.midi_helper is None:
                log.message("MIDI helper not initialized.")
                return

            if self.save_mode:
                save_all_controls_to_single_file(self.editors, file_path)
                log.message(f"Patch saved to {file_path}")
            else:
                self.midi_helper.load_patch(file_path)
                log.message(f"Patch loaded from {file_path}")

            self.close()

        except Exception as ex:
            log.message(
                f"Error {'saving' if self.save_mode else 'loading'} patch: {str(ex)}"
            )
