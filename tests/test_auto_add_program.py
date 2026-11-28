"""
The program the JD-Xi reports goes into the program database once, not at
every re-read: the window re-reads the shown part every 2 s while the JD-Xi
is quiet (three writes of the same row every 2 s, and a rename each time).
"""

from types import SimpleNamespace
from unittest.mock import Mock

from jdxi_editor.midi.io import input_handler
from jdxi_editor.midi.io.input_handler import MidiInHandler
from jdxi_editor.ui.preset.incoming_data import IncomingPresetData


def test_the_same_program_is_saved_once(monkeypatch):
    saved = []
    monkeypatch.setattr(input_handler, "add_or_replace_program_and_save",
                        lambda program: saved.append(program) or True)
    data = IncomingPresetData()
    data.program_number, data.program_name, data.msb, data.lsb = 0, "E-D-M", 85, 1
    data.set_tone_name("digital_2", "JUNO Sqr Bs2")
    handler = SimpleNamespace(_incoming_preset_data=data, update_program_name=Mock())
    for _ in range(3):
        MidiInHandler._auto_add_current_program(handler)
    assert [p.id for p in saved] == ["G01"]
    assert handler.update_program_name.emit.call_count == 1
    data.set_tone_name("digital_2", "Trance Key 1")  # changed: saved again
    MidiInHandler._auto_add_current_program(handler)
    assert len(saved) == 2
