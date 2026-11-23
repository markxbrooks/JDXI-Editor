"""
The Audio Monitor paints a snapshot. No input device is opened.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))

import numpy as np
import pytest
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.audio.audio_snapshot import (  # noqa: E402
    BAND_COUNT,
    DB_FLOOR,
    WAVEFORM_COLUMNS,
    AudioSnapshot,
)
from jdxi_editor.ui.style.rack_skin import MeterStyle, active_skin  # noqa: E402
from jdxi_editor.ui.widgets.audio.audio_monitor import AudioMonitor  # noqa: E402
from jdxi_editor.ui.widgets.audio.oscilloscope import (  # noqa: E402
    Oscilloscope,
    trace_y,
)
from jdxi_editor.ui.widgets.audio.spectrum_display import SpectrumDisplay  # noqa: E402
from jdxi_editor.ui.widgets.audio.vu_meter import (  # noqa: E402
    ARC_RADIUS,
    NEEDLE_RADIUS,
    VUMeter,
    bar_x,
    dial_rects,
    needle_tip,
    row_bar,
    track_rect,
)
from jdxi_editor.ui.widgets.rack import RackPanel  # noqa: E402
from jdxi_editor.ui.windows.audio.monitor import AudioMonitorWindow  # noqa: E402


def _distance(first: QColor, second: QColor) -> int:
    return (
        abs(first.red() - second.red())
        + abs(first.green() - second.green())
        + abs(first.blue() - second.blue())
    )


def _grab(widget):
    widget.show()
    _APP.processEvents()
    image = widget.grab().toImage()
    return image, image.width() / widget.width(), image.height() / widget.height()


def _near(image, x, y, scale_x, scale_y, color: QColor, radius: int = 4) -> bool:
    px = int(x * scale_x)
    py = int(y * scale_y)
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            sx = min(image.width() - 1, max(0, px + dx))
            sy = min(image.height() - 1, max(0, py + dy))
            if _distance(image.pixelColor(sx, sy), color) <= 40:
                return True
    return False


@pytest.fixture(autouse=True)
def default_skin():
    """
    Pin the default skin. Otherwise these tests draw in whichever skin is
    saved in the user's settings, and the Mini Moog's VU faces replace the
    bars and dials they check.
    """
    from jdxi_editor.ui.style.rack_skin import set_active_skin

    previous = active_skin().skin_id
    set_active_skin("glossy_black", remember=False)
    yield
    set_active_skin(previous, remember=False)


def test_the_scope_leaves_a_phosphor_trail():
    lcd = active_skin().lcd
    scope = Oscilloscope()
    scope.resize(400, 160)
    high = np.full((WAVEFORM_COLUMNS, 2), 0.85, dtype=np.float32)
    low = np.full((WAVEFORM_COLUMNS, 2), -0.85, dtype=np.float32)
    quiet = np.zeros((WAVEFORM_COLUMNS, 2), dtype=np.float32)
    scope.set_waveform(high, quiet)
    scope.set_waveform(low, quiet)
    image, sx, sy = _grab(scope)
    try:
        assert _near(image, 80, trace_y(160, 0.85), sx, sy, QColor(lcd.text_dim))
        assert _near(image, 80, trace_y(160, -0.85), sx, sy, QColor(lcd.text))
    finally:
        scope.close()


def test_a_full_bar_reaches_zero_and_red_is_only_at_the_clip():
    lcd = active_skin().lcd
    meter = VUMeter()
    meter.resize(400, meter.height())
    meter.set_levels(0.0, DB_FLOOR, 0.0, DB_FLOOR, DB_FLOOR, DB_FLOOR)
    image, sx, sy = _grab(meter)
    try:
        track = track_rect(meter.width(), meter.height())
        bar = row_bar(track, 0)
        y = bar.center().y()
        clip = image.pixelColor(int(bar_x(track, -1.0) * sx), int(y * sy))
        middle = image.pixelColor(int(bar_x(track, -10.0) * sx), int(y * sy))
        assert _near(image, bar_x(track, -1.0), y, sx, sy, QColor(224, 68, 53))
        assert _near(image, bar_x(track, -10.0), y, sx, sy, QColor(lcd.text))
        assert _distance(middle, QColor(224, 68, 53)) > 80
        meter.set_levels(DB_FLOOR, DB_FLOOR, DB_FLOOR, DB_FLOOR, DB_FLOOR, DB_FLOOR)
        image, sx, sy = _grab(meter)
        floor = image.pixelColor(int(bar_x(track, -1.0) * sx), int(y * sy))
        assert _distance(floor, QColor(224, 68, 53)) > 80
        assert _distance(floor, clip) > 40
    finally:
        meter.close()


def test_needles_draw_when_the_skin_asks():
    skin = active_skin()
    previous = skin.meter
    skin.meter = MeterStyle.NEEDLES
    meter = None
    try:
        lcd = skin.lcd
        meter = VUMeter()
        meter.resize(400, 180)
        meter.set_levels(0.0, DB_FLOOR, DB_FLOOR, DB_FLOOR, DB_FLOOR, DB_FLOOR)
        image, sx, sy = _grab(meter)
        rect = dial_rects(400, 180)[0]
        origin = rect.center()
        radius = rect.width() / 2.0
        tip = needle_tip(origin.x(), origin.y(), radius * NEEDLE_RADIUS, 0.0)
        assert _near(image, tip[0], tip[1], sx, sy, QColor(lcd.text), radius=6)
        overload = needle_tip(origin.x(), origin.y(), radius * ARC_RADIUS, -1.5)
        assert _near(image, overload[0], overload[1], sx, sy, QColor(224, 68, 53), radius=6)
    finally:
        skin.meter = previous
        if meter is not None:
            meter.close()


def test_one_spectrum_band_lights_its_column():
    lcd = active_skin().lcd
    display = SpectrumDisplay()
    display.resize(403, 160)
    bands = np.full(BAND_COUNT, DB_FLOOR)
    bands[15] = 0.0
    display.set_spectrum(bands)
    image, sx, sy = _grab(display)
    try:
        assert _near(image, 15.5 * 403 / 31, 4, sx, sy, QColor(lcd.text))
        assert _near(image, 0.5 * 403 / 31, 4, sx, sy, QColor(lcd.bg_edge))
        dark = image.pixelColor(int(0.5 * 403 / 31 * sx), int(4 * sy))
        assert _distance(dark, QColor(lcd.text)) > 80
    finally:
        display.close()


def test_a_snapshot_reaches_every_instrument_without_a_device():
    monitor = AudioMonitor()
    columns = np.zeros((WAVEFORM_COLUMNS, 2), dtype=np.float32)
    snapshot = AudioSnapshot(
        rms_left=-12.0,
        rms_right=-18.0,
        peak_left=-6.0,
        peak_right=-9.0,
        peak_hold_left=-3.0,
        peak_hold_right=-4.0,
        vu_left=-12.0,
        vu_right=-18.0,
        spectrum=np.full(BAND_COUNT, DB_FLOOR),
        waveform_left=columns,
        waveform_right=columns,
        sample_rate=48000,
        timebase_ms=20,
    )
    monitor.show_snapshot(snapshot)
    assert monitor.vu._peak == (-6.0, -9.0)
    assert monitor.vu._vu == (-12.0, -18.0)
    assert monitor.spectrum._bands[0] == DB_FLOOR
    assert monitor.scope._left is not None
    assert not monitor._timer.isActive()
    monitor.close()


def test_the_monitor_window_is_a_rack_panel():
    window = AudioMonitorWindow()
    try:
        assert isinstance(window.centralWidget(), RackPanel)
        assert window.windowTitle() == "Audio Monitor"
        assert window.monitor.show_scope.isChecked()
        assert window.monitor.show_vu.isChecked()
        assert window.monitor.show_spectrum.isChecked()
        assert window.monitor.listen_button.isCheckable()
        assert not window.monitor.listen_button.isChecked()
        assert not window.monitor.stop_button.isEnabled()  # nothing to stop yet
    finally:
        window.close()


def test_opening_the_monitor_leaves_the_application_stylesheet_alone():
    """
    Opening the window used to apply qdarktheme to the whole application,
    which re-polished every widget of every open editor (seconds) and
    replaced the application's own stylesheet. Its dark controls are now
    set on the window only.
    """
    own = "QTabWidget::tab-bar { alignment: center; }"
    previous = _APP.styleSheet()
    _APP.setStyleSheet(own)
    window = AudioMonitorWindow()
    try:
        assert _APP.styleSheet() == own
    finally:
        window.close()
        _APP.setStyleSheet(previous)



def test_round_start_and_stop_buttons(monkeypatch):
    """Start lights while listening; the round Stop button stops."""
    from jdxi_editor.audio.audio_source import InputDeviceSource

    # Before the widget is built: it disables Start when sounddevice cannot
    # be imported, and a disabled button ignores click(). Patching afterwards
    # passes only where sounddevice happens to be installed.
    monkeypatch.setattr(InputDeviceSource, "available", staticmethod(lambda: True))
    monitor = AudioMonitor()
    monkeypatch.setattr(monitor.source, "start", lambda device=None: 48_000)
    monkeypatch.setattr(monitor.source, "stop", lambda: None)
    try:
        assert monitor.listen_button.isEnabled()
        size = monitor.stop_button.size()
        assert size.width() == size.height()  # round, not a text button
        monitor.listen_button.click()
        assert monitor.listen_button.isChecked() and monitor.stop_button.isEnabled()
        assert monitor.status.text() == "Listening (48 kHz)"
        monitor.listen_button.click()  # Start again does not stop
        assert monitor.listen_button.isChecked() and monitor._timer.isActive()
        monitor.stop_button.click()
        assert not monitor.listen_button.isChecked()
        assert not monitor.stop_button.isEnabled()
        assert not monitor._timer.isActive()
        assert monitor.status.text() == "Stopped"
    finally:
        monitor.close()



def test_readout_headings_stay_legible_on_every_skin():
    """Pale skins print dark ink; the headings sit on a dark surface."""
    from jdxi_editor.ui.style.rack_skin import SKINS
    from jdxi_editor.ui.widgets.audio.audio_monitor import _contrast, _heading_colour

    for skin in SKINS.values():
        assert _contrast(_heading_colour(skin), skin.chassis.surface) >= 3.0, skin.skin_id


def test_the_analyser_measures_at_the_rate_the_input_opened(monkeypatch):
    """
    The JD-Xi's USB audio opens at 44.1 kHz, not the monitor's 48 kHz, and
    the timebase and spectrum must be measured at the rate actually opened.
    """
    from jdxi_editor.audio.audio_source import InputDeviceSource

    monkeypatch.setattr(InputDeviceSource, "available", staticmethod(lambda: True))
    monitor = AudioMonitor()
    monkeypatch.setattr(monitor.source, "start", lambda device=None: 44_100)
    monkeypatch.setattr(monitor.source, "stop", lambda: None)
    try:
        monitor.start()
        assert monitor.analyser.sample_rate == 44_100
        assert monitor.analyser.spectrum.sample_rate == 44_100
        assert monitor.status.text() == "Listening (44.1 kHz)"
    finally:
        monitor.stop()
        monitor.close()
