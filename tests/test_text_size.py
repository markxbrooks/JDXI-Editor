"""Preferences › Text size: nothing changes at Normal; Large and Larger scale the text."""

import pytest

from jdxi_editor.ui import text_size


@pytest.fixture
def size(monkeypatch):
    def choose(value):
        monkeypatch.setenv("JDXI_TEXT_SIZE", str(value))
        text_size.scale.cache_clear()
        text_size.scale_style.cache_clear()

    yield choose
    monkeypatch.delenv("JDXI_TEXT_SIZE", raising=False)
    text_size.scale.cache_clear()
    text_size.scale_style.cache_clear()


def test_normal_leaves_the_style_sheets_alone(size):
    size(100)
    css = "QLabel { font-size: 9px; color: #8a8d94; }"
    assert text_size.scale() == 1.0
    assert text_size.scale_style(css) == css


def test_larger_raises_and_scales_the_text(size):
    size(125)
    assert text_size.scale() == 1.25
    out = text_size.scale_style("QLabel { font-size: 9px; } QPushButton { font-size: 16px; }")
    assert "font-size: 15px" in out  # 9 raised to 12, then 125 %
    assert "font-size: 20px" in out
    assert text_size.scale_style("QLabel { font-size: 2px; }") == "QLabel { font-size: 2px; }"


def test_an_unknown_size_is_normal(size):
    size(300)
    assert text_size.scale() == 1.0
