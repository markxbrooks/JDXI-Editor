"""
Transport Spec

NoteButtonSpec migration: midi_note is canonical.
- Phase 2: Properties redirect to midi_note; _sync_midi_note handles mutation.
- Phase 3 (future): Collapse to midi_note-only.
"""

from dataclasses import dataclass

from picoui.specs.widgets import ButtonSpec


@dataclass(slots=True)
class TransportSpec(ButtonSpec):
    """TransportSpec"""

    name: str = ""
    text: str = ""
