"""
The instrument faceplate keeps the old panel's layout.

Each group of controls has a host in instrument_panel.ui at its rectangle on
the 1000 x 230 panel. The hosts are checked exactly; the controls inside them
are checked against each other with a little tolerance, because label
heights follow the platform's font.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from itertools import combinations
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QRect
from PySide6.QtWidgets import QApplication, QLabel, QSlider, QWidget

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.core.synth.type import JDXiSynth
from jdxi_editor.midi.data.control_change.digital import DigitalControlChange
from jdxi_editor.ui.image.instrument import PANEL_INSET, PANEL_SPLIT_GAP, PANEL_SPLIT_X
from jdxi_editor.ui.widgets.midi.slider.filter.cutoff import FilterCutoffSlider
from jdxi_editor.ui.widgets.rotary import ControlChangeRotary
from jdxi_editor.ui.windows.jdxi.panel import HOSTS, build_faceplate, load_instrument_form

#: x, y, width, height of each host on the 1000 x 230 panel
DESIGNED = {
    "title_host": (35, 15, 200, 50),
    "display_host": (35, 50, 210, 70),
    "octave_arp_host": (25, 125, 240, 100),
    "parts_host": (255, 15, 180, 220),
    "program_host": (385, 30, 150, 80),
    "tone_host": (385, 90, 150, 80),
    "sliders_host": (515, 15, 360, 140),
    "effects_host": (910, 15, 80, 120),
    "favorite_host": (505, 169, 34, 52),
    "sequencer_host": (535, 166, 500, 80),
}

WIDTHS = (1000, 1250)


def _window() -> QWidget:
    window = QWidget()
    window.midi_helper = Mock()
    window.digital_font_family = None
    window.current_synth_type = JDXiSynth.DIGITAL_SYNTH_1
    window.show_editor = Mock()
    window._midi_send_octave = Mock()
    window._preset_previous = Mock()
    window._preset_next = Mock()
    window._show_favorite_context_menu = Mock()
    window._save_favorite = Mock()
    window._select_synth = Mock()
    return window


@pytest.fixture(scope="module", params=WIDTHS, ids=lambda width: f"{width}px")
def shown(request):
    """A faceplate shown at an instrument width, and the window it fills."""
    window = _window()
    face = build_faceplate(window)
    face.apply_width(request.param)
    face.resize(request.param, face.height())
    face.show()
    for _ in range(10):
        _APP.processEvents()
    yield window, face
    face.close()
    face.deleteLater()
    window.deleteLater()
    # Outside an event loop deleteLater waits for this; left alive, every
    # later skin change restyles these panels too
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def _rect(widget: QWidget, face: QWidget) -> QRect:
    return QRect(widget.mapTo(face, widget.rect().topLeft()), widget.size())


def _sliders(window) -> list:
    return [slider.findChild(QSlider) or slider for slider in window.panel_sliders.values()]


def _part_buttons(window) -> list:
    return [window.part_buttons[key] for key in ("digital1", "digital2", "drums", "analog", "arp")]


def _controls(window) -> list:
    return [
        *_part_buttons(window),
        window.program_down_button,
        window.program_up_button,
        window.tone_down_button,
        window.tone_up_button,
        window.octave_down,
        window.octave_up,
        window.arpeggiator_button,
        window.key_hold_button,
        window.vocal_effects_button,
        window.effects_button,
        window.favorite_button,
        *window.sequencer_buttons,
        *_sliders(window),
    ]


def _pane(face, left: bool) -> tuple:
    sx = face.width() / JDXi.UI.Dimensions.INSTRUMENT.WIDTH
    if left:
        return PANEL_INSET * sx, PANEL_SPLIT_X * sx
    return (PANEL_SPLIT_X + PANEL_SPLIT_GAP) * sx, (JDXi.UI.Dimensions.INSTRUMENT.WIDTH - PANEL_INSET) * sx


def test_the_form_holds_one_host_per_group():
    form = load_instrument_form()
    assert (form.width(), form.height()) == (1000, 230)
    assert set(HOSTS) == set(DESIGNED)
    for name, rect in DESIGNED.items():
        assert form.findChild(QWidget, name).geometry().getRect() == rect, name


def test_hosts_sit_on_their_place_in_the_picture(shown):
    _window, face = shown
    sx = face.width() / JDXi.UI.Dimensions.INSTRUMENT.WIDTH
    sy = face.height() / JDXi.UI.Dimensions.INSTRUMENT.PANEL_HEIGHT
    assert face.height() == JDXi.UI.Dimensions.INSTRUMENT.panel_height_for(face.width())
    for name, (x, y, w, h) in DESIGNED.items():
        got = face.hosts[name].geometry().getRect()
        if face.width() == 1000:
            assert got == (x, y, w, h), name
        else:
            wanted = (x * sx, y * sy, w * sx, h * sy)
            assert all(abs(g - e) <= 1 for g, e in zip(got, wanted)), (name, got, wanted)


def test_controls_stay_on_their_gloss_pane(shown):
    window, face = shown
    left = [
        face.findChild(QLabel, "instrument_title"),
        *_part_buttons(window),
        window.program_down_button,
        window.program_up_button,
        window.tone_down_button,
        window.tone_up_button,
        window.octave_down,
        window.octave_up,
        window.arpeggiator_button,
        window.key_hold_button,
    ]
    right = [
        *_sliders(window),
        window.vocal_effects_button,
        window.effects_button,
        window.favorite_button,
        *window.sequencer_buttons,
    ]
    for widgets, is_left in ((left, True), (right, False)):
        start, end = _pane(face, is_left)
        for widget in widgets:
            rect = _rect(widget, face)
            assert start <= rect.left() and rect.right() <= end, (widget.objectName(), rect, start, end)


def test_every_control_can_be_reached(shown):
    window, face = shown
    controls = _controls(window)
    rects = [_rect(control, face) for control in controls]
    for control, rect in zip(controls, rects):
        assert face.rect().contains(rect), (control, rect)
        hit = face.childAt(rect.center())
        assert hit is control or control.isAncestorOf(hit), (control, rect, hit)
    for (a, ra), (b, rb) in combinations(zip(controls, rects), 2):
        assert not ra.intersects(rb), (a, ra, b, rb)


def test_controls_keep_the_old_arrangement(shown):
    window, face = shown
    r = lambda widget: _rect(widget, face)  # noqa: E731

    parts = [r(button) for button in _part_buttons(window)]
    assert len({part.left() for part in parts}) == 1
    pitches = [b.top() - a.top() for a, b in zip(parts, parts[1:])]
    assert max(pitches) - min(pitches) <= 2, pitches

    program, tone = r(window.program_down_button), r(window.tone_down_button)
    assert program.bottom() < tone.top()
    parts_right = max(part.right() for part in parts)
    sliders = [r(slider) for slider in _sliders(window)]
    for button in (window.program_down_button, window.tone_down_button):
        assert r(button).left() > parts_right
    for button in (window.program_up_button, window.tone_up_button):
        assert r(button).right() < sliders[0].left()
    assert [slider.left() for slider in sliders] == sorted({slider.left() for slider in sliders})
    assert len(sliders) == 10

    assert r(window.vocal_effects_button).bottom() < r(window.effects_button).top()

    favorite, first = r(window.favorite_button), r(window.sequencer_buttons[0])
    assert favorite.right() < first.left()
    assert abs(favorite.center().y() - first.center().y()) <= 4

    edge = face.height()
    for widget in [*window.sequencer_buttons, window.octave_down, window.key_hold_button]:
        assert edge - 20 <= r(widget).bottom() + 1 <= edge, widget

    sx = face.width() / JDXi.UI.Dimensions.INSTRUMENT.WIDTH
    assert abs(first.left() - JDXi.UI.Dimensions.SEQUENCER.X * sx) <= 2


def test_controls_keep_the_old_sizes(shown):
    window, face = shown
    round_buttons = [
        *_part_buttons(window),
        window.octave_down,
        window.octave_up,
        window.arpeggiator_button,
        window.key_hold_button,
        window.vocal_effects_button,
        window.effects_button,
        window.favorite_button,
    ]
    assert {(b.width(), b.height()) for b in round_buttons} == {(30, 30)}
    small = [window.program_down_button, window.program_up_button, window.tone_down_button, window.tone_up_button]
    assert {(b.width(), b.height()) for b in small} == {(25, 25)}
    assert {(b.width(), b.height()) for b in window.sequencer_buttons} == {(25, 25)}
    assert face.findChild(QLabel, "instrument_title").font().pointSize() == 24


def test_cutoff_knob_sends_the_same_control_change_as_the_slider():
    slider_helper = Mock()
    knob_helper = Mock()
    slider = FilterCutoffSlider(slider_helper)
    knob = ControlChangeRotary(
        knob_helper, "Cutoff", DigitalControlChange.get_cc_map("Cutoff")
    )
    slider.setValue(40)
    knob.setValue(40)
    assert slider_helper.send_control_change.call_args_list == knob_helper.send_control_change.call_args_list
    assert knob_helper.send_control_change.called
