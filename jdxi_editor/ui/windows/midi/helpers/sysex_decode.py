"""
SysEx decoding for the MIDI debugger
====================================

Turns a line of hex into the byte list the debugger decodes, and decodes
JD-Xi parameter dumps of any length: a 15-byte message sets one parameter, a
longer one (a DT1 bulk dump, as the JD-Xi sends in reply to a data request)
carries a whole parameter block.

Lines copied from the log file are accepted as they are: the log prints the
message without its F0/F7 frame and follows it with the parsed dictionary, so
:func:`parse_hex_line` stops at the first token that is not a hex byte and
:func:`frame_sysex` restores F0/F7.

Example
-------
>>> parse_hex_line("41 10 00 00 00 0E 12 19 01 50 00 07 {'SYNTH_TONE': 'MODIFY'}")
[65, 16, 0, 0, 0, 14, 18, 25, 1, 80, 0, 7]
>>> frame_sysex([0x41, 0x10])
[240, 65, 16, 247]
>>> roland_checksum([0x19, 0x01, 0x50, 0x00, 0x07, 0x0B])
4
"""

from __future__ import annotations

import re
from typing import Iterable

from jdxi_editor.midi.message.sysex.offset import JDXiSysExMessageLayout
from jdxi_editor.midi.sysex.parser.utils import (
    get_parameter_class,
    get_parameter_value,
)

SYSEX_START = 0xF0
SYSEX_END = 0xF7
ROLAND_ID = 0x41
#: Index of the first data byte in a framed JD-Xi parameter message
DATA_START = JDXiSysExMessageLayout.ADDRESS.LSB + 1

_HEX_BYTE = re.compile(r"^(?:0x)?([0-9A-Fa-f]{1,2}),?$")


def parse_hex_line(line: str) -> list[int]:
    """
    Leading hex bytes of ``line``, stopping at the first token that is not one.

    :param line: str e.g. ``"F0 41 10 ..."`` or a log line ``"41 10 ... 04 {...}"``
    :return: list[int] byte values
    :raises ValueError: if the line does not start with a hex byte
    """
    values = []
    for token in line.split():
        match = _HEX_BYTE.match(token)
        if match is None:
            break
        values.append(int(match.group(1), 16))
    if not values:
        raise ValueError("no hex bytes found")
    return values


def frame_sysex(message: list[int]) -> list[int]:
    """
    ``message`` with its F0 and F7, adding whichever is missing.

    :param message: list[int] SysEx bytes, framed or not
    :return: list[int] framed message
    """
    framed = list(message)
    if not framed or framed[0] != SYSEX_START:
        framed.insert(0, SYSEX_START)
    if framed[-1] != SYSEX_END:
        framed.append(SYSEX_END)
    return framed


def roland_checksum(address_and_data: Iterable[int]) -> int:
    """
    Roland checksum: the value that makes address + data + checksum a multiple of 128.

    :param address_and_data: Iterable[int] address and data bytes
    :return: int checksum 0-127
    """
    return (128 - sum(address_and_data) % 128) % 128


def is_roland_dump(message: list[int]) -> bool:
    """
    Whether a framed ``message`` is a Roland address message longer than one parameter.

    :param message: list[int] framed SysEx bytes
    :return: bool
    """
    return (
        len(message) > DATA_START + 2
        and message[0] == SYSEX_START
        and message[1] == ROLAND_ID
    )


def _hex(values: Iterable[int]) -> str:
    return " ".join(f"{v:02X}" for v in values)


def _row(*cells: object) -> str:
    offset, name, value, raw = cells
    return f"| {offset!s:<7} | {name!s:<36} | {value!s:>7} | {raw!s:<12} |\n"


def _rule() -> str:
    return f"|{'-' * 9}|{'-' * 38}|{'-' * 9}|{'-' * 14}|\n"


def decode_parameter_dump(message: list[int]) -> str:
    """
    Table of the header and every parameter in a framed JD-Xi parameter dump.

    Data bytes no parameter covers are listed as reserved when they are not 0,
    and counted otherwise, so a mostly empty block stays readable.

    :param message: list[int] framed SysEx bytes (F0 41 ... checksum F7)
    :return: str text table
    """
    data = bytes(message)
    layout = JDXiSysExMessageLayout
    address = message[layout.ADDRESS.MSB : DATA_START]
    payload = message[DATA_START:-2]
    checksum = message[-2]
    expected = roland_checksum(address + payload)
    area, tone, parameter_cls = get_parameter_class(data)

    lines = [
        f"Roland parameter dump: {len(message)} bytes, "
        f"{len(payload)} data bytes\n",
        f"Device ID {message[layout.DEVICE_ID]:02X}  "
        f"Model ID {_hex(message[layout.MODEL_ID.POS1 : layout.COMMAND_ID])}  "
        f"Command {message[layout.COMMAND_ID]:02X}\n",
        f"Address {_hex(address)}: {area} / {tone} "
        f"({getattr(parameter_cls, '__name__', 'unknown parameters')})\n",
        f"Checksum {checksum:02X}: "
        + ("valid" if checksum == expected else f"INVALID (expected {expected:02X})")
        + "\n\n",
        _rule(),
        _row("Offset", "Parameter", "Value", "Bytes"),
        _rule(),
    ]

    covered: set[int] = set()
    rows: list[tuple[int, str]] = []
    parameters = sorted(
        (p for p in (parameter_cls or []) if 0 <= p.address < len(payload)),
        key=lambda p: p.address,
    )
    for param in parameters:
        get_size = getattr(param, "get_nibbled_size", None)
        size = get_size() if get_size else 1
        span = range(param.address, min(param.address + size, len(payload)))
        covered.update(span)
        value = get_parameter_value(data, param, DATA_START)
        rows.append(
            (
                param.address,
                _row(
                    f"0x{param.address:02X}",
                    param.name,
                    value,
                    _hex(payload[o] for o in span),
                ),
            )
        )

    reserved = [o for o in range(len(payload)) if o not in covered]
    for offset in (o for o in reserved if payload[o]):
        byte = payload[offset]
        rows.append(
            (offset, _row(f"0x{offset:02X}", "(reserved / unassigned)", byte, f"{byte:02X}"))
        )
    lines.extend(row for _, row in sorted(rows))
    lines.append(_rule())
    zero = sum(1 for o in reserved if not payload[o])
    if zero:
        lines.append(f"{zero} reserved/unassigned data bytes are 00 (not shown)\n")
    return "".join(lines)
