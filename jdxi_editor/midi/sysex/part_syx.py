"""
Per-part SysEx import/export helpers (Manager-style librarian for one editor).
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, List, Optional, Tuple

from decologr import Decologr as log

from jdxi_editor.midi.sysex.json_composer import JDXiJSONComposer
from jdxi_editor.midi.sysex.request.read_session import normalize_address


def expected_address_prefix(editor: Any) -> str:
    """4-byte hex address prefix expected for this editor, if known."""
    address = getattr(editor, "address", None)
    if address is None:
        return ""
    try:
        raw = address.to_list() if hasattr(address, "to_list") else None
        if raw and len(raw) >= 4:
            return normalize_address("".join(f"{b:02x}" for b in raw[:4]))
    except Exception:
        pass
    # Fallback: first RQ1 address
    for req in getattr(editor, "midi_requests", None) or []:
        try:
            from jdxi_editor.midi.sysex.request.read_session import address_from_rq1_hex

            return address_from_rq1_hex(str(req))
        except ValueError:
            continue
    return ""


def split_sysex_messages(data: bytes) -> List[bytes]:
    """Split concatenated F0…F7 SysEx blocks."""
    messages: List[bytes] = []
    pos = 0
    while pos < len(data):
        if data[pos : pos + 1] != b"\xf0":
            pos += 1
            continue
        end = data.find(b"\xf7", pos)
        if end == -1:
            break
        messages.append(data[pos : end + 1])
        pos = end + 1
    return messages


def address_from_dt1_bytes(msg: bytes) -> str:
    """
    Extract 4-byte address from a JD-Xi DT1 message.

    Typical: F0 41 10 00 00 00 0E 12 aa aa aa aa … CS F7
    """
    if len(msg) < 14 or msg[0] != 0xF0:
        return ""
    # Find command 0x12 (DT1)
    try:
        cmd_idx = msg.index(0x12, 1, 16)
    except ValueError:
        return ""
    if cmd_idx + 4 >= len(msg):
        return ""
    return normalize_address("".join(f"{b:02x}" for b in msg[cmd_idx + 1 : cmd_idx + 5]))


def validate_part_syx(
    data: bytes,
    *,
    expected_prefix: str = "",
) -> Tuple[bool, str, List[bytes]]:
    """
    Validate a per-part .syx blob.

    :return: (ok, message, messages)
    """
    messages = split_sysex_messages(data)
    if not messages:
        return False, "No SysEx messages found in file", []
    if expected_prefix:
        exp = normalize_address(expected_prefix)
        for msg in messages:
            if msg[7:8] != b"\x12" and 0x12 not in msg[1:12]:
                # Allow non-DT1 (skip)
                continue
            addr = address_from_dt1_bytes(msg)
            if addr and not addr.startswith(exp[:4]) and addr[:4] != exp[:4]:
                # Compare first 2 address bytes (area) for part match when possible
                if exp and addr[:2] != exp[:2]:
                    return (
                        False,
                        f"Address {addr} does not match expected part prefix {exp}",
                        messages,
                    )
    return True, f"{len(messages)} SysEx message(s)", messages


def export_editor_to_syx(editor: Any, midi_helper, file_path: str) -> bool:
    """Compose JSON for one editor and write concatenated SysEx to ``file_path``."""
    if not hasattr(editor, "get_controls_as_dict"):
        log.warning("Editor cannot export: missing get_controls_as_dict")
        return False
    composer = JDXiJSONComposer()
    with tempfile.TemporaryDirectory(prefix="jdxi_part_syx_") as tmp:
        temp_folder = Path(tmp)
        try:
            composer.process_editor(editor, temp_folder)
        except Exception as ex:
            log.error(f"Error composing editor JSON for .syx: {ex}")
            return False
        return bool(midi_helper.save_patch_as_syx(file_path, temp_folder))


def import_syx_to_editor(
    midi_helper,
    editor: Any,
    file_path: str,
    *,
    refresh: bool = True,
) -> Tuple[bool, str]:
    """
    Load a .syx file, validate against the editor's address area, send to device.

    Optionally run ``editor.read_from_jdxi()`` afterward.
    """
    path = Path(file_path)
    if not path.is_file():
        return False, f"File not found: {file_path}"
    data = path.read_bytes()
    expected = expected_address_prefix(editor)
    ok, msg, messages = validate_part_syx(data, expected_prefix=expected)
    if not ok:
        return False, msg
    for msg_bytes in messages:
        try:
            midi_helper.send_raw_message(list(msg_bytes))
        except Exception as ex:
            return False, f"Failed to send SysEx: {ex}"
    if refresh and hasattr(editor, "read_from_jdxi"):
        editor.read_from_jdxi()
    elif refresh and hasattr(editor, "data_request"):
        editor.data_request()
    return True, msg
