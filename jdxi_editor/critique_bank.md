I think introducing a `Bank` dataclass is a good idea. In fact, I would go a little further and make it a value object representing a MIDI bank selection, rather than simply a container for two integers.

Your current design has `bank_msb` and `bank_lsb` repeated in several places. A `Bank` class would encapsulate those values, their validation, and potentially their MIDI-specific behaviour.

## 1. Suggested Bank class

I'd start with:

```
from dataclasses import dataclass@dataclass(frozen=True)class Bank:    """MIDI bank selection (MSB and LSB)."""    msb: int = 0    lsb: int = 0    def __post_init__(self) -> None:        if not 0 <= self.msb <= 127:            raise ValueError("Bank MSB must be between 0 and 127")        if not 0 <= self.lsb <= 127:            raise ValueError("Bank LSB must be between 0 and 127")
```

A few design decisions:

- `frozen=True`: bank selections are value objects and should be immutable.
- Defaults of zero: MIDI bank selection commonly defaults to MSB 0, LSB 0.
- Validation: both MIDI CC 0 (Bank Select MSB) and CC 32 (Bank Select LSB) have 7-bit values.

## 2. Refactor ProgramChangeSelection

I'd replace the two bank fields with a single `Bank` attribute.

```
@dataclass(frozen=True)class ProgramChangeSelection:    """Wire values for a bank select + program change."""    channel: int    bank: Bank    program: int    name: str = ""    def __post_init__(self) -> None:        if not 0 <= self.channel <= 15:            raise ValueError("Channel must be between 0 and 15")        if not 0 <= self.program <= 127:            raise ValueError("Program must be between 0 and 127")
```

Usage:

```
selection = ProgramChangeSelection(    channel=0,    bank=Bank(msb=87, lsb=0),    program=12,    name="My Preset",)
```

This is considerably cleaner than passing around three separate MIDI values.

## 3. Refactor ProgramChangeDialog

I'd also change the dialog constructor to accept a `Bank` object.

```
class ProgramChangeDialog(QDialog):    """Choose the channel and JD-Xi preset for a program change."""    def __init__(        self,        *,        channel: int,        bank: Bank,        program: int,        parent: Optional[QWidget] = None,    ):        super().__init__(parent)        self._channel = channel        self._bank = bank        self._program = program
```

Notice that I've made the arguments keyword-only. This helps avoid accidentally swapping channel, bank and program values.

The dialog can then return a `ProgramChangeSelection` rather than requiring the caller to reconstruct one.

## 4. One additional consideration: MIDI terminology

There is a distinction worth preserving:

| Concept  | MIDI representation          |
| -------- | ---------------------------- |
| Bank MSB | CC 0                         |
| Bank LSB | CC 32                        |
| Program  | Program Change message       |
| Channel  | MIDI channel 0–15 internally |

I'd avoid calling the class `BankSelect`, because that describes the MIDI operation rather than the underlying bank value.

`Bank` is a good domain name.

## 5. Potential future extension

If you anticipate supporting multiple synthesizers, you might eventually want a bank catalog:

```
@dataclass(frozen=True)class Bank:    """MIDI bank selection."""    msb: int = 0    lsb: int = 0    name: str = ""
```

However, I would not add `name` yet unless bank names are genuinely part of your application domain. A bank number and a preset name are different concepts. Your existing `ProgramChangeSelection.name` is better suited to the preset name.

My recommendation: implement `Bank` as a small, immutable value object with just `msb` and `lsb`. Use it consistently in `ProgramChangeSelection`, the dialog, and eventually the MIDI output layer. This gives you a clean domain model without introducing unnecessary abstraction.

I would definitely introduce a `Preset` class as well. Looking at the dialog, I think this is an opportunity to make a more substantial improvement to the domain model.

At present, the dialog is doing several jobs:

1. Loading preset definitions from different sources.
2. Converting dictionary-based preset definitions into lists.
3. Translating preset data into MIDI bank/program values.
4. Managing the user's selection.
5. Presenting the selected preset and its MIDI information.

I'd separate the preset domain model from the Qt presentation layer. In particular, the dialog should ideally work with `Preset` objects rather than dictionaries.

## 1. Suggested Preset dataclass

I'd start with something like this:

```
@dataclass(frozen=True)class Preset:    """A synthesizer preset and its MIDI address."""    name: str    bank: Bank    program: int    category: str = ""    source: PresetSource | None = None    def __post_init__(self) -> None:        if not 0 <= self.program <= 127:            raise ValueError("Program must be between 0 and 127")    @property    def midi_address(self) -> tuple[int, int, int]:        """Return (bank MSB, bank LSB, program)."""        return self.bank.msb, self.bank.lsb, self.program
```

There are a few deliberate choices here:

- `bank: Bank` reuses your existing value object.
- `program` is the zero-based MIDI Program Change value.
- `category` supports your existing category filtering.
- `source` identifies the preset library or synthesizer source.
- `midi_address` provides a convenient representation for MIDI operations.

I'd keep the preset name separate from the bank name. A preset is an individual sound; a bank is its MIDI address grouping.

## 2. Refactor ProgramChangeSelection

There is an interesting design choice here. Since `Preset` already contains the bank and program, I'd avoid duplicating those fields in `ProgramChangeSelection`.

I'd favour:

```
@dataclass(frozen=True)class ProgramChangeSelection:    """A preset selected for transmission on a MIDI channel."""    channel: int    preset: Preset    def __post_init__(self) -> None:        if not 0 <= self.channel <= 15:            raise ValueError("Channel must be between 0 and 15")    @property    def bank(self) -> Bank:        return self.preset.bank    @property    def program(self) -> int:        return self.preset.program    @property    def name(self) -> str:        return self.preset.name
```

This gives you a clean hierarchy:

Bank

msb · lsb

Preset

name · bank · program · category · source

ProgramChangeSelection

channel · preset

The distinction is important:

- `Bank` describes the MIDI bank address.
- `Preset` describes an actual synthesizer sound.
- `ProgramChangeSelection` describes the user's choice of sound on a particular MIDI channel.

## 3. Changes to ProgramChangeDialog

This is where the benefits become apparent.

Currently:

```
self._presets: list[dict] = []
```

Becomes:

```
self._presets: list[Preset] = []
```

Your conversion method:

```
@staticmethoddef _preset_list(source: PresetSource) -> list[Preset]:    ...
```

And your `_wire()` method becomes unnecessary because the MIDI address is already represented by the `Preset`:

```
preset.midi_address
```

For example:

```
preset = Preset(    name="Warm Strings",    bank=Bank(msb=87, lsb=0),    program=12,    category="Strings",    source=PresetSource.JDXI,)print(preset.midi_address)# (87, 0, 12)
```

I'd also change the initial dialog state to:

```
self._channel = channelself._bank = bankself._program = programself._presets: list[Preset] = []
```

You can retain the initial bank/program values because the currently selected MIDI address might not exist in the preset catalogue.

## 4. Consider a PresetCatalog later

One further architectural improvement is to move preset loading out of the dialog entirely.

For example:

```
class PresetCatalog:    def __init__(self) -> None:        self._presets: dict[PresetSource, list[Preset]] = {}    def presets(self, source: PresetSource) -> list[Preset]:        ...    def categories(self, source: PresetSource) -> list[str]:        ...    def find(        self,        source: PresetSource,        bank: Bank,        program: int,    ) -> Preset | None:        ...
```

This would allow other parts of your application to access preset definitions without depending on `ProgramChangeDialog`.

It also gives you a natural place to handle:

- Loading different preset libraries.
- Deduplicating presets.
- Searching by name.
- Filtering by category.
- Resolving MIDI addresses to preset names.

I wouldn't necessarily implement this immediately, but I'd design `Preset` so that it can support it.

## 5. One important question: should Preset contain Bank?

I think yes, particularly for your JD-Xi application.

However, I'd distinguish between two possible models:

| Model                    | Meaning                             |
| ------------------------ | ----------------------------------- |
| `Preset`                 | A named sound with its MIDI address |
| `ProgramChangeSelection` | A preset selected on a MIDI channel |

This is preferable to having the dialog independently maintain a bank, program and preset name.

## My recommended architecture

I'd settle on these three immutable dataclasses:

```
@dataclass(frozen=True)class Bank:    msb: int = 0    lsb: int = 0@dataclass(frozen=True)class Preset:    name: str    bank: Bank    program: int    category: str = ""    source: PresetSource | None = None@dataclass(frozen=True)class ProgramChangeSelection:    channel: int    preset: Preset
```

With validation added as discussed above.

One final thought: I'd avoid allowing dictionaries to propagate beyond the preset-loading layer. Convert the existing `PRESET_SOURCES` data into `Preset` objects once, at the boundary. That will make the rest of the application substantially more type-safe, easier to maintain, and easier to test.

I would make `MidiWireInfo` a resolved MIDI transmission value object, composed from `ProgramChangeSelection` and a small amount of channel-specific metadata.

The important distinction is that `Preset`, `ProgramChangeSelection`, and `MidiWireInfo` represent three different stages:

1. `Preset` — what sound the user wants.
2. `ProgramChangeSelection` — which preset is selected on which MIDI channel.
3. `MidiWireInfo` — the actual MIDI values and metadata resolved for transmission.

I would retain `MidiWireInfo`, but change its composition slightly. In particular, I would avoid storing both `channel` and `channel_display` as independent fields, and I would avoid duplicating the bank's MSB/LSB as `cc0` and `cc32` unless there is a specific wire-protocol reason to do so.

## 1. Recommended composition

I'd use the following structure:

```
@dataclass(frozen=True)class MidiWireInfo:    """Resolved MIDI wire values for a program or tone selection."""    channel: int    bank: Bank    program: int    preset_pc: int | None = None    program_id: str | None = None    def __post_init__(self) -> None:        if not 0 <= self.channel <= 15:            raise ValueError("Channel must be between 0 and 15")        if not 0 <= self.program <= 127:            raise ValueError("Program must be between 0 and 127")    @property    def cc0(self) -> int:        return self.bank.msb    @property    def cc32(self) -> int:        return self.bank.lsb    @property    def midi_pc(self) -> int:        return self.program    @property    def channel_display(self) -> str:        return channel_display_name(self.channel)
```

This has several advantages:

- `Bank` is reused rather than decomposed.
- The canonical program value is `program`.
- `midi_pc` is retained as a convenient compatibility property.
- Channel display formatting is derived rather than stored.
- You cannot accidentally construct an object where `bank.msb` disagrees with `cc0`.

I would keep `preset_pc` and `program_id` optional because they describe the source preset's identity rather than the MIDI wire message itself.

## 2. Keep preset metadata out of the wire object

There is one aspect of your current design I'd change quite firmly.

These fields:

```
channel_display: strpreset_pc: Optional[int]program_id: Optional[str]
```

are not all wire-format MIDI values.

For example:

- `channel_display="Ch 3 (Analog)"` is presentation metadata.
- `preset_pc=13` is a preset catalogue convention.
- `program_id="A01"` is a synthesizer-specific identifier.

None of these is transmitted in the MIDI Program Change message.

I'd therefore keep the wire object focused on the actual transmission address:

```
@dataclass(frozen=True)class MidiWireInfo:    """Resolved MIDI address for a program selection."""    channel: int    bank: Bank    program: int
```

You can add convenience properties if other code needs the traditional MIDI terminology:

```
    @property    def cc0(self) -> int:        return self.bank.msb    @property    def cc32(self) -> int:        return self.bank.lsb    @property    def midi_pc(self) -> int:        return self.program
```

This is a much cleaner separation of concerns.

## 3. Where should preset_pc and program_id go?

I'd put these in `Preset`, provided they describe the preset catalogue rather than the MIDI transmission.

For example:

```
@dataclass(frozen=True)class Preset:    """A named synthesizer preset."""    id: str    name: str    bank: Bank    program: int    category: str = ""    source: PresetSource | None = None
```

Here, `id` could be `"A01"` or another identifier supplied by the preset library.

One subtle issue in your existing code is:

```
preset_pc = (    int(preset.id)    if preset.id.isdigit()    else selection.program + 1)
```

I'd avoid this fallback.

A catalogue ID and a MIDI program number are not necessarily interchangeable. In particular, `"A01"` is a perfectly valid preset ID but doesn't tell you the MIDI program number without consulting the preset definition.

If you genuinely need a separate 1-based preset slot, make that explicit:

```
preset_number: int | None = None
```

Then you have three unambiguous concepts:

| Attribute       | Meaning                          |
| --------------- | -------------------------------- |
| `id`            | Catalogue identifier, e.g. `A01` |
| `preset_number` | 1-based preset slot              |
| `program`       | 0-based MIDI Program Change      |

That distinction is particularly useful when supporting synthesizers with different preset numbering conventions.

## 4. Simplify ValidationResult

I'd also reconsider this:

```
@dataclass(frozen=True)class ValidationResult:    ok: bool    expected: MidiWireInfo    actual: MidiWireInfo    diff_fields: List[str]
```

There is a potential consistency problem: `ok` could be `True` while `diff_fields` is non-empty.

I'd make `ok` a derived property and use a tuple for the immutable collection of differences.

```
@dataclass(frozen=True)class ValidationResult:    """Outcome of comparing expected and actual MIDI wire values."""    expected: MidiWireInfo    actual: MidiWireInfo    diff_fields: tuple[str, ...]    @property    def ok(self) -> bool:        return not self.diff_fields
```

I'd then provide a comparison factory:

```
    @classmethod    def compare(        cls,        expected: MidiWireInfo,        actual: MidiWireInfo,    ) -> ValidationResult:        fields = ("channel", "bank", "program")        differences = tuple(            field            for field in fields            if getattr(expected, field) != getattr(actual, field)        )        return cls(            expected=expected,            actual=actual,            diff_fields=differences,        )
```

Usage:

```
result = ValidationResult.compare(expected, actual)if not result.ok:    print("MIDI mismatch:", result.diff_fields)
```

This makes the validation result internally consistent.

## 5. Construct MidiWireInfo from ProgramChangeSelection

Rather than manually reconstructing the MIDI information in `_update_info()`, I'd give `MidiWireInfo` a factory method.

```
@dataclass(frozen=True)class MidiWireInfo:    """Resolved MIDI address for a program selection."""    channel: int    bank: Bank    program: int    @classmethod    def from_selection(        cls,        selection: ProgramChangeSelection,    ) -> MidiWireInfo:        return cls(            channel=selection.channel,            bank=selection.preset.bank,            program=selection.preset.program,        )
```

Your dialog then becomes considerably simpler:

```
def _update_info(self, *_args) -> None:    selection = self.selection()    self.ok_button.setEnabled(selection is not None)    if selection is None:        self.info_bar.set_message("MIDI  —")        return    self.info_bar.set_info(        MidiWireInfo.from_selection(selection)    )
```

Notice that the dialog no longer needs to know how MIDI wire information is constructed.

## 6. Keep MidiSelectionInfoBar presentation-oriented

Your existing widget is already reasonably well designed.

I'd retain it, with formatting delegated to a standalone function:

```
def format_midi_wire_info(    info: MidiWireInfo | None,) -> str:    if info is None:        return "MIDI  —"    channel = channel_display_name(info.channel)    return (        f"MIDI  {channel} · "        f"CC#0 {info.bank.msb} · "        f"CC#32 {info.bank.lsb} · "        f"PC {info.program}"    )
```

This keeps formatting out of both the domain objects and the Qt widget.

One important point: `channel_display_name()` can incorporate JD-Xi-specific channel assignments such as Digital Synth or Analog. That is application/device metadata, not a property of a generic MIDI channel.

## 7. My recommended overall architecture

I'd settle on the following relationships:

Domain objects

Bank

msb, lsb

Preset

id, name, bank, program, category, source

ProgramChangeSelection

channel, preset

Resolution

MIDI transmission layer

MidiWireInfo

channel, bank, program

Validation

ValidationResult

expected, actual, diff_fields, ok

Presentation layer

- `ProgramChangeDialog`
- `MidiSelectionInfoBar`
- `format_midi_wire_info()`

### Final recommendation

| Class/function            | Responsibility                                |
| ------------------------- | --------------------------------------------- |
| `Bank`                    | MIDI bank address (MSB/LSB)                   |
| `Preset`                  | Synthesizer preset definition                 |
| `ProgramChangeSelection`  | User's channel/preset choice                  |
| `MidiWireInfo`            | Resolved MIDI transmission values             |
| `ValidationResult`        | Comparison of expected and actual MIDI values |
| `MidiSelectionInfoBar`    | Qt presentation                               |
| `format_midi_wire_info()` | Human-readable MIDI formatting                |

One additional architectural consideration: I would keep `MidiWireInfo` independent of JD-Xi. It should be usable for any MIDI device. The preset catalogue, channel naming and preset ID conventions belong in the device-specific layer.

That will make this design much easier to extend if you eventually support other synthesizers alongside the JD-Xi.