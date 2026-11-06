"""
Coordinated RQ1 read session with DT1 address matching and section status.

Used by Patch Manager and per-editor "Read from JD-Xi" actions so saves are
not based on stale UI state without an explicit hardware round-trip.

Replies are matched on the raw DT1 bytes from the MIDI input
(``midi_message_incoming``). The parsed ``midi_sysex_json`` signal is not used
when raw input is available: its ADDRESS field is the command byte plus only
three address bytes (e.g. ``"12194200"`` for ``19 42 00 00``), and the same
signal also carries JSON from patch files being loaded, which are not replies.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from decologr import Decologr as log
from PySide6.QtCore import QObject, QTimer, Signal

from jdxi_editor.midi.io.request_queue import DT1_COMMAND, roland_address
from jdxi_editor.midi.sysex.sections import SysExSection


class SectionStatus(str, Enum):
    PENDING = "pending"
    OK = "ok"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class ReadSectionResult:
    """Status for one expected SysEx section."""

    label: str
    address: str
    request_hex: str
    status: SectionStatus = SectionStatus.PENDING

    @property
    def ok(self) -> bool:
        return self.status == SectionStatus.OK


@dataclass
class ReadResult:
    """Outcome of a full or scoped read session."""

    sections: List[ReadSectionResult] = field(default_factory=list)

    @property
    def complete(self) -> bool:
        return bool(self.sections) and all(s.ok for s in self.sections)

    @property
    def pending_count(self) -> int:
        return sum(1 for s in self.sections if s.status == SectionStatus.PENDING)

    @property
    def ok_count(self) -> int:
        return sum(1 for s in self.sections if s.ok)

    def summary(self) -> str:
        parts = [f"{s.label}: {s.status.value}" for s in self.sections]
        return "; ".join(parts) if parts else "(no sections)"


def normalize_address(address: Optional[str]) -> str:
    """Normalize an address hex string for comparison (no spaces, lower)."""
    if not address:
        return ""
    return "".join(str(address).split()).lower()


def address_from_rq1_hex(request_hex: str) -> str:
    """
    Extract the 4-byte Roland address from an RQ1 SysEx hex string.

    RQ1 layout after the JD-Xi header: command ``11``, then address (4 bytes),
    then size (4 bytes), checksum, ``F7``.
    """
    tokens = [t for t in request_hex.strip().split() if t]
    try:
        cmd_idx = next(i for i, t in enumerate(tokens) if t.upper() == "11")
    except StopIteration as ex:
        raise ValueError(f"RQ1 hex missing command 11: {request_hex!r}") from ex
    addr_tokens = tokens[cmd_idx + 1 : cmd_idx + 5]
    if len(addr_tokens) < 4:
        raise ValueError(f"RQ1 hex too short for address: {request_hex!r}")
    return normalize_address("".join(addr_tokens))


def address_from_dt1_bytes(data: Sequence[int]) -> Optional[str]:
    """4-byte address of a Roland DT1 (data set) message, or None if *data* is not one."""
    return roland_address(data, DT1_COMMAND)


def address_from_parsed_json(address_field: Optional[str]) -> str:
    """
    Normalise the ADDRESS of a parsed-SysEx JSON payload to the 4-byte form.

    The parser reports ``command + 3 address bytes`` (``"12194200"``); patch
    JSON written by the composer uses the 4-byte address (``"19420000"``).
    """
    address = normalize_address(address_field)
    if len(address) == 8 and address.startswith("12"):
        return address[2:] + "00"
    return address


def label_for_address(address: str) -> str:
    """Human-readable label for a common JD-Xi temporary address."""
    addr = normalize_address(address)
    known = {
        "18000000": "Program Common",
        "18000100": "Vocal FX",
        "18000200": "Effect 1",
        "18000400": "Effect 2",
        "18000600": "Delay",
        "18000800": "Reverb",
        "18004000": "Arpeggio / Controller",
        "19010000": "Digital 1 Common",
        "19012000": "Digital 1 Partial 1",
        "19012100": "Digital 1 Partial 2",
        "19012200": "Digital 1 Partial 3",
        "19015000": "Digital 1 Modify",
        "19210000": "Digital 2 Common",
        "19212000": "Digital 2 Partial 1",
        "19212100": "Digital 2 Partial 2",
        "19212200": "Digital 2 Partial 3",
        "19215000": "Digital 2 Modify",
        "19420000": "Analog",
        "19700000": "Drums Common",
    }
    if addr in known:
        return known[addr]
    if addr.startswith("1970") and len(addr) == 8:
        index = drum_partial_index(addr)
        if index is not None:
            return f"Drum Partial {index + 1} (note {DRUM_FIRST_NOTE + index})"
    return addr or "Unknown"


DRUM_PARTIAL_COUNT = 38
DRUM_FIRST_NOTE = 36  # partial 1 (19 70 2E 00) is BD1, note 36
_DRUM_FIRST_LMB = 0x2E
_DRUM_PARTIAL_SIZE = (0x00, 0x00, 0x01, 0x43)


def drum_partial_index(address: str) -> Optional[int]:
    """0-based drum partial of a 19 70 xx 00 address, or None."""
    lmb = int(address[4:6], 16)
    index, odd = divmod(lmb - _DRUM_FIRST_LMB, 2)
    if odd or not 0 <= index < DRUM_PARTIAL_COUNT:
        return None
    return index


def rq1_hex(address: Sequence[int], size: Sequence[int]) -> str:
    """JD-Xi RQ1 (data request) for *size* bytes at *address*, as hex."""
    body = list(address) + list(size)
    checksum = (128 - sum(body) % 128) % 128
    data = [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x11, *body, checksum, 0xF7]
    return " ".join(f"{b:02X}" for b in data)


def patch_section_requests() -> List[Tuple[str, str]]:
    """
    (label, RQ1) for every section of a patch, whichever editors are open.

    Program Common, Vocal FX, Effects, Delay, Reverb, Zones, Arpeggio, both
    Digital synths (Common, partials, Modify), Analog, Drum Common and all 38
    drum partials.
    """
    from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests as R

    requests = [
        R.PROGRAM_COMMON,
        R.PROGRAM_VOCAL_EFFECT,
        R.PROGRAM_EFFECT1,
        R.PROGRAM_EFFECT2,
        R.PROGRAM_DELAY,
        R.PROGRAM_REVERB,
        R.PROGRAM_ZONE_DIGITAL1,
        R.PROGRAM_ZONE_DIGITAL2,
        R.PROGRAM_ZONE_ANALOG,
        R.PROGRAM_ZONE_DRUMS,
        R.PROGRAM_CONTROLLER,
        *R.DIGITAL1,
        *R.DIGITAL2,
        R.ANALOG,
        R.DRUMS[0] if isinstance(R.DRUMS, list) else R.DRUMS,
    ]
    requests += [
        rq1_hex((0x19, 0x70, _DRUM_FIRST_LMB + 2 * i, 0x00), _DRUM_PARTIAL_SIZE)
        for i in range(DRUM_PARTIAL_COUNT)
    ]
    pairs = []
    for request in requests:
        address = address_from_rq1_hex(request)
        pairs.append((label_for_address(address), request))
    return pairs


def sections_from_requests(
    requests: Sequence[str],
    *,
    labels: Optional[Sequence[str]] = None,
) -> List[ReadSectionResult]:
    """Build section results from RQ1 hex strings."""
    sections: List[ReadSectionResult] = []
    for i, req in enumerate(requests):
        if not req or not str(req).strip():
            continue
        address = address_from_rq1_hex(str(req))
        label = (
            labels[i]
            if labels is not None and i < len(labels) and labels[i]
            else label_for_address(address)
        )
        sections.append(
            ReadSectionResult(
                label=label,
                address=address,
                request_hex=str(req),
            )
        )
    return sections


def collect_editor_requests(
    editors: Iterable[Any],
    *,
    skip_types: Optional[Tuple[type, ...]] = None,
) -> List[Tuple[str, str]]:
    """
    Collect (label, rq1_hex) from editors that expose ``midi_requests``.

    Deduplicates by address (first wins).
    """
    skip_types = skip_types or ()
    seen: set[str] = set()
    out: List[Tuple[str, str]] = []
    for editor in editors or []:
        if skip_types and isinstance(editor, skip_types):
            continue
        requests = getattr(editor, "midi_requests", None)
        if not requests:
            continue
        editor_name = (
            getattr(editor, "windowTitle", lambda: None)()
            or editor.__class__.__name__
        )
        for req in requests:
            try:
                address = address_from_rq1_hex(str(req))
            except ValueError:
                continue
            if address in seen:
                continue
            seen.add(address)
            out.append((f"{editor_name}: {label_for_address(address)}", str(req)))
    return out


class PatchReadSession(QObject):
    """
    Send RQ1s and wait for matching DT1 addresses via ``midi_sysex_json``.

    Emits ``progress`` as sections update and ``finished`` with the final
    :class:`ReadResult` (complete, partial, or timed out).
    """

    progress = Signal(object)  # ReadResult snapshot
    finished = Signal(object)  # ReadResult

    def __init__(
        self,
        midi_helper,
        sections: Sequence[ReadSectionResult],
        *,
        timeout_ms: int = 8000,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self._midi_helper = midi_helper
        self._sections = list(sections)
        self._by_address: Dict[str, ReadSectionResult] = {
            s.address: s for s in self._sections
        }
        self._timeout_ms = timeout_ms
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_timeout)
        self._connected = False
        self._connected_signal = None
        self._done = False

    @property
    def result(self) -> ReadResult:
        return ReadResult(sections=list(self._sections))

    def start(self) -> None:
        """Connect to MIDI input, send RQ1s, and start the timeout timer."""
        if not self._sections:
            self._finish()
            return
        if self._midi_helper is None:
            for section in self._sections:
                section.status = SectionStatus.ERROR
            self._finish()
            return

        if not self._connected:
            # Prefer the raw MIDI input: exact addresses, and only real replies
            signal = getattr(self._midi_helper, "midi_message_incoming", None)
            slot = self._on_midi_message
            if signal is None:
                signal = getattr(self._midi_helper, "midi_sysex_json", None)
                slot = self._on_sysex_json
            if signal is not None:
                signal.connect(slot)
                self._connected = True
                self._connected_signal = (signal, slot)

        from jdxi_editor.midi.io.delay import send_with_delay
        import threading

        requests = [s.request_hex for s in self._sections]
        # Fire RQ1s off the UI thread (same as data_request)
        threading.Thread(
            target=send_with_delay,
            args=(self._midi_helper, requests),
            daemon=True,
        ).start()
        self._timer.start(self._timeout_ms)
        self.progress.emit(self.result)

    def cancel(self) -> None:
        """Stop waiting; mark remaining sections as timeout."""
        self._on_timeout()

    def _on_midi_message(self, message: Any) -> None:
        """Raw MIDI input: match DT1 replies by their exact address."""
        if self._done or getattr(message, "type", None) != "sysex":
            return
        address = address_from_dt1_bytes(getattr(message, "data", ()))
        if address:
            self._mark_received(address)

    def _on_sysex_json(self, payload: str) -> None:
        """Fallback when raw input is unavailable: match parsed-SysEx JSON."""
        if self._done:
            return
        try:
            parsed = json.loads(payload) if isinstance(payload, str) else payload
        except (TypeError, json.JSONDecodeError):
            return
        address = address_from_parsed_json(parsed.get(SysExSection.ADDRESS))
        if address:
            self._mark_received(address)

    def _mark_received(self, address: str) -> None:
        section = self._by_address.get(address)
        if section is None or section.status != SectionStatus.PENDING:
            return
        section.status = SectionStatus.OK
        self.progress.emit(self.result)
        if self.pending_count == 0:
            self._finish()

    @property
    def pending_count(self) -> int:
        return sum(1 for s in self._sections if s.status == SectionStatus.PENDING)

    def _on_timeout(self) -> None:
        if self._done:
            return
        for section in self._sections:
            if section.status == SectionStatus.PENDING:
                section.status = SectionStatus.TIMEOUT
        self._finish()

    def _finish(self) -> None:
        if self._done:
            return
        self._done = True
        self._timer.stop()
        self._disconnect()
        result = self.result
        log.message(
            f"Patch read session finished: {result.ok_count}/{len(result.sections)} ok — {result.summary()}",
            scope="PatchReadSession",
        )
        self.finished.emit(result)

    def _disconnect(self) -> None:
        if not self._connected or self._connected_signal is None:
            return
        signal, slot = self._connected_signal
        try:
            signal.disconnect(slot)
        except (TypeError, RuntimeError):
            pass
        self._connected = False
        self._connected_signal = None


def start_read_session(
    midi_helper,
    requests: Sequence[str],
    *,
    labels: Optional[Sequence[str]] = None,
    timeout_ms: int = 8000,
    on_progress: Optional[Callable[[ReadResult], None]] = None,
    on_finished: Optional[Callable[[ReadResult], None]] = None,
    parent: Optional[QObject] = None,
) -> PatchReadSession:
    """Convenience: build sections, wire callbacks, and start."""
    sections = sections_from_requests(requests, labels=labels)
    session = PatchReadSession(
        midi_helper, sections, timeout_ms=timeout_ms, parent=parent
    )
    if on_progress:
        session.progress.connect(on_progress)
    if on_finished:
        session.finished.connect(on_finished)
    session.start()
    return session
