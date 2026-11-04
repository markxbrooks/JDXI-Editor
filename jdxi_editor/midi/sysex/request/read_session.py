"""
Coordinated RQ1 read session with DT1 address matching and section status.

Used by Patch Manager and per-editor "Read from JD-Xi" actions so saves are
not based on stale UI state without an explicit hardware round-trip.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from decologr import Decologr as log
from PySide6.QtCore import QObject, QTimer, Signal

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
    if addr.startswith("1970"):
        return f"Drum Partial ({addr[4:6]})"
    return addr or "Unknown"


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

        if hasattr(self._midi_helper, "midi_sysex_json") and not self._connected:
            self._midi_helper.midi_sysex_json.connect(self._on_sysex_json)
            self._connected = True

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

    def _on_sysex_json(self, payload: str) -> None:
        if self._done:
            return
        try:
            parsed = json.loads(payload) if isinstance(payload, str) else payload
        except (TypeError, json.JSONDecodeError):
            return
        address = normalize_address(parsed.get(SysExSection.ADDRESS))
        if not address:
            return
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
        if not self._connected:
            return
        try:
            self._midi_helper.midi_sysex_json.disconnect(self._on_sysex_json)
        except (TypeError, RuntimeError):
            pass
        self._connected = False


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
