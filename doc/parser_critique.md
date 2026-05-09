## Parser Critique



This is a strong, fairly mature parser—you're already operating at the level where design clarity and invariants matter more than raw functionality. I’m going to focus on structural correctness, hidden edge cases, and where the architecture will become brittle under extension.

1. Core Architectural Issue: Parser Has Too Many Responsibilities

Your JDXiSysExParser currently does four distinct jobs:

Validation (_is_*, _verify_header)
Parsing (field extraction, structured mapping)
Transformation (→ mido.Message)
I/O side effects (JSON logging to disk)

That’s not just “a bit busy”—it actively limits reuse and testability.

The most problematic part:
with open(json_log_file, "w", encoding="utf-8") as file_handle:
    json.dump(self.sysex_dict, file_handle, ensure_ascii=False, indent=2)

You’ve embedded I/O into the parse path.

Why this is a problem:
Parsing is no longer pure → harder to test
You cannot reuse parser in real-time MIDI pipelines
You silently incur disk overhead on every message
Fix (high priority)

Extract logging into a hook:

def parse(self) -> dict:
    result = self._parse_internal()
    self._on_parse_complete(result)
    return result

def _on_parse_complete(self, parsed: dict) -> None:
    pass  # override or inject

Or inject a logger:

def __init__(..., log_sink: Optional[Callable[[dict], None]] = None):
    self.log_sink = log_sink
2. Short vs Long Message Detection Is Incorrect
if len(self.sysex_data) < JDXi.Midi.SYSEX.PARAMETER.LENGTH.FOUR_BYTE:

You’re using message length to determine:

short (1-byte param) vs long (4-byte address)

That’s not reliable.

Why?

JD-Xi SysEx messages:

have variable payload sizes
can include tone dumps, bulk data, etc.

Length ≠ semantic type.

Correct approach

Use address width or command semantics, not total length.

Example:

address_bytes = self._extract_field_bytes(address_field)

if len(address_bytes) == 1:
    ...
elif len(address_bytes) == 4:
    ...

Or better: let parse_sysex handle it entirely (you already do).

Practical conclusion:

You can delete:

_parse_short_parameter_message
_parse_long_parameter_message

They are currently redundant anyway.

3. _is_jdxi_sysex Is Overcomplicated and Still Leaky

This function is trying to distinguish:

Roland SysEx
JD-Xi SysEx
Universal identity messages

But it mixes:

positional checks
semantic checks
length heuristics
Problem area:
# Identity requests don't have Roland ID...
return False

This means:

valid MIDI identity request → rejected
parser cannot be reused in a general MIDI pipeline
Cleaner model

Split into:

def is_roland_sysex(...)
def is_jdxi_parameter(...)
def is_identity_message(...)

Then in parse():

if is_identity_message(...):
    ...
elif is_jdxi_parameter(...):
    ...
else:
    raise ValueError(...)

Right now _is_jdxi_sysex is doing too much and still ambiguous.

4. _extract_field_bytes — Overengineered Offset Resolution

This block:

if isinstance(offset, type) and hasattr(offset, "__members__"):

means you are allowing:

int
IntEnum member
IntEnum class (!!)

That last one is a design smell.

Why this is risky

You are encoding implicit rules:

if hasattr(offset, "START"):
    ...
elif hasattr(offset, "POS1"):

This is:

non-deterministic
fragile under refactor
hard to reason about
Recommendation

Normalize FieldSpec.offset at definition time.

Instead of:

offset=SomeEnum

Require:

offset=SomeEnum.START

Then _extract_field_bytes simplifies to:

if hasattr(offset, "value"):
    offset = offset.value
elif not isinstance(offset, int):
    raise TypeError(...)
5. _parse_field — Silent Failure Is Dangerous

You swallow parsing failures:

except (AttributeError, ValueError, TypeError):
    pass

Then fall back to raw bytes.

This creates:
silent data corruption
impossible debugging scenarios
Better approach

Introduce strict vs permissive mode

def __init__(..., strict: bool = False):
    self.strict = strict

Then:

except Exception as ex:
    if self.strict:
        raise
    log.debug(...)
    return raw_bytes
6. Field Mapping (_parse_fields) Is Index-Coupled
field_names = {
    0: "start",
    1: "roland_id",
    ...
}

This is brittle.

If FIELDS changes order → everything breaks silently.

Correct design

Move names into FieldSpec:

FieldSpec(name="roland_id", offset=..., length=..., parser=...)

Then:

parsed_fields[field.name] = parsed_value

This removes:

index coupling
duplication
maintenance overhead
7. Identity Parsing Has a Real Bug
"manufacturer_id": data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.ROLAND],

This assumes:

identity reply always contains Roland ID at that position

But earlier you correctly noted:

identity requests don’t have Roland ID

So this function is:

misnamed (_parse_identity_sysex)
assuming reply structure only
Fix

Split:

_parse_identity_request
_parse_identity_reply

And gate them properly.

8. convert_to_mido_message — Mixed Abstraction Layer

This method:

parses raw MIDI bytes
constructs mido.Message
handles SysEx, PC, CC

This does not belong in a SysEx parser.

Why?

You now have:

SysExParser → MIDI interpreter → transport layer object

That’s three layers collapsed into one.

Recommendation

Move to:

MidiMessageFactory.from_bytes(...)

Let the parser only handle:

bytes → structured JD-Xi meaning
9. _parse_sysex_to_mido — Chunking Logic Is Arbitrary
if len(sysex_data) > 128:

Why 128?

Not tied to MIDI spec
Not tied to JD-Xi constraints

This is a hidden policy decision.

At minimum

Make it explicit:

MAX_SYSEX_CHUNK = 128

Better: make it configurable.

10. One Very Good Design Choice

This is genuinely solid:

if hasattr(parser, "from_bytes"):
    return parser.from_bytes(raw_bytes)

You’ve effectively created a pluggable parsing system.

That’s the strongest part of this design.

Final Assessment
What’s strong
FieldSpec-driven parsing (good abstraction)
Parser extensibility via parser hooks
Clean separation of identity vs parameter parsing (conceptually)
What needs correction
Remove I/O from parsing path
Stop using message length as semantic discriminator
Eliminate index-based field naming
Simplify offset handling (no IntEnum class magic)
Introduce strict parsing mode
Separate MIDI message construction from parsing
If You Want the Next Step

The highest-impact improvement would be:

Refactor this into a two-stage pipeline:

bytes → ParsedSysExMessage (pure, structured)
ParsedSysExMessage → JD-Xi domain objects / MIDI messages

I can sketch a concrete ParsedSysExMessage dataclass + factory layer that plugs directly into your existing FieldSpec system without breaking your current API.

Yes please

Good—this is exactly the point where a clean intermediate representation (IR) will pay off. The goal is to make your parser:

pure (no side effects)
structurally typed (not just dicts)
composable (can feed UI, MIDI, logging, etc.)

Below is a concrete refactor that fits your current system without forcing a rewrite.

1. Introduce a Typed Intermediate Representation

Start with a dataclass that represents a fully parsed SysEx message:

from dataclasses import dataclass
from typing import Optional, Union


@dataclass(slots=True)
class ParsedSysExMessage:
    raw: bytes

    # Core structure
    roland_id: Optional["RolandID"]
    device_id: Optional[int]
    model_id: Optional[bytes]
    command_id: Optional["CommandID"]

    # Address + payload
    address: Optional[Union["ParameterAddress", bytes]]
    data: bytes  # raw payload after address

    # Metadata
    checksum: Optional[int]
    valid_checksum: bool

    # Classification
    message_type: str  # "parameter", "identity_request", "identity_reply", etc.

    # Optional semantic fields
    tone_name: Optional[str] = None
Why this matters

This replaces:

dict[str, Any]

with:

ParsedSysExMessage

Which gives you:

type safety
IDE support
explicit invariants
2. Refactor Parser → IR (Pure Function)

Replace your current parse() with:

def parse(self) -> ParsedSysExMessage:
    if not self.sysex_data:
        raise ValueError("No SysEx data provided")

    if not self._is_sysex_frame():
        raise ValueError("Invalid SysEx framing")

    if self._is_identity_sysex():
        return self._parse_identity_to_ir()

    if not self._verify_header():
        raise ValueError("Invalid JD-Xi header")

    return self._parse_parameter_to_ir()
Parameter Parsing → IR
def _parse_parameter_to_ir(self) -> ParsedSysExMessage:
    fields = self._parse_fields()

    raw = self.sysex_data

    # Extract core fields safely
    roland_id = fields.get("roland_id")
    device_id = fields.get("device_id")
    model_id = fields.get("model_id")
    command_id = fields.get("command_id")
    address = fields.get("address")

    checksum = fields.get("checksum")
    valid_checksum = self._validate_checksum(raw)

    # Extract payload (after address → before checksum)
    payload_start = JDXiSysExMessageLayout.ADDRESS.END
    payload_end = JDXiSysExMessageLayout.CHECKSUM

    data = raw[payload_start:payload_end]

    tone_name = self._decode_tone_name(fields.get("tone_name"))

    return ParsedSysExMessage(
        raw=raw,
        roland_id=roland_id,
        device_id=device_id,
        model_id=model_id,
        command_id=command_id,
        address=address,
        data=data,
        checksum=checksum,
        valid_checksum=valid_checksum,
        message_type="parameter",
        tone_name=tone_name,
    )
Identity Parsing → IR
def _parse_identity_to_ir(self) -> ParsedSysExMessage:
    data = self.sysex_data

    return ParsedSysExMessage(
        raw=data,
        roland_id=None,
        device_id=data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.DEVICE],
        model_id=None,
        command_id=None,
        address=None,
        data=data,
        checksum=None,
        valid_checksum=True,
        message_type="identity_reply",
    )
3. Move Field Names Into FieldSpec

Fix your biggest structural weakness.

Before:
field_names = {0: "start", 1: "roland_id", ...}
After:
@dataclass
class FieldSpec:
    name: str
    offset: int
    length: Optional[int]
    parser: Optional[Any] = None

Then:

def _parse_fields(self) -> dict:
    parsed = {}

    for field in JDXiSysExMessageLayout.FIELDS:
        try:
            parsed[field.name] = self._parse_field(field)
        except Exception as ex:
            if self.strict:
                raise
            log.debug(...)
    return parsed
4. Add Checksum Validation (You Don’t Have This Yet)

JD-Xi uses Roland checksum:

def _validate_checksum(self, data: bytes) -> bool:
    # Exclude F0 and F7
    body = data[1:-2]
    checksum = data[-2]

    total = sum(body)
    computed = (128 - (total % 128)) % 128

    return computed == checksum

This is critical for:

detecting corrupted MIDI streams
validating dumps
5. Separate Conversion Layer (IR → mido)

Move this OUT of the parser.

class MidiMessageFactory:
    @staticmethod
    def from_parsed(parsed: ParsedSysExMessage):
        if parsed.message_type == "parameter":
            return mido.Message("sysex", data=list(parsed.raw[1:-1]))

        if parsed.message_type == "identity_reply":
            return mido.Message("sysex", data=list(parsed.raw[1:-1]))

        return None
6. Optional: Domain Layer (JD-Xi Semantic Objects)

This is where things get powerful.

@dataclass
class JDXiParameterChange:
    address: "ParameterAddress"
    value: bytes


class JDXiMessageDecoder:
    @staticmethod
    def decode(parsed: ParsedSysExMessage):
        if parsed.message_type != "parameter":
            return None

        return JDXiParameterChange(
            address=parsed.address,
            value=parsed.data,
        )

Now you have:

bytes → ParsedSysExMessage → Domain Object → MIDI/UI/etc.
7. Logging Becomes Optional and Clean
class SysExLogger:
    def __call__(self, parsed: ParsedSysExMessage):
        path = ...
        with open(path, "w") as f:
            json.dump(parsed.__dict__, f, indent=2)

Inject it:

parser = JDXiSysExParser(log_sink=SysExLogger())
8. Net Result (What You Gain)
Before
dict-based parsing
implicit structure
side effects in parser
fragile field mapping
After
typed IR (ParsedSysExMessage)
pure parsing step
pluggable downstream consumers
stable extension path
9. Minimal Migration Strategy

You don’t need to break your API.

Keep:

def get_structured_fields(self) -> dict:
    return self._parse_fields()

Add:

def parse_to_ir(self) -> ParsedSysExMessage:
    return self.parse()

Gradually migrate callers.

If You Want to Push This Further

Next logical step:

Replace bytes data payload with bitfield-aware parameter decoding

i.e.:

ParsedSysExMessage → StructuredParameterBlock (per JD-Xi tone layout)

That’s where your JDXiSysExParameterLayout becomes extremely powerful.

I can sketch that layer next if you want to turn this into a full bidirectional patch editor pipeline.

## Action Plan

The safest way to act on this critique is to separate behavior-changing work from structural cleanup. The parser is already in active use by MIDI input handling, preset/tone updates, SysEx JSON forwarding, and outbound message logging, so the migration should keep the existing dict-based API available until each caller has been moved deliberately.

### Phase 1: Add Coverage Around Current Behavior

Before refactoring, lock down the behavior the application depends on today.

- Add parser tests for representative JD-Xi parameter SysEx messages, identity replies, malformed frames, short messages, and tone-name payloads.
- Add tests proving that existing public methods still return the same dict keys and values expected by current callers.
- Add tests for invalid checksum, truncated payload, unknown non-JD-Xi SysEx, and universal identity messages.
- Capture the current behavior of permissive parsing, including fallback-to-raw-bytes behavior, so strict mode can be introduced without surprising existing code.

Acceptance criteria:

- The test suite has fixtures for valid parameter messages, identity messages, and invalid/corrupt messages.
- Current parser behavior is documented by tests before internal structure changes begin.
- No production call sites need to change in this phase.

### Phase 2: Introduce a Typed ParsedSysExMessage IR

Add the intermediate representation alongside the existing parser output. Do not replace `parse_bytes()` or existing dict-returning methods yet.

- Create a `ParsedSysExMessage` dataclass for raw bytes, message type, device/model/command fields, address, payload data, checksum, checksum validity, and optional semantic fields such as tone name.
- Add `parse_to_ir()` as a new parser entry point.
- Implement `_parse_parameter_to_ir()`, `_parse_identity_request_to_ir()`, and `_parse_identity_reply_to_ir()`.
- Keep existing dict output by adapting from the IR where practical, or by preserving the current path temporarily.

Acceptance criteria:

- Existing callers still work without modification.
- New tests can assert structured fields on `ParsedSysExMessage`.
- Identity request and identity reply are represented as distinct message types.

### Phase 3: Remove Side Effects From Parsing

Move JSON file writing and other parse-time side effects out of the parser core.

- Add an optional `log_sink` or parse-completion hook.
- Move JSON serialization into a dedicated `SysExLogger` or caller-level sink.
- Ensure real-time MIDI input parsing does not write to disk unless explicitly configured.
- Preserve current debug output through an injected sink during transition if needed.

Acceptance criteria:

- Calling the parser no longer writes files by default.
- Logging behavior is opt-in and testable.
- MIDI input handling can parse messages without disk I/O.

### Phase 4: Normalize FieldSpec and Field Parsing

Make field definitions explicit and remove index-coupled parsing.

- Add `name` to `FieldSpec`.
- Update `JDXiSysExMessageLayout.FIELDS` so each field declares its own name.
- Replace `_parse_fields()` index-name mapping with `parsed[field.name] = ...`.
- Normalize `FieldSpec.offset` at definition time so offsets are concrete integers or enum members, not enum classes.
- Simplify `_extract_field_bytes()` after callers stop relying on enum-class magic.

Acceptance criteria:

- Reordering `FIELDS` does not silently change parsed field names.
- `_extract_field_bytes()` has deterministic offset handling.
- Tests cover field parsing by field name rather than list position.

### Phase 5: Add Strict and Permissive Modes

Make parse failures explicit without breaking existing permissive behavior.

- Add `strict: bool = False` to the parser constructor.
- In permissive mode, preserve fallback-to-raw behavior but log debug context.
- In strict mode, re-raise parse failures with enough field context to diagnose bad layouts or corrupt data.
- Use strict mode in unit tests for parser internals and permissive mode in real-time MIDI paths unless a caller explicitly wants validation failure.

Acceptance criteria:

- Strict mode fails fast on malformed fields.
- Permissive mode keeps the current application behavior.
- Parse errors include field name, offset, length, and raw bytes where possible.

### Phase 6: Replace Length-Based Message Classification

Remove semantic decisions based on total message length.

- Split classification into clear predicates: SysEx frame, universal identity request/reply, Roland SysEx, JD-Xi parameter message.
- Use command ID, model ID, address presence, and layout-specific rules instead of `len(self.sysex_data)` for parser branching.
- Delete redundant `_parse_short_parameter_message` and `_parse_long_parameter_message` once no callers depend on them.

Acceptance criteria:

- Bulk/tone dump-sized messages are not misclassified as a different semantic type because of length.
- Universal identity messages are accepted or rejected by a dedicated identity path.
- Dead short/long parsing methods are removed.

### Phase 7: Validate Roland Checksums

Add checksum validation as metadata first, then decide where strict enforcement belongs.

- Implement Roland checksum calculation over the correct address and data range.
- Store `valid_checksum` on `ParsedSysExMessage`.
- In permissive mode, parse corrupt messages but mark them invalid.
- In strict mode, raise on invalid checksum for parameter messages.

Acceptance criteria:

- Tests include valid and invalid checksum fixtures.
- UI and logging code can display checksum validity without recalculating it.
- Strict parsing rejects corrupt parameter SysEx messages.

### Phase 8: Move MIDI Object Conversion Out of the Parser

Separate parsing from transport-layer object construction.

- Create `MidiMessageFactory.from_bytes()` or `MidiMessageFactory.from_parsed()`.
- Move `convert_to_mido_message()` and `_parse_sysex_to_mido()` behavior into the factory.
- Replace the arbitrary `128` chunking constant with a named, configurable policy if chunking is still required.
- Keep a deprecated parser wrapper temporarily if external callers still use `convert_to_mido_message()`.

Acceptance criteria:

- `JDXiSysExParser` only parses SysEx into structured data.
- Mido construction lives in a dedicated conversion layer.
- Existing callers have a clear migration path.

### Phase 9: Introduce Domain Decoding

Once the IR is stable, add a semantic layer for JD-Xi concepts.

- Add domain objects such as `JDXiParameterChange`, `JDXiToneNameMessage`, and future patch/tone block structures.
- Decode `ParsedSysExMessage` into domain objects based on address and command semantics.
- Keep UI code consuming domain objects where possible instead of raw dicts.

Acceptance criteria:

- UI update paths no longer need to understand raw SysEx offsets.
- Address-specific behavior lives in decoder classes, not in the parser.
- The same parsed message can feed UI updates, logs, and MIDI routing without reparsing.

### Recommended Implementation Order

1. Add fixtures and tests for current behavior.
2. Add `ParsedSysExMessage` and `parse_to_ir()` without changing callers.
3. Move parser side effects behind an injected sink.
4. Add `FieldSpec.name` and remove index-based field naming.
5. Add strict mode and checksum metadata.
6. Replace length-based classification with explicit predicates.
7. Move mido conversion into a factory.
8. Migrate callers from dict output to IR/domain objects one subsystem at a time.

The key rule is to keep one stable public surface during each phase. The first milestone should not be "rewrite the parser"; it should be "the parser can produce a typed IR while everything else still works." Once that is true, the rest of the cleanup becomes incremental instead of risky.