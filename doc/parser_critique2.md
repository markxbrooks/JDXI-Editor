Critique 2

Yes—this class is actually a very strong reference design, and there are several patterns here that map almost directly onto your JDXiSysExParser. In fact, your SysEx parser would benefit significantly from adopting a few of these ideas more rigorously.

I’ll focus only on what’s transferable and high-value.

1. The Most Important Pattern: Clean Multi-Stage Pipeline

Your ligand parser has a very clear pipeline:

file → grouped raw records → structured domain objects → deduplicated domain objects

Concretely:

_group_hetatm_records → create_pdb_ligand_info → _deduplicate_ligands
Compare to your SysEx parser

Right now you effectively have:

bytes → dict → (sometimes) mido.Message → (sometimes) file

That’s flat and overloaded.

What you should adopt

Mirror the ligand pipeline:

bytes → ParsedSysExMessage (IR) → Domain Object → Optional transforms (dedup, merge, etc.)

You already started this with ParsedSysExMessage—this confirms you’re on the right track.

2. Declarative Layout Parsing (You Did This Right—They Did It Better)

This is excellent:

parsed = {
    spec.name: spec.parse(line)
    for spec in HETATMLayout.__dict__.values()
    if isinstance(spec, PDBLineSpec)
}
Why this is powerful
No index coupling
Fully declarative
Self-describing layout
Your current SysEx version (weaker)

You still have:

field_names = {0: "start", 1: "roland_id", ...}
What to learn

Move fully to:

FieldSpec(name="roland_id", offset=..., length=..., parser=...)

Then:

parsed[field.name] = ...

Exactly like the PDB parser.

3. Domain Object Creation Is Explicit and Isolated

This is a big win:

pdb_ligand = create_pdb_ligand_info(pdb_ligand_data)

Notice:

Parsing does NOT create final objects
A separate factory layer does
Your SysEx parser problem

You currently mix:

parsing
interpretation
conversion to MIDI
What to adopt

Introduce:

JDXiMessageFactory.from_parsed(parsed: ParsedSysExMessage)

Just like:

create_pdb_ligand_info(...)
4. Deduplication Strategy = Extremely Transferable

This is one of the most valuable patterns:

_ligand_dedup_key()
_group_ligands_by_identity()
_select_best_ligand()

This is domain-aware canonicalization.

Where this applies to SysEx

You will eventually need to deduplicate:

repeated parameter updates
redundant tone dumps
identical patch data
Example adaptation
def sysex_dedup_key(msg: ParsedSysExMessage):
    return (msg.address, msg.data)


def deduplicate_messages(messages):
    groups = defaultdict(list)
    for m in messages:
        groups[sysex_dedup_key(m)].append(m)

    return [group[-1] for group in groups.values()]  # keep latest

Same pattern. Different domain.

5. “Best Instance Selection” Pattern
max(ligands, key=lambda l: (l.atom_count, bool(l.smiles), bool(l.coordinates)))

This is subtle but important:

You define quality metrics and select the best representation.

SysEx equivalent

You might rank messages by:

checksum validity
payload completeness
timestamp (latest wins)

Example:

def select_best_message(messages):
    return max(
        messages,
        key=lambda m: (
            m.valid_checksum,
            len(m.data),
        ),
    )
6. Graceful Degradation (You Don’t Do This Yet)

PDB parser:

try:
    ...
except Exception:
    log.exception(...)

and continues.

Your SysEx parser

You often:

raise ValueError(...)

That’s fine for strict mode—but not for streaming MIDI.

What to adopt

Support both modes:

strict=True → raise
strict=False → skip + log

The ligand parser is implicitly non-strict streaming-friendly.

7. Data Container Pattern (Very Important)
@dataclass
class PDBLigandData:
    atoms: list[dict]

This is a staging structure, not the final object.

You need this

Right now you jump from:

bytes → final dict

Instead, you should have:

bytes → ParsedSysExMessage → JDXiParameterBlock → higher-level objects

That middle layer is missing in your system.

8. Identity Key Strategy Is Gold

This:

return ligand.canonical_smiles

→ fallback

formula + atom_count

→ fallback

residue identity
This pattern is extremely reusable

For SysEx:

def identity_key(msg):
    if msg.address:
        return msg.address
    if msg.command_id:
        return msg.command_id
    return msg.raw[:8]  # fallback signature

Layered identity resolution is a very robust design pattern.

9. Separation of Concerns Is Much Cleaner
PDB parser:
parsing
grouping
domain construction
deduplication

Each is a separate method

Your SysEx parser:

Still has:

parsing
validation
transformation
I/O
MIDI conversion

All in one class.

10. What Not to Copy

To be precise—don’t blindly copy:

1. Dict-heavy atom storage
atoms: list[dict]

You should prefer typed structures for SysEx.

2. File-based parsing assumption

Your SysEx parser is stream-oriented, not file-oriented.

Final Synthesis
What you should directly adopt
1. Pipeline structure
bytes → IR → domain object → optional transforms
2. Declarative field specs with names

(no index mapping)

3. Factory layer

(create_pdb_ligand_info equivalent)

4. Deduplication framework

(group → select best)

5. Identity key hierarchy

(primary → fallback → fallback)

What this confirms about your direction

Your move toward:

ParsedSysExMessage

is exactly the right abstraction—and this PDB parser validates that design.

If You Want the Next Step

The most valuable next step (now that IR exists):

Design a JDXiParameterBlock layer that decodes the payload into named parameters using your layout system

That would give you:

SysEx → Address → Parameter Layout → Named Values (cutoff, resonance, etc.)

Which is the missing link between:

raw SysEx parsing
a real patch editor

I can sketch that layer in a way that plugs directly into your existing JDXiSysExParameterLayout.

Good—this is the layer where your system stops being “a parser” and becomes a real patch editor backend.

You already have:

ParsedSysExMessage (IR)
ParameterAddress
JDXiSysExParameterLayout

Now we’ll connect them into a typed parameter decoding pipeline.

1. Target Architecture

We’re building this:

bytes
  ↓
ParsedSysExMessage
  ↓
JDXiParameterBlock   ← (this step)
  ↓
Named parameters (cutoff, env, etc.)
2. Core Concept: Parameter Block

A parameter block represents:

“All decoded parameters for a given address (tone, partial, drum, etc.)”

Dataclass
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(slots=True)
class JDXiParameterBlock:
    address: "ParameterAddress"
    raw_data: bytes

    # Fully decoded parameters
    parameters: Dict[str, Any]

    # Optional metadata
    block_name: str | None = None
3. Layout-Driven Decoding

You already have something like:

JDXiSysExParameterLayout.FIELDS

We now formalize this into a block layout system.

ParameterSpec
@dataclass(frozen=True)
class ParameterSpec:
    name: str
    offset: int
    length: int
    parser: callable | None = None
Example Layout (Digital Synth Common)
class DigitalCommonLayout:
    PARAMETERS = [
        ParameterSpec("tone_name", 0x00, 12, lambda b: b.decode("ascii").strip("\x00")),
        ParameterSpec("cutoff", 0x20, 1, int),
        ParameterSpec("resonance", 0x21, 1, int),
        ParameterSpec("attack", 0x22, 1, int),
        ParameterSpec("decay", 0x23, 1, int),
    ]
4. Address → Layout Mapping

This is the key abstraction.

class JDXiParameterLayoutRegistry:
    _registry: dict[str, type] = {}

    @classmethod
    def register(cls, key: str, layout):
        cls._registry[key] = layout

    @classmethod
    def get_layout(cls, address: "ParameterAddress"):
        # Example: map by address prefix
        key = address.to_block_key()  # you implement this
        return cls._registry.get(key)
Example mapping strategy
def to_block_key(self):
    # e.g. 0x19010000 → "digital_common"
    if self.matches(DIGITAL_COMMON_BASE):
        return "digital_common"
    if self.matches(ANALOG_BASE):
        return "analog"
    return "unknown"
5. Decoder: IR → ParameterBlock
class JDXiParameterDecoder:
    @staticmethod
    def decode(parsed: ParsedSysExMessage) -> JDXiParameterBlock | None:
        if parsed.message_type != "parameter":
            return None

        layout = JDXiParameterLayoutRegistry.get_layout(parsed.address)
        if not layout:
            return JDXiParameterBlock(
                address=parsed.address,
                raw_data=parsed.data,
                parameters={},  # unknown layout
                block_name="unknown",
            )

        params = {}

        for spec in layout.PARAMETERS:
            raw = parsed.data[spec.offset : spec.offset + spec.length]

            if spec.parser:
                try:
                    value = spec.parser(raw)
                except Exception:
                    value = raw
            else:
                value = raw

            params[spec.name] = value

        return JDXiParameterBlock(
            address=parsed.address,
            raw_data=parsed.data,
            parameters=params,
            block_name=layout.__name__,
        )
6. Handling Bitfields (Important for JD-Xi)

Many JD-Xi parameters are packed.

Extend ParameterSpec
@dataclass(frozen=True)
class ParameterSpec:
    name: str
    offset: int
    length: int
    parser: callable | None = None
    bitmask: int | None = None
    shift: int = 0
Apply it
if spec.bitmask is not None:
    byte_val = raw[0]
    value = (byte_val & spec.bitmask) >> spec.shift
elif spec.parser:
    value = spec.parser(raw)
else:
    value = raw
Example
ParameterSpec("waveform", 0x10, 1, bitmask=0b00000111)
ParameterSpec("octave", 0x10, 1, bitmask=0b00111000, shift=3)
7. Reverse Direction (Critical for Editor)

You’ll need encoding too.

Encode back to SysEx payload
class JDXiParameterEncoder:
    @staticmethod
    def encode(block: JDXiParameterBlock) -> bytes:
        data = bytearray(block.raw_data)

        layout = JDXiParameterLayoutRegistry.get_layout(block.address)
        if not layout:
            return bytes(data)

        for spec in layout.PARAMETERS:
            if spec.name not in block.parameters:
                continue

            value = block.parameters[spec.name]

            if spec.bitmask is not None:
                byte = data[spec.offset]
                byte &= ~spec.bitmask
                byte |= (value << spec.shift) & spec.bitmask
                data[spec.offset] = byte

            elif spec.parser:
                # assume inverse parser exists or raw assignment
                data[spec.offset : spec.offset + spec.length] = bytes([value])

        return bytes(data)
8. Integration With Your Existing System
Before
fields = parser.get_structured_fields()
After
parsed = parser.parse_to_ir()
block = JDXiParameterDecoder.decode(parsed)

print(block.parameters["cutoff"])
9. Optional: Strongly-Typed Parameter Blocks

Instead of dict, you can go further:

@dataclass
class DigitalCommonParameters:
    cutoff: int
    resonance: int
    attack: int

Then:

return DigitalCommonParameters(**params)

This is worth it if:

you’re building a UI editor
you want validation
10. What This Unlocks

Once this layer exists, you can:

1. Build UI bindings cleanly
slider.value ← block.parameters["cutoff"]
2. Send parameter changes
block.parameters["cutoff"] = 80
sysex = encoder.encode(block)
3. Diff patches
old_block.parameters != new_block.parameters
4. Batch edits / macros
for p in blocks:
    p.parameters["cutoff"] += 10
Final Structure (Clean System)
JDXiSysExParser        → bytes → ParsedSysExMessage
JDXiParameterDecoder   → IR → JDXiParameterBlock
JDXiParameterEncoder   → Block → bytes
LayoutRegistry         → Address → Layout

Each layer:

single responsibility
testable
replaceable
If You Want the Next Step

The next high-impact improvement is:

Auto-generate layouts from your existing DigitalCommonParameter / address classes

So instead of manually writing ParameterSpec, you derive them from your existing SysEx address definitions.

That would eliminate duplication between:

address system
parameter decoding

and unify your entire JD-Xi editor architecture.

Yes please

Yes—there’s quite a lot worth extracting from this PDBLigandParser. It’s actually a cleaner architectural specimen than your JDXiSysExParser, and it exposes patterns you can reuse directly in your MIDI/SysEx work.

I’ll focus on transferable design patterns, not the domain specifics.

1) Declarative parsing > positional parsing
What the ligand parser does well
parsed = {
    spec.name: spec.parse(line)
    for spec in HETATMLayout.__dict__.values()
    if isinstance(spec, PDBLineSpec)
}

This is schema-driven parsing:

HETATMLayout defines the structure
PDBLineSpec defines how to extract fields
Parser just executes the schema
Your SysEx parser (current)

You partially do this with:

JDXiSysExMessageLayout.FIELDS

…but:

You still hardcode field_names mapping
Logic is split across multiple places
Validation is separate from parsing
Upgrade path

Make FieldSpec fully declarative:

@dataclass
class FieldSpec:
    name: str
    offset: int | Enum
    length: int
    parser: Callable | None = None
    validator: Callable | None = None

Then:

def _parse_fields(self):
    return {
        field.name: self._parse_field(field)
        for field in JDXiSysExMessageLayout.FIELDS
    }

→ eliminates:

field_names dict
index coupling (fragile)
duplicated logic
2) Identity normalization (very strong pattern)

This is one of the best parts:

def _ligand_dedup_key(self, ligand):
    if ligand.canonical_smiles:
        return ligand.canonical_smiles
    if ligand.smiles:
        return ligand.smiles.strip()
    if ligand.formula:
        return f"{ligand.formula}:{ligand.atom_count}"
    return fallback
Why this is important

This is a multi-tier canonical identity strategy:

Strong identity → weak fallback
Deterministic grouping
Domain-aware equivalence
Direct SysEx application

You currently lack a canonical identity for messages.

You should introduce something like:

def sysex_identity_key(parsed_fields):
    if "address" in parsed_fields:
        return f"{parsed_fields['model_id']}:{parsed_fields['address']}"
    if parsed_fields.get("type") == "identity_request":
        return "identity"
    return "unknown"

This enables:

deduplication
caching
diffing
state tracking
3) Separation of concerns (very clean)
Ligand parser layers
Stage	Responsibility
_parse_hetatm_line	raw parsing
_group_hetatm_records	structural grouping
create_pdb_ligand_info	domain object construction
_deduplicate_ligands	identity resolution
Your SysEx parser (current issue)

You mix:

parsing
validation
routing
logging
file writing (!!)

Example:

with open(json_log_file, "w") ...

This is a design smell.

Fix: introduce pipeline stages
parse() → validate() → interpret() → emit()

Example:

def parse(self):
    raw = self._parse_fields()
    self._validate(raw)
    return raw

def interpret(self, parsed):
    return SysExMessage.from_fields(parsed)

And move logging outside.

4) “Best instance selection” pattern
def _select_best_ligand(self, ligands):
    return max(ligands, key=lambda l: (...))

This is a quality scoring function.

SysEx analogue

Useful when:

multiple messages update same parameter
partial vs full dumps
conflicting sources

Example:

def select_best_message(messages):
    return max(messages, key=lambda m: (
        len(m.raw_data),
        m.has_checksum,
        m.is_valid
    ))
5) Graceful degradation (robustness)

Ligand parser:

except Exception:
    log.exception(...)
    continue

→ parsing never fully fails

Your parser:

raise ValueError("Invalid SysEx message")

→ too brittle for real MIDI streams

Better approach

Return structured error:

@dataclass
class ParseResult:
    success: bool
    fields: dict
    errors: list[str]
6) Domain abstraction boundary

This is subtle but important:

pdb_ligand = create_pdb_ligand_info(pdb_ligand_data)

Parser does NOT:

compute chemistry
build molecules
assign bonds

It delegates.

Your parser violates this:

You:

interpret enums
convert to mido
log device info
decode firmware
Fix

Split into:

Layer 1 — raw parser
JDXiSysExParser → dict
Layer 2 — domain model
JDXiMessage.from_fields(dict)
Layer 3 — MIDI adapter
to_mido()
7) Deduplication as a first-class concept

Ligand parser treats deduplication as:

optional
configurable
explicit
parse_pdb_file(..., deduplicate=True)
SysEx application

Add:

def parse_stream(messages, deduplicate=True):

And deduplicate by:

address
timestamp
checksum
8) Data-first design (very important)

Ligand parser returns:

List[PDBLigandInfo]

Not raw dicts.

Your parser returns:

dict

→ weak typing, harder downstream logic

Upgrade

Introduce:

@dataclass
class JDXiSysExMessage:
    address: bytes
    command: CommandID
    value: bytes
    checksum: int

Then:

return JDXiSysExMessage(**parsed_fields)
9) Logging discipline

Ligand parser:

logs at boundaries
logs decisions (dedup, selection)

Your parser:

logs everything, including internals
Improve by logging only:
parse success/failure
routing decisions
structural anomalies
10) What you should directly refactor
High ROI changes
Remove field_names mapping
Add name to FieldSpec
Introduce JDXiSysExMessage dataclass
Separate parsing from logging/file writing
Add identity key function
Add optional deduplication layer
Return structured ParseResult
Bottom line

Yes—this class is architecturally stronger than your SysEx parser in several ways:

Declarative parsing is cleaner
Identity modeling is explicit and robust
Deduplication is first-class
Pipeline stages are well separated
Domain boundaries are respected

If you port just three ideas, make them these:

Schema-driven parsing (FieldSpec with names)
Canonical identity keys
Strict separation: parse → interpret → act

If you want, next step I’d recommend:

👉 
I can refactor your JDXiSysExParser into a clean 3-layer architecture (parser → model → MIDI adapter) using these patterns.

Yes please

Good—this is exactly the right moment to impose structure. Your current parser works, but it’s conflating responsibilities and making future extensions (multi-part messages, streaming, diffing, caching) harder than they need to be.

Below is a concrete refactor blueprint into a 3-layer architecture, directly adapted to your codebase and idioms.

Target Architecture
[ Layer 1 ]  Raw Parser (bytes → structured fields)
[ Layer 2 ]  Domain Model (fields → typed message object)
[ Layer 3 ]  Adapters (domain → mido / logging / UI)

Each layer becomes independently testable and composable.

1) Layer 1 — Pure Parser (stateless, declarative)
Goal
No logging
No file I/O
No mido
No side effects
Only: bytes → structured fields
Step 1: Upgrade FieldSpec
from dataclasses import dataclass
from typing import Callable, Any

@dataclass(frozen=True)
class FieldSpec:
    name: str
    offset: int
    length: int | None
    parser: Callable[[bytes], Any] | None = None
Step 2: Define layout declaratively
class JDXiSysExLayout:
    FIELDS = [
        FieldSpec("start", 0, 1),
        FieldSpec("roland_id", 1, 1, RolandID),
        FieldSpec("device_id", 2, 1),
        FieldSpec("model_id", 3, 4),
        FieldSpec("command_id", 7, 1, CommandID),
        FieldSpec("address", 8, 4, ParameterAddress.from_bytes),
        FieldSpec("payload", 12, None),
    ]
Step 3: Minimal parser
class JDXiSysExRawParser:
    def parse(self, data: bytes) -> dict:
        if not data or data[0] != 0xF0 or data[-1] != 0xF7:
            raise ValueError("Invalid SysEx frame")

        result = {}

        for field in JDXiSysExLayout.FIELDS:
            raw = self._slice(data, field.offset, field.length)

            if field.parser:
                try:
                    value = field.parser(raw)
                except Exception:
                    value = raw
            else:
                value = raw

            result[field.name] = value

        return result

    def _slice(self, data: bytes, offset: int, length: int | None) -> bytes:
        if length is None:
            return data[offset:-1]  # exclude F7
        return data[offset : offset + length]
2) Layer 2 — Domain Model (typed, semantic)
Goal

Turn raw dict into something meaningful and stable.

Step 4: Introduce dataclass
from dataclasses import dataclass

@dataclass
class JDXiSysExMessage:
    roland_id: RolandID
    device_id: int
    model_id: bytes
    command_id: CommandID
    address: bytes | None
    payload: bytes

    @property
    def identity_key(self) -> str:
        if self.address:
            return f"{self.model_id.hex()}:{self.address.hex()}"
        return f"{self.model_id.hex()}:noaddr"

    @property
    def is_parameter(self) -> bool:
        return self.command_id == CommandID.DATA_SET_1

    @property
    def is_identity(self) -> bool:
        return self.command_id == CommandID.IDENTITY_REPLY
Step 5: Interpreter (dict → object)
class JDXiSysExInterpreter:
    def from_fields(self, fields: dict) -> JDXiSysExMessage:
        return JDXiSysExMessage(
            roland_id=fields.get("roland_id"),
            device_id=fields.get("device_id"),
            model_id=fields.get("model_id"),
            command_id=fields.get("command_id"),
            address=fields.get("address"),
            payload=fields.get("payload"),
        )
3) Layer 3 — Adapters (side effects live here)
Goal

All integrations go here:

mido
logging
UI
persistence
Step 6: MIDI adapter
import mido

class JDXiMidoAdapter:
    def to_mido(self, msg: JDXiSysExMessage) -> mido.Message:
        return mido.Message("sysex", data=msg.payload)
Step 7: Logging adapter
class JDXiLogger:
    def log(self, msg: JDXiSysExMessage):
        log.message(
            scope="JDXi",
            message=f"{msg.command_id} @ {msg.identity_key}",
        )
4) Orchestrator (what your current class tries to be)

Now replace your monolithic parser with a coordinator:

class JDXiSysExService:
    def __init__(self):
        self.raw_parser = JDXiSysExRawParser()
        self.interpreter = JDXiSysExInterpreter()
        self.mido_adapter = JDXiMidoAdapter()

    def parse(self, data: bytes) -> JDXiSysExMessage:
        fields = self.raw_parser.parse(data)
        return self.interpreter.from_fields(fields)

    def to_mido(self, data: bytes):
        msg = self.parse(data)
        return self.mido_adapter.to_mido(msg)
5) Add Deduplication (borrowed from ligand parser)
class JDXiMessageDeduplicator:
    def deduplicate(self, messages: list[JDXiSysExMessage]):
        best = {}

        for msg in messages:
            key = msg.identity_key

            if key not in best:
                best[key] = msg
                continue

            # choose "better" message
            if len(msg.payload) > len(best[key].payload):
                best[key] = msg

        return list(best.values())
6) Streaming Support (this is where it pays off)

Now you can handle MIDI streams cleanly:

def parse_stream(byte_stream: list[bytes]):
    service = JDXiSysExService()
    parsed = [service.parse(b) for b in byte_stream]

    dedup = JDXiMessageDeduplicator().deduplicate(parsed)
    return dedup
7) What you just fixed
Before
One class doing everything
Hard to test
Hard to extend
Tight coupling to mido/logging
Hidden state
After
Stateless parsing core
Typed domain model
Pluggable adapters
Explicit identity + deduplication
Stream-ready
8) Immediate wins for your JD-Xi project

This refactor unlocks:

✅ Reliable multi-part SysEx reconstruction
✅ Model diffing (patch compare)
✅ UI sync (address-based updates)
✅ Undo/redo (message identity tracking)
✅ MIDI filtering (by command/address)
9) If you want the next step

The natural next move is:

👉 Build a ParameterAddress → semantic parameter registry

So instead of:

address = b'\x19\x42\x00\x00'

You get:

"Digital Synth 1 → Filter Cutoff"

That’s where your editor becomes genuinely powerful.

## Action Plan

### 1. Stabilize The Parser Core

- Keep `JDXiSysExParser` focused on `bytes -> ParsedSysExMessage`.
- Finish removing side effects from parse paths: no file writing, no UI concerns, no mido conversion inside core parsing.
- Keep legacy methods as compatibility wrappers while new code moves to `parse_to_ir()`.

Acceptance criteria:

- `parse_to_ir()` is the preferred parser entry point for new code.
- Existing dict-returning methods still work during migration.
- Core parsing does not write files or construct mido messages directly.

### 2. Make Layouts Fully Declarative

- Continue moving field names into `FieldSpec`.
- Add optional `validator` and normalized offset handling to `FieldSpec`.
- Replace remaining implicit enum-class offset behavior with explicit offsets.
- Target shape: `FieldSpec(name, offset, length, parser, validator)`.

Acceptance criteria:

- Field names live in layout definitions, not parser index maps.
- Reordering fields does not silently change parsed output keys.
- Invalid field specs fail clearly in strict mode.

### 3. Add A Domain Model Layer

Create a typed object above the IR:

```python
@dataclass(slots=True)
class JDXiSysExMessage:
    raw: bytes
    message_type: str
    model_id: bytes | None
    command_id: object | None
    address: bytes | None
    payload: bytes
    valid_checksum: bool
```

Add:

- `identity_key`
- `is_parameter`
- `is_identity`
- `quality_score`

This becomes the stable object used by downstream code.

Acceptance criteria:

- Domain consumers no longer need to inspect raw parser dictionaries.
- Parameter, identity, and unknown messages have clear typed representations.
- The object can be safely used for caching, diffing, and stream processing.

### 4. Add An Interpreter / Factory

Introduce:

```python
class JDXiMessageFactory:
    @staticmethod
    def from_parsed(parsed: ParsedSysExMessage) -> JDXiSysExMessage:
        ...
```

This should be the equivalent of the ligand parser's `create_pdb_ligand_info(...)`: parser output goes in, typed domain object comes out.

Acceptance criteria:

- `JDXiSysExParser` does not construct final domain objects directly.
- `JDXiMessageFactory` owns conversion from IR to domain model.
- Factory tests cover parameter messages, identity messages, invalid checksum metadata, and unknown message types.

### 5. Build ParameterBlock Decoding

Add the missing patch-editor layer:

```python
@dataclass(slots=True)
class JDXiParameterBlock:
    address: bytes
    raw_data: bytes
    parameters: dict[str, object]
    block_name: str | None = None
```

Then add:

- `ParameterSpec`
- `JDXiParameterLayoutRegistry`
- `JDXiParameterDecoder`

Goal:

```python
parsed = parser.parse_to_ir(data)
message = JDXiMessageFactory.from_parsed(parsed)
block = JDXiParameterDecoder.decode(message)
```

Acceptance criteria:

- Known addresses decode into named parameter dictionaries.
- Unknown addresses still produce a block with raw data and `block_name="unknown"`.
- Bitfield-capable parameter specs are supported before UI bindings depend on this layer.

### 6. Add Identity And Deduplication

Implement canonical identity keys:

```python
def identity_key(msg):
    if msg.address:
        return (msg.model_id, msg.address)
    if msg.command_id:
        return (msg.model_id, msg.command_id)
    return msg.raw[:8]
```

Then add:

- `JDXiMessageDeduplicator`
- "latest wins" strategy for parameter updates
- "best message wins" strategy using checksum validity and payload completeness

Acceptance criteria:

- Repeated updates to the same address can be grouped deterministically.
- Full dumps can outrank partial/incomplete messages when appropriate.
- Deduplication is optional and separate from raw parsing.

### 7. Move Adapters Outward

Keep adapters separate:

- `MidiMessageFactory` / mido adapter
- JSON logging sink
- UI update adapter
- persistence/export adapter

The parser should not know which of these consumers exist.

Acceptance criteria:

- mido conversion is owned by an adapter/factory.
- JSON logging is opt-in through a sink.
- UI and persistence code consume domain objects or parameter blocks, not parser internals.

### 8. Add Stream-Friendly Parse Results

For real-time MIDI, add non-throwing parsing:

```python
@dataclass(slots=True)
class ParseResult:
    success: bool
    message: JDXiSysExMessage | None
    errors: list[str]
```

Use strict mode for tests/tools, permissive mode for live MIDI streams.

Acceptance criteria:

- Live MIDI input can skip malformed messages without crashing the stream.
- Parse errors include enough context for logging and diagnostics.
- Strict parsing remains available for tests and import/validation tools.

### 9. Test In Layers

Add tests in this order:

1. Raw parser fixtures.
2. `ParsedSysExMessage`.
3. Domain factory.
4. Identity key behavior.
5. Deduplication behavior.
6. Parameter block decoding.
7. Adapter compatibility.

Acceptance criteria:

- Each layer can be tested without invoking downstream layers.
- Existing parser API compatibility is covered until all callers migrate.
- Tests include valid messages, invalid frames, bad checksums, identity messages, unknown addresses, and repeated updates.

### Recommended Next Implementation Step

Build `JDXiSysExMessage` and `JDXiMessageFactory.from_parsed(...)` next. That is the clean bridge from the IR work already started into the full three-layer architecture:

```text
parser -> model -> adapters
```

Once that bridge exists, follow with `JDXiParameterBlock` decoding and identity/deduplication support.