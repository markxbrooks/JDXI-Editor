"""
Piano keyboard widget for JD-Xi Manager.

This module defines address PianoKeyboard widget, address custom QWidget that arranges and displays
address set of piano keys styled like those on address JD-Xi synthesizer. The widget combines both
white and black keys to form address complete piano keyboard, along with labels representing
drum pad names.

Key Features:
- **Custom Key Dimensions:** White and black keys are sized and positioned appropriately,
    with configurable widths and heights.
- **Dynamic Key Creation:** White keys are created first in address horizontal layout,
    while black keys are overlaid at specific positions.
- **Drum Pad Labels:** A row of labels is displayed above the keyboard to denote
    corresponding drum pad names.
- **Signal Integration:** Each key emits custom signals (noteOn and noteOff) to notify
    parent widgets of key events.
- **MIDI Channel Configuration:** The widget supports setting address MIDI channel for outgoing
    note messages.
- **Styling and Layout:** Uses QHBoxLayout and QVBoxLayout to manage key and label placement,
    ensuring address neat appearance.

Usage Example:
    from jdxi_editor.ui.widgets.piano.keyboard import PianoKeyboard
    keyboard = PianoKeyboard(parent=main_window)
    keyboard.set_midi_channel(1)
    main_window.setCentralWidget(keyboard)

This module requires PySide6 and proper integration with the JD-Xi Manager's signal handling for note events.
"""

from decologr import Decologr as log
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QHBoxLayout, QLabel

from jdxi_editor.midi.data.piano.keyboard import (
    DRUM_LABELS,
    KEYBOARD_BLACK_NOTES,
    KEYBOARD_WHITE_NOTES,
)
from jdxi_editor.ui.common import JDXi, QVBoxLayout, QWidget
from jdxi_editor.ui.widgets.piano.key import PianoKey


def drum_label_style(color: str) -> str:
    """
    The style of the drum labels above the keys, in ``color``.

    They sit on the instrument's body, so they are silkscreen and have to
    follow the skin: a fixed grey disappears on a pale chassis.

    :param color: str the lettering colour
    :return: str stylesheet for one label
    """
    return f"""
                QLabel {{
                    color: {color};
                    font-size: 7px;
                    font-family: monospace;
                    padding: 2px;
                    min-width: 30px;
                }}
            """


class PianoKeyboard(QWidget):
    """Widget containing a row of piano keys styled like JD-Xi"""

    noteOn = Signal(int)
    noteOff = Signal(int)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.current_channel = 0  # Default to analog synth channel

        # Connected here, once: the keys are rebuilt on every resize, by which
        # time this widget has been moved into the status bar
        if hasattr(parent, "handle_piano_note_on"):
            self.noteOn.connect(parent.handle_piano_note_on)
        if hasattr(parent, "handle_piano_note_off"):
            self.noteOff.connect(parent.handle_piano_note_off)

        # Define note patterns
        self.white_notes = KEYBOARD_WHITE_NOTES
        self.black_notes = KEYBOARD_BLACK_NOTES

        # Keys sized for an instrument of the default width; the window calls
        # set_instrument_width when it knows its own
        self._apply_key_sizes(JDXi.UI.Dimensions.INSTRUMENT.WIDTH)

        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Add drum pad labels
        labels_layout = QHBoxLayout()
        labels_layout.setSpacing(0)
        labels_layout.setContentsMargins(1, 1, 1, 1)

        # Create and style labels
        self.drum_labels = []
        for text in DRUM_LABELS:
            label = QLabel(text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.drum_labels.append(label)
            labels_layout.addWidget(label)
        self.apply_skin()

        labels_layout.addStretch()
        main_layout.addLayout(labels_layout)

        # Create keyboard container widget
        self.keyboard_widget = keyboard_widget = QWidget()
        keyboard_widget.setFixedSize(
            len(self.white_notes) * self.white_key_width + 2,
            self.white_key_height + 2,
        )
        keyboard_layout = QHBoxLayout(keyboard_widget)
        keyboard_layout.setSpacing(0)
        keyboard_layout.setContentsMargins(1, 1, 1, 1)

        # Create keys
        self._create_keys(keyboard_widget)

        main_layout.addWidget(keyboard_widget)

    #: room above the keys for the drum labels
    LABEL_HEIGHT = 30

    def _apply_key_sizes(self, instrument_width: int) -> None:
        """
        Size the keys for an instrument ``instrument_width`` px wide.

        The JD-Xi's keys run from the wheels to the right edge and are as
        long as the machine is deep below the panel, so both follow the
        width rather than being pinned to a number that is only right at one
        size.

        :param instrument_width: int the instrument's width in px
        :return: None
        """
        dimensions = JDXi.UI.Dimensions.INSTRUMENT
        span = dimensions.keys_width_for(instrument_width)
        self.white_key_width = max(18, span // len(self.white_notes))
        self.white_key_height = max(
            60, dimensions.keys_height_for(instrument_width) - self.LABEL_HEIGHT
        )
        self.black_key_width = int(self.white_key_width * 0.6)
        # ~62 % of a white key, as on the JD-Xi
        self.black_key_height = int(self.white_key_height * 0.62)
        self.setFixedSize(
            len(self.white_notes) * self.white_key_width + 2,
            self.white_key_height + self.LABEL_HEIGHT,
        )

    def _rebuild_keys(self) -> None:
        """
        Build the keys again at the current size.

        :return: None
        """
        container = getattr(self, "keyboard_widget", None)
        if container is None:
            return
        for key in container.findChildren(PianoKey):
            key.release()
            container.layout().removeWidget(key)
            key.setParent(None)
            key.deleteLater()
        container.setFixedSize(
            len(self.white_notes) * self.white_key_width + 2,
            self.white_key_height + 2,
        )
        self._create_keys(container)

    def set_instrument_width(self, instrument_width: int, depth: int = 0) -> None:
        """
        Re-size the keys for an instrument ``instrument_width`` px wide.

        Rebuilds the keys, so it returns at once when nothing would change.

        :param instrument_width: int the instrument's width in px
        :param depth: int the depth the keyboard must fill, labels included;
            0 to take it from the instrument's own proportions
        :return: None
        """
        before = (self.white_key_width, self.white_key_height)
        self._apply_key_sizes(instrument_width)
        if depth:
            # The panel takes what its controls need, so the keys take the
            # rest of the instrument's depth: that is what keeps the whole
            # thing at the JD-Xi's 2.37 : 1 whatever the panel asks for.
            self.white_key_height = max(60, depth - self.LABEL_HEIGHT)
            self.black_key_height = int(self.white_key_height * 0.62)
            self.setFixedSize(
                len(self.white_notes) * self.white_key_width + 2,
                self.white_key_height + self.LABEL_HEIGHT,
            )
        if (self.white_key_width, self.white_key_height) == before:
            return
        self._rebuild_keys()

    def apply_skin(self) -> None:
        """
        Letter the drum labels in the active skin's silkscreen.

        :return: None
        """
        from jdxi_editor.ui.style.rack_skin import active_skin

        style = drum_label_style(active_skin().foreground.text_secondary)
        for label in self.drum_labels:
            label.setStyleSheet(style)

    def _create_keys(self, keyboard_widget: QWidget) -> None:
        """
        Create piano keys with individual shadows

        :param keyboard_widget: QWidget
        """

        def apply_shadow(widget):
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setOffset(3, 3)
            shadow.setColor(QColor(0, 0, 0, 80))
            widget.setGraphicsEffect(shadow)

        # First create all white keys
        for _, note in enumerate(self.white_notes):
            key = PianoKey(
                note,
                is_black=False,
                width=self.white_key_width,
                height=self.white_key_height,
            )
            apply_shadow(key)
            keyboard_widget.layout().addWidget(key)
            key.noteOn.connect(self.noteOn)
            key.noteOff.connect(self.noteOff)

        # Add black keys
        black_positions = [0, 1, 3, 4, 5, 7, 8, 10, 11, 12, 14, 15, 17, 18, 19]

        for pos, note in zip(
            black_positions, [n for n in KEYBOARD_BLACK_NOTES if n is not None]
        ):
            black_key = PianoKey(
                note,
                is_black=True,
                width=self.black_key_width,
                height=self.black_key_height,
            )
            black_key.setParent(keyboard_widget)
            apply_shadow(black_key)

            x_pos = (pos * self.white_key_width) + (
                self.white_key_width - self.black_key_width // 2
            )
            black_key.move(x_pos, 0)
            black_key.show()
            black_key.noteOn.connect(self.noteOn)
            black_key.noteOff.connect(self.noteOff)

    def set_midi_channel(self, channel: int) -> None:
        """Set MIDI channel for note messages

        :param channel: int
        """
        self.current_channel = channel
        log.message(f"Piano keyboard set to channel {channel}")
