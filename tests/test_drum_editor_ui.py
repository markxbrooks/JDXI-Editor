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


def test_only_outermost_panels_get_the_sheen():
    """The Instrument window's sheen goes on an editor's outer panels only, not nested ones."""
    from PySide6.QtWidgets import QGroupBox

    from jdxi_editor.ui.editors.digital.editor import DigitalSynthEditor
    from jdxi_editor.ui.style.editor_style import SHEEN_PROPERTY

    editor = DigitalSynthEditor(midi_helper=MagicMock(), preset_helper=MagicMock())
    try:
        _APP.processEvents()  # marking runs once the editor is built
        assert editor.tab_widget.property(SHEEN_PROPERTY)
        nested = [g for g in editor.tab_widget.findChildren(QGroupBox)]
        assert nested and not any(g.property(SHEEN_PROPERTY) for g in nested)
    finally:
        editor.close()
        editor.deleteLater()


def test_mixer_is_laid_out_like_a_kit(drum_editor):
    """Hats and cymbals above snares and toms, kicks at the bottom; master beside them; icons kept."""
    from jdxi_editor.ui.editors.drum.mixer.lane import MixerLane
    from jdxi_editor.ui.editors.drum.mixer.section import DrumKitMixerSection

    drum_editor.resize(1600, 1100)
    drum_editor.show()
    drum_editor.presets_parts_tab_widget.setCurrentIndex(2)
    _APP.processEvents()
    mixer = drum_editor.findChild(DrumKitMixerSection)
    lanes = {lane.title(): lane for lane in mixer.findChildren(MixerLane)}

    def top(name):
        return lanes[name].mapTo(mixer, lanes[name].rect().topLeft()).y()

    def left(name):
        return lanes[name].mapTo(mixer, lanes[name].rect().topLeft()).x()

    assert top("Hi-Hat") == top("Cymbals") < top("Snare") == top("Toms") < top("Kick")
    assert left("Kit") < left("Percussion") < left("Snare") < left("Toms") < left("Other")
    assert len(mixer.mixer_sliders) == 27  # master + 26 partials, each once
    from PySide6.QtWidgets import QLabel

    icons = [l for l in mixer.findChildren(QLabel) if l.pixmap() and not l.pixmap().isNull()]
    assert len(icons) == 27  # every strip shows its drum (or keyboard) icon
    assert mixer.title_label.isVisible()  # the Drum Kit Mixer display
    # Display and every strip sit inside the one glossy panel
    from jdxi_editor.ui.style.editor_style import SHEEN_PROPERTY

    assert mixer.panel.property(SHEEN_PROPERTY)
    assert mixer.panel.isAncestorOf(mixer.title_label)
    assert all(mixer.panel.isAncestorOf(s) for s in mixer.mixer_sliders.values())
