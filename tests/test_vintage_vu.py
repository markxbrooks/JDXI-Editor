"""
The Mini Moog skin's Audio Monitor meters: a pair of backlit analogue VU
meters. The needle reads the average level on a VU scale (0 VU = -18 dBFS);
the digital peak is shown apart, as a number and a peak LED.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.audio.audio_snapshot import DB_FLOOR  # noqa: E402
from jdxi_editor.ui.style.rack_skin import SKINS, MeterStyle, active_skin, set_active_skin  # noqa: E402
from jdxi_editor.ui.widgets.audio.analog_vu import (  # noqa: E402
    EXPLANATION,
    LED_OFF,
    RED,
    VU_REFERENCE_DBFS,
    FaceGeometry,
    face_rects,
    led_centre,
    scale_fraction,
    vu_from_dbfs,
)
from jdxi_editor.ui.widgets.audio.vu_meter import VUMeter  # noqa: E402

W, H = 900, 260


@pytest.fixture
def minimoog():
    previous = active_skin().skin_id
    set_active_skin("minimoog", remember=False)
    yield
    set_active_skin(previous, remember=False)


def _meter(levels):
    meter = VUMeter()
    meter.resize(W, H)
    meter.set_levels(*levels)
    meter.show()
    _APP.processEvents()
    image = meter.grab().toImage()
    sx, sy = image.width() / meter.width(), image.height() / meter.height()
    meter.close()
    return image, sx, sy


def _darkest_near(image, point, sx, sy, radius=3):
    best = 255 * 3
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            c = image.pixelColor(int(point.x() * sx) + dx, int(point.y() * sy) + dy)
            best = min(best, c.red() + c.green() + c.blue())
    return best


def test_the_vintage_skins_have_vintage_meters():
    # The Mini Moog, the brushed-metal 1970s rack gear, and the ARP 2600
    assert {s.skin_id for s in SKINS.values() if s.meter == MeterStyle.VINTAGE_VU} == {
        "minimoog", "brushed_70s", "arp2600"
    }


def test_the_vu_scale_is_aligned_to_minus_18_dbfs():
    assert VU_REFERENCE_DBFS == -18.0
    assert vu_from_dbfs(-18.0) == 0.0
    assert vu_from_dbfs(-21.0) == -3.0


def test_the_scale_is_linear_in_voltage_like_a_real_vu_meter():
    assert scale_fraction(-20) == 0.0 and scale_fraction(3) == pytest.approx(1.0)
    # 0 VU sits about two thirds of the way across; -20..-10 is squeezed left
    assert 0.65 < scale_fraction(0) < 0.75
    assert scale_fraction(-10) - scale_fraction(-20) < scale_fraction(3) - scale_fraction(0)
    # Off the scale, the needle rests on its pins
    assert scale_fraction(-60) == 0.0 and scale_fraction(+20) == pytest.approx(1.0)


def test_the_faces_sit_side_by_side_in_the_housing():
    housing, left, right = face_rects(W, H)
    assert housing.contains(left) and housing.contains(right)
    assert left.right() < right.left()
    assert left.size() == right.size()
    assert 1.3 <= left.width() / left.height() <= 1.9


def test_the_needle_reads_the_vu_level(minimoog):
    # Left at 0 VU (-18 dBFS RMS), right at -10 VU (-28 dBFS RMS)
    image, sx, sy = _meter((-6.0, -14.0, -18.0, -28.0, -6.0, -14.0))
    _, left, right = face_rects(W, H)
    for face, vu in ((left, 0.0), (right, -10.0)):
        geo = FaceGeometry(face)
        on = geo.point(vu, 0.75)  # along the needle, inside the arc
        off = geo.point(vu + (4 if vu < 0 else -4), 0.75)
        assert _darkest_near(image, on, sx, sy) < 150
        assert _darkest_near(image, off, sx, sy, radius=1) > 450  # the cream face


def test_the_red_zone_is_above_zero_vu(minimoog):
    image, sx, sy = _meter((DB_FLOOR,) * 6)
    _, left, _right = face_rects(W, H)
    geo = FaceGeometry(left)
    red = image.pixelColor(int(geo.point(1.5, 0.985).x() * sx), int(geo.point(1.5, 0.985).y() * sy))
    assert abs(red.red() - RED.red()) < 40 and red.green() < 90
    black = image.pixelColor(int(geo.point(-5, 1.0).x() * sx), int(geo.point(-5, 1.0).y() * sy))
    assert black.red() < 120


def test_the_peak_led_lights_near_full_scale(minimoog):
    image, sx, sy = _meter((-0.5, -20.0, -20.0, -30.0, -0.5, -20.0))
    _, left, right = face_rects(W, H)
    lit = image.pixelColor(int(led_centre(left).x() * sx), int(led_centre(left).y() * sy))
    dark = image.pixelColor(int(led_centre(right).x() * sx), int(led_centre(right).y() * sy))
    assert lit.red() > 200 and lit.red() > lit.green() + 80
    assert dark.red() < 120


def test_the_tooltip_explains_the_two_scales(minimoog):
    meter = VUMeter()
    assert meter.toolTip() == EXPLANATION
    assert "-18 dBFS" in EXPLANATION and "peak" in EXPLANATION.lower()
    meter.close()


def test_other_skins_keep_the_bars(minimoog):
    set_active_skin("glossy_black", remember=False)
    meter = VUMeter()
    meter.set_levels(*(DB_FLOOR,) * 6)
    assert meter.toolTip() == ""
    assert meter.maximumHeight() == meter.minimumHeight()  # the fixed bar height
    meter.close()
