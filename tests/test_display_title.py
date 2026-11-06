"""
DigitalTitle lines and the shared input style (no MIDI hardware).

- the status line (part name, tempo) and the tone name are kept apart, so
  setting either never overwrites the other, with or without a BANK/PC line
- the global combo / line edit styles follow the shared rule (grey, accent on
  focus), not a red top bar
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.ui.style.jdxi import JDXiUIStyle
from jdxi_editor.ui.widgets.digital.title import DigitalTitle


def test_status_and_tone_lines_are_independent():
    title = DigitalTitle(tone_name="New pattern")
    assert title.display_texts == ["New pattern"]  # no blank status line
    title.set_upper_display_text("Tempo: 120 BPM")
    assert title.display_texts == ["Tempo: 120 BPM", "New pattern"]
    title.setText("Loaded: groove.mid")
    assert title.display_texts == ["Tempo: 120 BPM", "Loaded: groove.mid"]
    title.set_upper_display_text("Tempo: 132 BPM | Bar 2.5")
    assert title.text == "Loaded: groove.mid"


def test_part_name_tone_and_bank_line():
    title = DigitalTitle(tone_name="Init Tone")
    title.set_upper_display_text("DIGITAL SYNTH 1")
    title.set_wire_detail(bank_msb=95, bank_lsb=64, program=0)
    title.setText("Trem EP 1")
    assert title.display_texts == ["DIGITAL SYNTH 1", "Trem EP 1", "BANK 95/64 · PC 0"]
    assert title.text == "Trem EP 1"
    title.set_wire_detail()  # cleared
    assert title.display_texts == ["DIGITAL SYNTH 1", "Trem EP 1"]


def test_global_inputs_follow_the_shared_rule():
    for name in ("COMBO_BOX", "COMBO_BOX_ANALOG", "QLINEEDIT", "QLINEEDIT_ANALOG"):
        style = getattr(JDXiUIStyle, name)
        assert "border-top" not in style, name
        assert ":focus" in style, name


def test_sliders_share_the_jdxi_look_except_analog():
    """One slider look: neon red (Analog: neon blue), as the synth sections' ADSR style."""
    import re

    from jdxi_editor.ui.style.editor_style import AppEditorStyle

    def handle_rules(sheet: str) -> list[str]:
        return re.findall(r"QSlider::handle:(?:horizontal|vertical)\s*\{([^}]*)\}", sheet)

    digital = handle_rules(AppEditorStyle.editor_stylesheet())
    analog = handle_rules(AppEditorStyle.editor_stylesheet(accent=JDXiUIStyle.ACCENT_ANALOG))
    assert len(digital) == len(analog) == 2  # horizontal and vertical
    assert all(JDXiUIStyle.SLIDER_NEON in rule for rule in digital)
    assert all(JDXiUIStyle.SLIDER_NEON_ANALOG in rule for rule in analog)
    # Vertical handle identical to the sections' ADSR style
    adsr = handle_rules(JDXiUIStyle.ADSR)[0]
    assert " ".join(digital[0].split()).split("border: 2px solid")[1][:8] in adsr
