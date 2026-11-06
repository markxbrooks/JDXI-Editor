"""
Drum editor UI (no MIDI hardware).

- mixer mute buttons are lit while muted, dark while playing
- Partial Coarse Tune reads as a note name (0 = C-1)
- a tone name reported by the synth selects the matching preset and its
  BANK/PC line; an unknown name clears the BANK/PC line
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.ui.editors.drum.partial.partial import note_name
from jdxi_editor.ui.editors.program.channel_strip import ChannelStrip
from jdxi_editor.ui.style.factory import generate_sequencer_button_style


def test_mute_lit_only_while_muted():
    strip = ChannelStrip(title="BD1", slider=None, value_label=None, icon=None)
    assert strip.mute.styleSheet() == generate_sequencer_button_style(False)
    strip.mute.setChecked(True)
    assert strip.mute.styleSheet() == generate_sequencer_button_style(True)


@pytest.mark.parametrize("note, name", [(0, "C-1"), (36, "C2"), (60, "C4"), (127, "G9")])
def test_coarse_tune_note_names(note, name):
    assert note_name(note) == name


@pytest.fixture
def drum_editor():
    from jdxi_editor.ui.editors.drum.editor import DrumCommonEditor

    editor = DrumCommonEditor(midi_helper=MagicMock(), preset_helper=MagicMock())
    yield editor
    editor.close()
    editor.deleteLater()


def test_reported_tone_selects_matching_preset(drum_editor):
    combo = drum_editor.instrument_preset.instrument_selection_combo
    title = drum_editor.instrument_preset.instrument_title_label
    target = next(o for o in combo.options if "CR-78" in o)
    name = target.split(" - ", 1)[1]

    drum_editor.set_instrument_title_label(name, drum_editor.preset_type)
    assert combo.combo_box.currentText() == target
    assert "PC" in title._wire_detail

    drum_editor.set_instrument_title_label("My Edited Kit", drum_editor.preset_type)
    assert combo.combo_box.currentText() == target  # left where it was
    assert title._wire_detail == ""


def _lightness_at(host, widget, x, y):
    from PySide6.QtCore import QPoint

    point = widget.mapTo(host, QPoint(x, y))
    return host.grab().toImage().pixelColor(point).lightness()


def test_glossy_panels_survive_the_main_editor_host():
    """
    In the app every editor sits in MainEditor's QTabWidget, and MainEditor is
    itself an editor body: the editors' panels must stay glossy black there.
    """
    from PySide6.QtWidgets import QGroupBox

    from jdxi_editor.ui.editors.digital.editor import DigitalSynthEditor
    from jdxi_editor.ui.editors.main import MainEditor
    from jdxi_editor.ui.editors.midi_player.editor import MidiFilePlayer

    host = MainEditor()
    digital = DigitalSynthEditor(midi_helper=MagicMock(), preset_helper=MagicMock())
    player = MidiFilePlayer(midi_helper=MagicMock(), preset_helper=MagicMock())
    host.editor_tab_widget.addTab(digital, "Digital Synth 1")
    host.editor_tab_widget.addTab(player, "MIDI File")
    host.resize(1600, 1000)
    host.show()
    _APP.processEvents()
    try:
        pane = digital.tab_widget
        glossy = _lightness_at(host, pane, pane.width() // 2, pane.height() - 30)
        matte = _lightness_at(host, digital, 8, digital.height() // 2)
        assert glossy < 25 < matte

        host.editor_tab_widget.setCurrentWidget(player)
        _APP.processEvents()
        def outermost(group):
            parent = group.parentWidget()
            while parent is not None and parent is not player:
                if isinstance(parent, QGroupBox):
                    return False
                parent = parent.parentWidget()
            return True

        panel = next(g for g in player.findChildren(QGroupBox) if outermost(g))
        assert _lightness_at(host, panel, panel.width() // 2, panel.height() - 10) < 25
    finally:
        host.close()
        host.deleteLater()


def test_pads_select_partial_pages(drum_editor):
    tabs = drum_editor.partial_tab_widget
    grid = drum_editor.pad_grid
    assert not tabs.tabBar().isVisible()
    assert len(grid.pads) == tabs.count()  # 26 partials + Common
    grid.pads[12].click()  # TOM1
    assert tabs.currentIndex() == 12 and tabs.tabText(12) == "TOM1"
    tabs.setCurrentIndex(3)
    assert grid.current() == 3 and grid.pads[3].isChecked()
