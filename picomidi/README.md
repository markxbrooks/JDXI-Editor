# PicoMidi

A lightweight, focused MIDI library for Python.

PicoMidi provides core MIDI protocol functionality with a clean, type-safe API.

## Features

- **Type-safe MIDI values**: `Note`, `Velocity`, `ControlValue`, `ProgramNumber`, `PitchBendValue`
- **Message classes**: `NoteOn`, `NoteOff`, `ControlChange`, `ProgramChange`, `PitchBend`
- **Parser**: Convert raw MIDI bytes to message objects
- **Utilities**: Value conversions, validation, formatting, timing calculations
- **Core constants**: Status bytes, channels, bitmasks

## Installation

```bash
pip install picomidi
```

## Quick Start

### Creating Messages

```python
from picomidi import NoteOn, NoteOff, ControlChange, ProgramChange, PitchBend
from picomidi.core import Channel, Note, Velocity, ControlValue, ProgramNumber, PitchBendValue

# Create a Note On message (Middle C, full velocity, channel 1)
note_on = NoteOn(
    channel=Channel.CH1,
    note=Note(60),  # Middle C
    velocity=Velocity(127)
)

# Convert to bytes
bytes_data = note_on.to_bytes()  # b'\x90<\x7f'

# Convert to hex string
hex_str = note_on.to_hex_string()  # "90 3C 7F"
```

### Using Note Names

```python
from picomidi.core import Note

# Create note from name
note = Note.from_name("C4")  # Middle C
note = Note.from_name("A#3")  # A sharp, octave 3
note = Note.from_name("Bb5")  # B flat, octave 5

# Convert to name
name = note.to_name()  # "C4"
name = note.to_name(use_sharps=False)  # "Db4" instead of "C#4"
```

### Parsing Messages

```python
from picomidi.parser import Parser

parser = Parser()

# Feed raw MIDI bytes
raw_bytes = b'\x90<\x7f'  # Note On message
for message in parser.feed(raw_bytes):
    print(message)  # NoteOn(channel=1, note=Note(C4), velocity=127)
    print(message.to_hex_string())  # "90 3C 7F"
```

### Value Conversions

```python
from picomidi.utils.conversion import (
    combine_7bit_msb_lsb,
    split_14bit_to_7bit,
    clamp_midi_value
)

# Combine two 7-bit values into 14-bit
msb, lsb = 0x40, 0x20
value_14bit = combine_7bit_msb_lsb(msb, lsb)  # 8256

# Split 14-bit value
msb, lsb = split_14bit_to_7bit(value_14bit)  # (64, 32)

# Clamp values
clamped = clamp_midi_value(200)  # 127 (max MIDI value)
```

### Timing Calculations

```python
from picomidi.utils.timing import (
    bpm_to_microseconds_per_quarter,
    ticks_to_milliseconds
)

# Convert BPM to microseconds per quarter note (for MIDI files)
usec = bpm_to_microseconds_per_quarter(120)  # 500000

# Convert ticks to milliseconds
ms = ticks_to_milliseconds(
    ticks=480,
    ticks_per_beat=480,
    bpm=120
)  # 1000.0 (1 second)
```

## Structure

```
picomidi/
├── core/           # Core protocol definitions
│   ├── bitmask.py  # Bit masks
│   ├── constant.py # MIDI constants
│   ├── status.py   # Status bytes
│   ├── channel.py  # Channel handling
│   └── types.py    # Type-safe value classes
├── message/        # Message classes
│   ├── base.py     # Base message class
│   └── channel_voice/  # Channel voice messages
├── parser/         # Message parsing
│   └── parser.py   # Parser implementation
└── utils/          # Utilities
    ├── conversion.py  # Value conversions
    ├── validation.py  # Value validation
    ├── formatting.py  # Message formatting
    └── timing.py      # Timing calculations
```

## Design Principles

1. **Lightweight**: Minimal dependencies, focused on core MIDI protocol
2. **Type-safe**: Use dataclasses and type hints throughout
3. **Composable**: Messages can be easily combined and extended
4. **Well-tested**: Each module should have comprehensive tests
5. **Documented**: Clear docstrings and examples

## License

[MIT License]

