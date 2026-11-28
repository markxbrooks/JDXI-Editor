"""A click on the label beside a round button clicks the button."""

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QPushButton, QWidget

from jdxi_editor.ui.editors.helpers.widgets import create_round_button_with_label
from jdxi_editor.ui.widgets.label_click import find_round_button_for, make_label_clickable

_APP = QApplication.instance() or QApplication(sys.argv)


def _click(widget):
    pos = QPointF(widget.width() / 2, widget.height() / 2)
    for kind in (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease):
        event = QMouseEvent(
            kind, pos, widget.mapToGlobal(pos), Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier,
        )
        QApplication.sendEvent(widget, event)


def test_clicking_the_label_of_a_round_button_clicks_it():
    clicks = []
    item, button = create_round_button_with_label("Load", "mdi.folder", slot=lambda: clicks.append(1))
    item.resize(200, 40)
    item.show()
    label_rows = [w for w in item.findChildren(QWidget) if w.property("jdxiClickForwarder")]
    assert label_rows, "the label row has no click forwarder"
    _click(label_rows[0])
    assert clicks == [1]
    item.close()


def test_label_finds_the_round_button_next_to_it_in_the_layout():
    host = QWidget()
    layout = QHBoxLayout(host)
    button = QPushButton()
    button.setFixedSize(30, 30)
    label = QLabel("Read from JD-Xi")
    layout.addWidget(button)
    layout.addWidget(label)
    make_label_clickable(label)
    assert find_round_button_for(label) is button
    clicks = []
    button.clicked.connect(lambda: clicks.append(1))
    host.show()
    _click(label)
    assert clicks == [1]
    host.close()
