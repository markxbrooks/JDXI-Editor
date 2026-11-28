"""create_centered_layout_with_widgets holds its widgets without adding itself."""

import sys

from PySide6.QtWidgets import QApplication, QLabel, QWidget

from jdxi_editor.ui.widgets.editor.helper import create_centered_layout_with_widgets

_APP = QApplication.instance() or QApplication(sys.argv)


def test_centered_layout_holds_its_widgets_without_adding_itself():
    widgets = [QLabel("a"), QLabel("b")]
    layout = create_centered_layout_with_widgets(widgets)
    host = QWidget()
    host.setLayout(layout)
    assert all(w.parentWidget() is host for w in widgets)
    assert layout.itemAt(1).layout() is not layout
