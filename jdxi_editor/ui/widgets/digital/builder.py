"""
Digital Display Builder

Builds JDXiDisplayState from program, tone, or parsed SysEx data.
"""

from typing import Any, Dict, Optional

from jdxi_editor.midi.sysex.sections import SysExSection
from jdxi_editor.ui.widgets.digital.state import JDXiDisplayState

# Map display synth key to program attribute (JDXiProgram or dict)
_SYNTH_TO_PROGRAM_ATTR = {
    "D1": "digital_1",
    "D2": "digital_2",
    "DR": "drums",
    "AN": "analog",
}

# Map SysEx address (from input_handler) to display synth key
_SYSEX_ADDRESS_TO_SYNTH = {
    "12180000": None,  # Program common: program name, not a tone
    "12190100": "D1",
    "12192100": "D2",
    "12194200": "AN",
    "12197000": "DR",
}


class DisplayStateBuilder:
    """Builds JDXiDisplayState from program, tone, or parsed SysEx data."""

    @staticmethod
    def from_program(
        program: Any,
        active_synth: str,
        octave: int = 0,
    ) -> JDXiDisplayState:
        """Build display state from a program (JDXiProgram or dict) and active synth.

        :param program: JDXiProgram or dict with id, name, digital_1, digital_2, drums, analog.
        :param active_synth: "D1" | "D2" | "DR" | "AN".
        :param octave: Current octave (default 0).
        :return: JDXiDisplayState.
        """
        program_name = _get_attr(program, "name") or "Untitled Program"
        program_id = _get_attr(program, "id") or ""
        attr = _SYNTH_TO_PROGRAM_ATTR.get(active_synth, "digital_1")
        tone_name = _get_attr(program, attr) or "Init Tone"
        return JDXiDisplayState(
            synth=active_synth,
            program_name=program_name,
            program_id=program_id,
            tone_name=tone_name,
            tone_number=0,
            octave=octave,
        )

    @staticmethod
    def from_tone(
        tone_name: str,
        tone_number: int = 0,
        active_synth: str = "D1",
        program_name: Optional[str] = None,
        program_id: Optional[str] = None,
        octave: int = 0,
    ) -> JDXiDisplayState:
        """Build display state from tone-focused data.

        :param tone_name: Name of the tone.
        :param tone_number: Tone/preset number (default 0).
        :param active_synth: "D1" | "D2" | "DR" | "AN" (default "D1").
        :param program_name: Optional program name.
        :param program_id: Optional program id (e.g. "A01").
        :param octave: Current octave (default 0).
        :return: JDXiDisplayState.
        """
        return JDXiDisplayState(
            synth=active_synth,
            program_name=program_name or "",
            program_id=program_id or "",
            tone_name=tone_name or "Init Tone",
            tone_number=tone_number,
            octave=octave,
        )

    @staticmethod
    def from_sysex(
        parsed_data: Dict[str, Any],
        program_name: Optional[str] = None,
        program_id: Optional[str] = None,
        octave: int = 0,
    ) -> Optional[JDXiDisplayState]:
        """Build display state from parsed SysEx message (e.g. from JDXiSysExParser).

        :param parsed_data: Dict with ADDRESS and TONE_NAME (SysExSection keys).
        :param program_name: Optional program name when known.
        :param program_id: Optional program id when known.
        :param octave: Current octave (default 0).
        :return: JDXiDisplayState, or None if address is program-common only (no tone).
        """
        address = parsed_data.get(SysExSection.ADDRESS) or ""
        tone_name = parsed_data.get(SysExSection.TONE_NAME) or ""

        if address == "12180000":
            return JDXiDisplayState(
                synth="D1",
                program_name=tone_name or program_name or "",
                program_id=program_id or "",
                tone_name="",
                tone_number=0,
                octave=octave,
            )

        synth = _SYSEX_ADDRESS_TO_SYNTH.get(address)
        if synth is None:
            return None
        return JDXiDisplayState(
            synth=synth,
            program_name=program_name or "",
            program_id=program_id or "",
            tone_name=tone_name or "Init Tone",
            tone_number=0,
            octave=octave,
        )


def _get_attr(obj: Any, key: str) -> Optional[str]:
    """Get attribute or dict key; return None if missing."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)
