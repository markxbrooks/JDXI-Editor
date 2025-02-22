"""
Piano keyboard widget for JD-Xi Manager.

This module defines a PianoKeyboard widget, a custom QWidget that arranges and displays
a set of piano keys styled like those on a JD-Xi synthesizer. The widget combines both
white and black keys to form a complete piano keyboard, along with labels representing
drum pad names.

Key Features:
- **Custom Key Dimensions:** White and black keys are sized and positioned appropriately,
    with configurable widths and heights.
- **Dynamic Key Creation:** White keys are created first in a horizontal layout,
    while black keys are overlaid at specific positions.
- **Drum Pad Labels:** A row of labels is displayed above the keyboard to denote
    corresponding drum pad names.
- **Signal Integration:** Each key emits custom signals (noteOn and noteOff) to notify
    parent widgets of key events.
- **MIDI Channel Configuration:** The widget supports setting a MIDI channel for outgoing
    note messages.
- **Styling and Layout:** Uses QHBoxLayout and QVBoxLayout to manage key and label placement,
    ensuring a neat appearance.

Usage Example:
    from jdxi_manager.ui.widgets.piano.keyboard import PianoKeyboard
    keyboard = PianoKeyboard(parent=main_window)
    keyboard.set_midi_channel(1)
    main_window.setCentralWidget(keyboard)

This module requires PySide6 and proper integration with the JD-Xi Manager's signal handling for note events.
"""

import logging
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QSize

from jdxi_manager.ui.widgets.piano.key import PianoKey


class PianoKeyboard(QWidget):
    """Widget containing a row of piano keys styled like JD-Xi"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_channel = 0  # Default to analog synth channel

        # Set keyboard dimensions
        self.white_key_width = 35
        self.white_key_height = 160
        self.black_key_width = int(self.white_key_width * 0.6)
        self.black_key_height = 100

        # Define note patterns
        self.white_notes = [
            36,
            38,
            40,
            41,
            43,
            45,
            47,  # C1 to B1
            48,
            50,
            52,
            53,
            55,
            57,
            59,  # C2 to B2
            60,
            62,
            64,
            65,
            67,
            69,
            71,  # C3 to B3
            72,  # C4
        ]

        self.black_notes = [
            37,
            39,
            None,
            42,
            44,
            46,  # C#1 to B1
            49,
            51,
            None,
            54,
            56,
            58,  # C#2 to B2
            61,
            63,
            None,
            66,
            68,
            70,  # C#3 to B3
        ]

        # Calculate total width
        total_width = len(self.white_notes) * self.white_key_width
        self.setFixedSize(
            total_width + 2, self.white_key_height + 30
        )  # Added height for labels

        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Add drum pad labels
        labels_layout = QHBoxLayout()
        labels_layout.setSpacing(0)
        labels_layout.setContentsMargins(1, 1, 1, 1)

        # Drum pad names in order
        drum_labels = [
            "BD1",
            "RIM",
            "BD2",
            "CLP",
            "BD3",
            "SD1",
            "CHH",
            "SD2",
            "PHH",
            "SD3",
            "OHH",
            "SD4",
            "TM1",
            "PC1",
            "TM2",
            "PC2",
            "TM3",
            "PC3",
            "CY1",
            "PC4",
            "CY2",
            "PC5",
            "CY3",
            "HIT",
            "OT1",
            "OT2",
            "   ",
            "   ",
            "   ",
            "   ",
            "   ",
            "   ",
            "   ",
            "   ",
            "   ",
            "   ",
            "  ",
            " ",
        ]

        # Create and style labels
        for text in drum_labels:
            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(
                """
                QLabel {
                    color: #808080;
                    font-size: 7px;
                    font-family: monospace;
                    padding: 2px;
                    min-width: 30px;
                }
            """
            )
            labels_layout.addWidget(label)

        labels_layout.addStretch()
        main_layout.addLayout(labels_layout)

        # Create keyboard container widget
        keyboard_widget = QWidget()
        keyboard_widget.setFixedSize(total_width + 2, self.white_key_height + 2)
        keyboard_layout = QHBoxLayout(keyboard_widget)
        keyboard_layout.setSpacing(0)
        keyboard_layout.setContentsMargins(1, 1, 1, 1)

        # Create keys
        self._create_keys(keyboard_widget)

        main_layout.addWidget(keyboard_widget)

    def _create_keys(self, keyboard_widget):
        """Create piano keys"""
        # First create all white keys
        for _, note in enumerate(self.white_notes):
            key = PianoKey(
                note,
                is_black=False,
                width=self.white_key_width,
                height=self.white_key_height,
            )
            keyboard_widget.layout().addWidget(key)

            # Connect signals
            if hasattr(self.parent(), "handle_piano_note_on"):
                key.noteOn.connect(self.parent().handle_piano_note_on)
            if hasattr(self.parent(), "handle_piano_note_off"):
                key.noteOff.connect(self.parent().handle_piano_note_off)

        # Then add black keys
        black_positions = [0, 1, 3, 4, 5, 7, 8, 10, 11, 12, 14, 15, 17, 18, 19]

        for pos, note in zip(
            black_positions, [n for n in self.black_notes if n is not None]
        ):
            black_key = PianoKey(
                note,
                is_black=True,
                width=self.black_key_width,
                height=self.black_key_height,
            )
            black_key.setParent(keyboard_widget)

            # Position black key
            x_pos = (pos * self.white_key_width) + (
                self.white_key_width - self.black_key_width // 2
            )
            black_key.move(x_pos, 0)
            black_key.show()

            # Connect signals
            if hasattr(self.parent(), "handle_piano_note_on"):
                black_key.noteOn.connect(self.parent().handle_piano_note_on)
            if hasattr(self.parent(), "handle_piano_note_off"):
                black_key.noteOff.connect(self.parent().handle_piano_note_off)

    def set_midi_channel(self, channel: int):
        """Set MIDI channel for note messages"""
        self.current_channel = channel
        logging.debug(f"Piano keyboard set to channel {channel}")

    def _update_channel_display(self):
        """Update channel indicator"""
        self.channel_button.set_channel(self.current_channel)
