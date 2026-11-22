"""
jdxi_editor.midi.io.data_requests
Whether the editor asks the JD-Xi for its current settings.

Editors read the synth's settings with data requests (Roland RQ1 SysEx) when
they open, on program changes and on Refresh. That needs a JD-Xi to answer.
In SoundFont mode the sound comes from FluidSynth, and often no JD-Xi is
connected at all, so the requests only go unanswered: each one waits for its
reply to time out, and the queue backs up.

The choice is stored in QSettings under ``midi_config/data_requests``. Until
it has been set, it follows the mode: requests are on with the JD-Xi preset
lists and off with "Use SoundFont List".

Only the automatic requests are switched off. A Read the user asks for
explicitly (``force=True``) is still sent, and so is everything else sent to
the synth: parameter changes, program changes and patch writes.

Example:
    >>> rq1 = bytes.fromhex("F0 41 10 00 00 00 0E 11 19 42 00 00 00 00 00 40 65 F7")
    >>> dt1 = bytes.fromhex("F0 41 10 00 00 00 0E 12 19 42 00 00 01 02 22 F7")
    >>> without_data_requests([rq1, dt1]) == [dt1]
    True
"""

from __future__ import annotations

from typing import Iterable, Optional, Sequence, Union

from PySide6.QtCore import QSettings

from jdxi_editor.midi.io.request_queue import RQ1_COMMAND, roland_address
from jdxi_editor.project import __organization_name__, __program__

DATA_REQUESTS_KEY = "midi_config/data_requests"

Message = Union[str, bytes, Sequence[int]]


def _as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes")
    return bool(value)


def stored_data_requests_setting() -> Optional[bool]:
    """The saved choice, or None if it has never been set."""
    value = QSettings(__organization_name__, __program__).value(DATA_REQUESTS_KEY, None)
    return None if value is None else _as_bool(value)


def data_requests_enabled() -> bool:
    """
    True if the editor should ask the JD-Xi for its settings: the saved
    choice, or, until one is made, on unless SoundFont mode is on.
    """
    stored = stored_data_requests_setting()
    if stored is not None:
        return stored
    from jdxi_editor.ui.editors.pattern.preset_list_provider import get_use_soundfont_list

    return not get_use_soundfont_list()


def set_data_requests_enabled(enabled: bool) -> None:
    """Save the choice."""
    settings = QSettings(__organization_name__, __program__)
    settings.setValue(DATA_REQUESTS_KEY, bool(enabled))
    settings.sync()


def is_data_request(message: Message) -> bool:
    """True for a Roland RQ1 (a request for data, which needs a reply)."""
    try:
        data = bytes.fromhex(message) if isinstance(message, str) else bytes(message)
    except (TypeError, ValueError):
        return False
    return roland_address(data, RQ1_COMMAND) is not None


def without_data_requests(messages: Iterable[Message]) -> list:
    """`messages` with the RQ1 requests taken out, in order."""
    return [m for m in messages if m and not is_data_request(m)]
