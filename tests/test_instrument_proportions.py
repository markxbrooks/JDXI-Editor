"""
Instrument window proportions follow the JD-Xi (562 x 236 mm, 2.38 : 1).

- the panel is drawn exactly PANEL_HEIGHT tall (no stretching or cropping)
- the step row and the round buttons sit along the bottom edge of the panel
- panel and keyboard split the depth about 56 / 44 %, as in Roland's top view
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.image.instrument import draw_instrument_pixmap


@pytest.fixture(scope="module")
def window():
    """
    The Instrument window on its own MidiIOHelper (the class is a singleton):
    the window connects lambdas to the helper's signals, which outlive it and
    would send read requests whenever later tests use the shared helper.
    """
    from jdxi_editor.midi.io.helper import MidiIOHelper
    from jdxi_editor.ui.windows.jdxi.instrument import JDXiInstrument

    shared = MidiIOHelper._instance
    MidiIOHelper._instance = None
    try:
        w = JDXiInstrument()
    finally:
        own = MidiIOHelper._instance
        MidiIOHelper._instance = shared
    w.show()
    for _ in range(10):
        _APP.processEvents()
    yield w
    w.close()
    own.device.requests.clear()
    from PySide6.QtCore import QCoreApplication, QEvent

    w.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_panel_image_is_the_panel():
    pixmap = draw_instrument_pixmap()
    assert pixmap.height() == JDXi.UI.Dimensions.INSTRUMENT.PANEL_HEIGHT


def test_proportions_match_the_jdxi(window):
    panel = window.centralWidget().height()
    keys = window.statusBar().height()
    assert panel == JDXi.UI.Dimensions.INSTRUMENT.PANEL_HEIGHT
    ratio = window.width() / (panel + keys)
    assert 2.30 <= ratio <= 2.50  # JD-Xi 2.38
    assert 0.52 <= panel / (panel + keys) <= 0.60


def test_bottom_row_sits_on_the_panel_edge(window):
    panel = window.centralWidget()

    def bottom(widget):
        return widget.mapTo(panel, widget.rect().bottomLeft()).y()

    edge = panel.height()
    for widget in [*window.sequencer_buttons, window.octave_down, window.key_hold_button, window.favorite_button]:
        assert edge - 20 <= bottom(widget) <= edge, widget


def test_finish_matte_body_and_glossy_panel():
    from PySide6.QtGui import QColor

    from jdxi_editor.ui.image.instrument import PANEL_INSET
    from jdxi_editor.ui.style.editor_style import BODY_PROPERTY, AppEditorStyle

    image = draw_instrument_pixmap().toImage()
    body = QColor(image.pixel(2, 2))  # outside the panel inset
    panel = QColor(image.pixel(PANEL_INSET + 40, image.height() - PANEL_INSET - 10))
    assert 30 <= body.red() <= 55  # rough black reads as dark grey
    assert panel.red() < body.red() - 15  # glossy black panel (with its sheen)
    sheet = AppEditorStyle.editor_stylesheet()
    assert f'QWidget[{BODY_PROPERTY}="true"]' in sheet and "background-image" in sheet
    assert "qlineargradient" in sheet.split("QGroupBox {")[1].split("}")[0]


def test_editor_roots_get_the_body_finish():
    from unittest.mock import Mock

    from jdxi_editor.midi.io.helper import MidiIOHelper
    from jdxi_editor.ui.editors.effects.common import EffectsCommonEditor
    from jdxi_editor.ui.style.editor_style import BODY_PROPERTY

    editor = EffectsCommonEditor(midi_helper=MidiIOHelper())
    try:
        assert editor.property(BODY_PROPERTY) is True
    finally:
        editor.close()
