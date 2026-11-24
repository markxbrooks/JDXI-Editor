"""
Instrument keyboard (offscreen): keys send their notes after the window has
resized them, and every key comes back up when it is let go.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMainWindow

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.ui.widgets.piano.key import PianoKey
from jdxi_editor.ui.widgets.piano.keyboard import PianoKeyboard


class Window(QMainWindow):
    """Hosts the keyboard in its status bar, as the instrument window does."""

    def __init__(self):
        super().__init__()
        self.sent = []
        self.piano_keyboard = PianoKeyboard(parent=self)
        self.statusBar().addPermanentWidget(self.piano_keyboard)

    def handle_piano_note_on(self, note: int) -> None:
        self.sent.append(("on", note))

    def handle_piano_note_off(self, note: int) -> None:
        self.sent.append(("off", note))


@pytest.fixture
def window():
    window = Window()
    window.show()
    _APP.processEvents()
    yield window
    window.close()
    window.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def _keys(window, black: bool) -> list:
    keys = window.piano_keyboard.keyboard_widget.findChildren(PianoKey)
    return [key for key in keys if key.is_black == black]


def _click(key) -> None:
    centre = QPoint(key.width() // 2, key.height() // 2)
    QTest.mousePress(key, Qt.MouseButton.LeftButton, pos=centre)
    QTest.mouseRelease(key, Qt.MouseButton.LeftButton, pos=centre)


def _settle() -> None:
    QTest.qWait(300)


def test_keys_send_notes_after_the_window_resizes_them(window):
    keyboard = window.piano_keyboard
    keyboard.set_instrument_width(keyboard.white_key_width * 40)
    _APP.processEvents()
    for black in (False, True):
        key = _keys(window, black)[0]
        window.sent.clear()
        _click(key)
        assert window.sent == [("on", key.note_num), ("off", key.note_num)]


@pytest.mark.parametrize("black", [False, True], ids=["white", "black"])
def test_a_released_key_comes_back_up(window, black):
    key = _keys(window, black)[2]
    rest = key.geometry()
    _click(key)
    _settle()
    assert not key.is_pressed
    assert key.geometry() == rest


def test_a_double_click_sends_one_note_and_lets_the_key_up(window):
    key = _keys(window, True)[1]
    rest = key.geometry()
    centre = QPoint(key.width() // 2, key.height() // 2)
    QTest.mousePress(key, Qt.MouseButton.LeftButton, pos=centre)
    QTest.mouseDClick(key, Qt.MouseButton.LeftButton, pos=centre)
    QTest.mouseRelease(key, Qt.MouseButton.LeftButton, pos=centre)
    _settle()
    assert window.sent.count(("on", key.note_num)) == window.sent.count(
        ("off", key.note_num)
    )
    assert not key.is_pressed
    assert key.geometry() == rest


def test_a_key_held_while_the_keys_are_rebuilt_sends_its_note_off(window):
    key = _keys(window, True)[0]
    note = key.note_num
    QTest.mousePress(key, Qt.MouseButton.LeftButton, pos=QPoint(2, 2))
    keyboard = window.piano_keyboard
    keyboard.set_instrument_width(keyboard.white_key_width * 40)
    assert window.sent == [("on", note), ("off", note)]
