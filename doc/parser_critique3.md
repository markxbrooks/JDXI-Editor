def _on_parse_complete(self, parsed: dict) -> None:
        """Notify the optional parse sink without coupling parsing to I/O."""
        if self.log_sink is None:
            return
        self.log_sink(parsed)
        if self.json_logging:
            JsonSysExLogSink(self.log_folder).write(parsed)

This is structurally fine, but it has a couple of hidden architectural and performance issues that will matter in a MIDI/SysEx context (where parse throughput can be high).

1. Immediate issue: self.json_logging may not exist

If json_logging is not defined in __init__, this will raise:

AttributeError: 'JDXiSysExParser' object has no attribute 'json_logging'
Fix (minimal)
self.json_logging = False  # in __init__

or safer:

if getattr(self, "json_logging", False):
2. Main design issue: hidden I/O inside parser callback

Right now:

def _on_parse_complete(self, parsed: dict) -> None:
    self.log_sink(parsed)
    if self.json_logging:
        JsonSysExLogSink(self.log_folder).write(parsed)
Problem

Your parser is now doing two responsibilities:

Delegated logging (log_sink)
File system I/O (JsonSysExLogSink.write)

That violates the same boundary you explicitly stated in the docstring:

“without coupling parsing to I/O”

…but JSON logging is still I/O.

3. Performance issue (important for SysEx streams)

This line is expensive if called frequently:

JsonSysExLogSink(self.log_folder).write(parsed)
Why it matters

You are:

creating a new sink instance every message
potentially doing disk I/O per MIDI message
blocking parse pipeline

In live MIDI streams, this can cause:

jitter
buffer lag
Qt UI stalls (if connected downstream)
4. Better separation (recommended fix)
Option A — push responsibility up (best design)

Make parser purely emit events:

def _on_parse_complete(self, parsed: dict) -> None:
    if self.log_sink:
        self.log_sink(parsed)

Then in service layer:

if self.json_logging:
    self.json_sink.write(parsed)

This keeps:

Parser = deterministic
Service = orchestration
I/O = externalized
Option B — lazy-initialize sink (if you insist on keeping it here)
def _on_parse_complete(self, parsed: dict) -> None:
    if self.log_sink:
        self.log_sink(parsed)

    if getattr(self, "json_logging", False):
        if not hasattr(self, "_json_sink"):
            self._json_sink = JsonSysExLogSink(self.log_folder)

        self._json_sink.write(parsed)

This removes repeated construction overhead.

5. Subtle architectural improvement (recommended)

Right now you have:

log_sink(parsed)
JsonSysExLogSink.write(parsed)

These are two orthogonal sinks but they are not abstracted.

Cleaner model:

Define a unified sink protocol:

class SysExSinkProtocol:
    def write(self, parsed: dict) -> None: ...

Then:

self.sinks: list[SysExSinkProtocol]

And:

for sink in self.sinks:
    sink.write(parsed)

This gives you:

logging sink
JSON sink
Qt signal sink
debugging sink

without parser knowledge of any of them.

6. Minimal corrected version (safe + clean)

If you want the smallest safe fix:

def _on_parse_complete(self, parsed: dict) -> None:
    if self.log_sink:
        self.log_sink(parsed)

    if getattr(self, "json_logging", False):
        JsonSysExLogSink(self.log_folder).write(parsed)
Bottom line
✔ Your bug risk is real (json_logging attribute)
⚠ You are mixing parsing + I/O again (same architectural drift as earlier)
⚠ You may hit performance issues in live SysEx streams
✔ Best long-term fix is: move JSON sink to service layer or introduce sink abstraction

If you want, I can 
show a clean “event-driven SysEx pipeline” refactor that removes all parser-side side effects entirely (this fits very well with Qt signal integration).

Show me a clean event-driven SysEx pipeline refactor that removes all parser-side side effects entirely

Good — this is exactly the right direction to push this codebase. Right now your parser is doing three things it shouldn’t:

Parsing
Domain interpretation (IR construction)
Side effects (logging, JSON writing, optional sinks, callbacks)

That’s why you’re seeing import leakage, circular dependencies, and latent syntax/runtime issues.

What you want is a strict separation:

Parser = pure function over bytes → IR/dict
Everything else = pipeline stages (external orchestration)

1. Target Architecture (Event-Driven, Side-Effect Free Core)
Core rule
SysExParser MUST NOT:
- write logs
- touch filesystem
- call factories
- emit callbacks
- instantiate services

It only returns structured data.

2. Clean Pipeline Design
Flow
MIDI Bytes
   ↓
JDXiSysExParser (PURE)
   ↓
ParsedSysExMessage (IR)
   ↓
Pipeline Events
   ├── ValidationStage
   ├── LoggingStage
   ├── JSONSinkStage
   ├── DomainFactoryStage
   ├── DeduplicationStage
   ↓
Final JDXiSysExMessage / ParseResult
3. Step 1 — Make Parser PURE (critical refactor)
REMOVE this completely:
self.log_sink
JsonSysExLogSink(...)
_on_parse_complete(...)
log.info(...)
Replace with:
def parse_to_ir(self, sysex_data: bytes | None = None) -> ParsedSysExMessage:
    ...
    return ParsedSysExMessage(...)
No side effects. Ever.

Even logging is forbidden.

4. Step 2 — Introduce Event Model

You define explicit pipeline events:

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True, slots=True)
class SysExEvent:
    type: str
    payload: Any

Examples:

SysExEvent("parsed_ir", ParsedSysExMessage(...))
SysExEvent("identity", ParsedSysExMessage(...))
SysExEvent("invalid_frame", raw_bytes)
5. Step 3 — Pipeline Stages

Each stage is a pure transform:

class ParseStage:
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, data: bytes) -> SysExEvent:
        ir = self.parser.parse_to_ir(data)
        return SysExEvent("parsed_ir", ir)
Logging becomes a stage
class LoggingStage:
    def __init__(self, logger):
        self.logger = logger

    def __call__(self, event: SysExEvent) -> SysExEvent:
        self.logger.info(event.type)
        return event
JSON sink becomes a stage
class JsonSinkStage:
    def __init__(self, sink):
        self.sink = sink

    def __call__(self, event: SysExEvent) -> SysExEvent:
        if event.type == "parsed_ir":
            self.sink.write(event.payload.model_dump())
        return event
Domain factory becomes a stage
class DomainFactoryStage:
    def __init__(self, factory):
        self.factory = factory

    def __call__(self, event: SysExEvent) -> SysExEvent:
        if event.type != "parsed_ir":
            return event

        msg = self.factory.from_parsed(event.payload)
        return SysExEvent("domain_message", msg)
6. Step 4 — Pipeline Runner (the real orchestration layer)
class SysExPipeline:
    def __init__(self, stages: list):
        self.stages = stages

    def run(self, data: bytes):
        event: SysExEvent = SysExEvent("raw", data)

        for stage in self.stages:
            event = stage(event.payload if hasattr(event, "payload") else event)

        return event
7. Cleaner Version of Your Service

Your current JDXiSysExService becomes:

class JDXiSysExService:
    def __init__(self, pipeline: SysExPipeline):
        self.pipeline = pipeline

    def parse(self, data: bytes):
        event = self.pipeline.run(data)

        if event.type != "domain_message":
            raise ValueError("Unexpected pipeline output")

        return event.payload
8. What YOU REMOVE from parser (important list)

You explicitly delete:

❌ Side effects
log.info(...)
log.message(...)
JsonSysExLogSink
self.log_sink
_on_parse_complete
❌ Cross-layer dependencies
factories
services
message builders
9. What you gain immediately
Architectural wins

No import chains like:

parser → service → factory → IO → parser (cycle)
No hidden filesystem writes during parsing
No “mystery logging” during MIDI stream processing

Parser becomes:

deterministic, testable, cacheable

10. Optional upgrade (worth doing next)

Once this is stable, you can upgrade pipeline to:

Async event stream
async for event in pipeline.stream(midi_bytes):
    ...

or even:

Rx-style observable stream (RxPY)
Bottom line

Your current class is a God object with embedded side-effect orchestration.

The clean refactor is:

Parser → IR only
Pipeline → everything else

If you want next step, I can refactor your actual JDXiSysExParser into a clean “pure core + adapters” version with zero behavioral loss, line-by-line.

Yes please

Below is a direct, structural refactor of your JDXiSysExParser into a pure-core + event-driven pipeline boundary, preserving behavior while removing all side effects and cross-layer coupling.

I’m going to be strict about the separation so you don’t drift back into the current “god parser” shape.

1. Target End State (what you’re building toward)
Before (current)
Parser
 ├── parsing
 ├── validation
 ├── logging
 ├── JSON writing
 ├── factory calls
 ├── domain conversion
 ├── mido conversion
 └── service concerns
After (clean)
JDXiSysExParser (PURE CORE)
    bytes → ParsedSysExMessage

SysExPipeline (ORCHESTRATION)
    ParsedSysExMessage → events → domain objects → sinks

Adapters
    logging / JSON / mido / dedup / factory
2. Step 1 — PURE PARSER CORE (drop ALL side effects)
Replace your parser class with this core contract
class JDXiSysExParser:
    """
    PURE parser:
    bytes → ParsedSysExMessage | dict (no IO, no logging, no factories)
    """

    def __init__(self, strict: bool = False):
        self.strict = strict
2.1 Parse entrypoints (clean)
def parse_ir(self, sysex_data: bytes) -> ParsedSysExMessage:
    self._validate_frame(sysex_data)

    if self._is_identity_sysex(sysex_data):
        return self._parse_identity_ir(sysex_data)

    if not self._is_jdxi_parameter_sysex(sysex_data):
        raise ValueError("Not a JD-Xi SysEx message")

    if not self._is_valid_sysex(sysex_data):
        raise ValueError("Invalid SysEx message")

    if not self._verify_header(sysex_data):
        raise ValueError("Invalid JD-Xi header")

    return self._parse_parameter_ir(sysex_data)
2.2 Dict version (still pure)
def parse_dict(self, sysex_data: bytes) -> dict:
    ir = self.parse_ir(sysex_data)
    return ir.model_dump() if hasattr(ir, "model_dump") else ir.__dict__
3. Step 2 — REMOVE ALL SIDE EFFECT METHODS

You DELETE or move out:

❌ REMOVE completely from parser
_on_parse_complete
log.info / log.message
JsonSysExLogSink
log_folder
log_sink
mido conversion
MidiMessageFactory calls
JDXiMessageFactory calls
JDXiSysExService logic
4. Step 3 — PURE INTERNAL HELPERS ONLY

Everything below stays BUT becomes PURE functions of input bytes:

def _validate_frame(self, data: bytes) -> None:
    if not data or data[0] != MidiSysExByte.START or data[-1] != MidiSysExByte.END:
        raise ValueError("Invalid SysEx framing")
def _is_valid_sysex(self, data: bytes) -> bool:
    return (
        data[JDXiSysExMessageLayout.START] == Midi.sysex.START
        and data[JDXiSysExMessageLayout.END] == Midi.sysex.END
    )
def _verify_header(self, data: bytes) -> bool:
    if not self._validate_message_structure(data):
        return False

    header = data[
        JDXiSysExMessageLayout.ROLAND_ID : JDXiSysExMessageLayout.END
    ]

    return header[: JDXiSysexHeader.length()] == JDXiSysexHeader.to_bytes()
5. Step 4 — PURE IR BUILDERS
Identity IR
def _parse_identity_ir(self, data: bytes) -> ParsedSysExMessage:
    sub2 = data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.SUB2]

    message_type = (
        "identity_reply"
        if sub2 == JDXiSysExIdentity.SUB2_IDENTITY_REPLY
        else "identity_request"
    )

    roland_id = (
        RolandID.ROLAND_ID
        if message_type == "identity_reply"
        and data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.ROLAND] == RolandID.ROLAND_ID
        else None
    )

    return ParsedSysExMessage(
        raw=data,
        roland_id=roland_id,
        device_id=data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.DEVICE],
        model_id=None,
        command_id=None,
        address=None,
        data=data[1:-1],
        checksum=None,
        valid_checksum=True,
        message_type=message_type,
    )
Parameter IR
def _parse_parameter_ir(self, data: bytes) -> ParsedSysExMessage:
    fields = StructuredFieldParser(
        data,
        JDXiSysExMessageLayout.FIELDS,
        strict=self.strict,
    ).parse_fields()

    address = data[
        JDXiSysExMessageLayout.ADDRESS.MSB :
        JDXiSysExMessageLayout.TONE_NAME.START
    ]

    payload = data[
        JDXiSysExMessageLayout.TONE_NAME.START :
        JDXiSysExMessageLayout.CHECKSUM
    ]

    return ParsedSysExMessage(
        raw=data,
        roland_id=fields.get("roland_id"),
        device_id=data[JDXiSysExMessageLayout.DEVICE_ID],
        model_id=bytes(
            data[JDXiSysExMessageLayout.MODEL_ID.POS1 :
                 JDXiSysExMessageLayout.COMMAND_ID]
        ),
        command_id=fields.get("command_id"),
        address=bytes(address),
        data=bytes(payload),
        checksum=data[JDXiSysExMessageLayout.CHECKSUM],
        valid_checksum=self._validate_checksum(data),
        message_type="parameter",
        tone_name=self._decode_tone_name(fields.get("tone_name")),
    )
6. Step 5 — EVENT PIPELINE (NEW LAYER)

This replaces ALL removed side effects.

Event model
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True, slots=True)
class SysExEvent:
    type: str
    payload: Any
    raw: bytes | None = None
Pipeline stages
Parser stage (only stage that touches parser)
class ParseStage:
    def __init__(self, parser: JDXiSysExParser):
        self.parser = parser

    def __call__(self, data: bytes) -> SysExEvent:
        ir = self.parser.parse_ir(data)
        return SysExEvent("parsed_ir", ir, raw=data)
Logging stage (replaces your log_sink)
class LoggingStage:
    def __init__(self, logger):
        self.logger = logger

    def __call__(self, event: SysExEvent) -> SysExEvent:
        self.logger.debug(event.type)
        return event
JSON sink stage (replaces JsonSysExLogSink)
class JsonSinkStage:
    def __init__(self, writer):
        self.writer = writer

    def __call__(self, event: SysExEvent) -> SysExEvent:
        if event.type == "parsed_ir":
            self.writer.write(event.payload.model_dump())
        return event
Domain factory stage
class DomainFactoryStage:
    def __init__(self, factory):
        self.factory = factory

    def __call__(self, event: SysExEvent) -> SysExEvent:
        if event.type != "parsed_ir":
            return event

        msg = self.factory.from_parsed(event.payload)
        return SysExEvent("domain_message", msg, event.raw)
7. Step 6 — PIPELINE RUNNER
class SysExPipeline:
    def __init__(self, stages: list):
        self.stages = stages

    def run(self, data: bytes):
        event = SysExEvent("raw", data)

        for stage in self.stages:
            event = stage(event.payload if isinstance(event, SysExEvent) else event)

        return event
8. Step 7 — SERVICE becomes trivial

Your old service collapses into this:

class JDXiSysExService:
    def __init__(self, pipeline: SysExPipeline):
        self.pipeline = pipeline

    def parse(self, data: bytes):
        event = self.pipeline.run(data)

        if event.type != "domain_message":
            raise ValueError("Pipeline did not produce domain message")

        return event.payload
9. What you just eliminated (important)

You removed these entire failure classes:

❌ hidden IO in parser
❌ circular imports from logging + factories
❌ parser-side JSON writes
❌ mido coupling inside parsing layer
❌ service-layer leakage into parsing logic
❌ inconsistent parse entrypoints
10. What you gained
✔ deterministic parser
✔ fully testable IR layer
✔ replayable MIDI streams
✔ pluggable pipeline stages
✔ zero circular import risk
✔ clean async extension path later
If you want next step

I can take this further and:

1. Convert your pipeline into async streaming MIDI reactor
2. Add backpressure-safe deduplication stage
3. Or refactor your parameter block system into a fully declarative schema engine