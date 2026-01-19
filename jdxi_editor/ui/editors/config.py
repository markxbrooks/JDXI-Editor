"""
Configuration of Editor classes for the JDXI Editor.

Stores
-Title: The title of the editor.
-Editor Class: The class that implements the editor functionality.
-Synth Type: Optional type of synthesizer associated with the editor.
-MIDI Channel: Optional MIDI channel for the editor.
-icon: Icon for the editor, represented as a string.
-Keyword Arguments: Additional parameters for the editor.


Example usage:
"arpeggio": EditorConfig(
    title="Arpeggiator",
    editor_class=ArpeggioEditor,
    icon="ph.music-notes-simple-bold"
),
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class EditorConfig:
    """Configuration for a synth editor."""

    title: str
    editor_class: Optional[Any]
    synth_type: Optional[Any] = None
    midi_channel: Optional[Any] = None
    kwargs: Dict[str, Any] = field(default_factory=dict)
    icon: str = ""
