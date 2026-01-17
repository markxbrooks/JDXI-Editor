"""
Patch Name Editor Module
========================

This module defines the `PatchNameEditor` class, a PySide6-based dialog for
editing the name of a JD-Xi patch.

Features:
- Provides a simple UI for renaming patches with a maximum of 12 characters.
- Ensures patch names are converted to uppercase, matching JD-Xi conventions.
- Includes "Save" and "Cancel" buttons for user confirmation.
- Applies a custom dark theme for styling.

Classes:
- PatchNameEditor: A QDialog that allows users to modify a patch name.

Dependencies:
- PySide6
- jdxi_editor.ui.style.Style

Example Usage
=============
>>>dialog = PatchNameEditor(current_name="Piano")
...if dialog.exec_():  # If the user clicks Save
...    sys_ex_bytes = dialog.get_sysex_bytes()
...    print("SysEx Bytes:", sys_ex_bytes)

"""

from PySide6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from jdxi_editor.jdxi.jdxi import JDXi


class PatchNameEditor(QDialog):
    def __init__(self, current_name="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Patch Name")
        self.setModal(True)

        main_layout = QVBoxLayout(self)
        group = QGroupBox("Patch Name")

        # Set up layout
        layout = QVBoxLayout(group)

        # Add name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.tone_name_input = QLineEdit(current_name)
        self.tone_name_input.setMaxLength(12)  # JD-Xi patch names are max 12 chars
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.tone_name_input)
        layout.addLayout(name_layout)

        # Add buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        group.setLayout(layout)
        main_layout.addWidget(group)
        self.setStyleSheet(JDXi.Style.EDITOR)

    def get_sysex_string(self):
        """
        Converts the current name input to SysExAddress bytes.
        JD-Xi patch names are encoded as ASCII characters, padded with spaces if shorter than 12 chars.
        """
        tone_name = self.tone_name_input.text()
        if len(tone_name) < 12:
            # Pad the name with spaces if it's shorter than 12 characters
            tone_name = tone_name.ljust(12)
        elif len(tone_name) > 12:
            # Truncate the name to 12 characters if it's too long (shouldn't happen due to setMaxLength)
            tone_name = tone_name[:12]
        return tone_name

    def get_sysex_bytes(self):
        """
        Converts the current name input to SysExAddress bytes.
        JD-Xi patch names are encoded as ASCII characters, padded with spaces if shorter than 12 chars.
        """
        tone_name = self.get_sysex_string()
        # Convert the string to a list of ASCII byte values
        sysex_bytes = [ord(char) for char in tone_name]
        return sysex_bytes


class PatchNameEditorOld(QDialog):
    def __init__(self, current_name="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Patch Name")
        self.setModal(True)

        main_layout = QVBoxLayout(self)
        group = QGroupBox("Patch Name")

        # Set up layout
        layout = QVBoxLayout(group)

        # Add name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_input = QLineEdit(current_name)
        self.name_input.setMaxLength(12)  # JD-Xi patch names are max 12 chars
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Add buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        group.setLayout(layout)
        main_layout.addWidget(group)
        self.setStyleSheet(JDXi.Style.EDITOR)

    def get_name(self):
        """Get the edited patch name"""
        return self.name_input.text().upper()  # JD-Xi uses uppercase names
