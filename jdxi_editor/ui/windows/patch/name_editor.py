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

"""


from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
)

from jdxi_editor.jdxi.style import JDXiStyle


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
        self.setStyleSheet(JDXiStyle.EDITOR)

    def get_name(self):
        """Get the edited patch name"""
        return self.name_input.text().upper()  # JD-Xi uses uppercase names
