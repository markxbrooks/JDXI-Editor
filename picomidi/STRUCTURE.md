F# PicoMidi Library Structure

A lightweight, focused MIDI library for Python.

## Directory Structure

```
picomidi/
├── __init__.py                 # Package initialization, exports main API
├── README.md                   # Library documentation
├── LICENSE                     # License file
│
├── core/                       # Core MIDI protocol definitions
│   ├── __init__.py
│   ├── bitmask.py             # ✅ Already exists
│   ├── constant.py            # ✅ Already exists (MIDI constants)
│   ├── status.py              # MIDI status bytes and message types
│   ├── channel.py             # MIDI channel handling (1-16, 0-based vs 1-based)
│   └── types.py               # MIDI data types (Note, Velocity, Control, etc.)
│
├── message/                    # MIDI message classes
│   ├── __init__.py
│   ├── base.py                # Base message class
│   ├── channel_voice.py       # Channel Voice Messages
│   │   ├── note_on.py
│   │   ├── note_off.py
│   │   ├── control_change.py
│   │   ├── program_change.py
│   │   ├── pitch_bend.py
│   │   └── aftertouch.py
│   ├── system_common.py       # System Common Messages
│   │   ├── song_position.py
│   │   ├── song_select.py
│   │   └── tune_request.py
│   ├── system_realtime.py     # System Realtime Messages
│   │   ├── clock.py
│   │   ├── start.py
│   │   ├── stop.py
│   │   └── continue.py
│   └── sysex.py               # System Exclusive messages
│
├── parser/                     # MIDI message parsing
│   ├── __init__.py
│   ├── parser.py              # Main parser class
│   ├── decoder.py             # Decode raw bytes to messages
│   └── encoder.py             # Encode messages to raw bytes
│
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── conversion.py          # Value conversions (7-bit, 14-bit, etc.)
│   ├── validation.py          # Validate MIDI values
│   ├── formatting.py          # Format messages for display/logging
│   └── timing.py              # Tempo, BPM, tick calculations
│
└── io/                         # I/O operations (optional, could be separate)
    ├── __init__.py
    ├── port.py                # Port discovery and management
    ├── reader.py              # Read MIDI messages
    └── writer.py              # Write MIDI messages
```

## Core Files

### `core/status.py`
```python
"""MIDI Status Bytes and Message Types"""

class Status:
    """MIDI status byte constants"""
    # Channel Voice Messages
    NOTE_OFF = 0x80
    NOTE_ON = 0x90
    POLY_AFTERTOUCH = 0xA0
    CONTROL_CHANGE = 0xB0
    PROGRAM_CHANGE = 0xC0
    CHANNEL_AFTERTOUCH = 0xD0
    PITCH_BEND = 0xE0
    
    # System Common Messages
    SYSTEM_EXCLUSIVE = 0xF0
    MIDI_TIME_CODE = 0xF1
    SONG_POSITION = 0xF2
    SONG_SELECT = 0xF3
    TUNE_REQUEST = 0xF6
    END_OF_EXCLUSIVE = 0xF7
    
    # System Realtime Messages
    TIMING_CLOCK = 0xF8
    START = 0xFA
    CONTINUE = 0xFB
    STOP = 0xFC
    ACTIVE_SENSING = 0xFE
    SYSTEM_RESET = 0xFF
    
    @staticmethod
    def is_channel_voice(status: int) -> bool:
        """Check if status byte is a channel voice message"""
        return 0x80 <= status <= 0xEF
    
    @staticmethod
    def is_system_realtime(status: int) -> bool:
        """Check if status byte is a system realtime message"""
        return 0xF8 <= status <= 0xFF
```

### `core/channel.py`
```python
"""MIDI Channel Handling"""

from enum import IntEnum

class Channel(IntEnum):
    """MIDI channels (0-based for internal use)"""
    CH1 = 0
    CH2 = 1
    CH3 = 2
    # ... CH16 = 15
    
    @classmethod
    def from_display(cls, channel: int) -> 'Channel':
        """Convert 1-based display channel to 0-based"""
        return cls(channel - 1)
    
    def to_display(self) -> int:
        """Convert to 1-based display channel"""
        return self.value + 1
```

### `core/types.py`
```python
"""MIDI Data Types"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class Note:
    """MIDI Note (0-127)"""
    value: int
    
    def __post_init__(self):
        if not 0 <= self.value <= 127:
            raise ValueError(f"Note value must be 0-127, got {self.value}")
    
    @classmethod
    def from_name(cls, name: str) -> 'Note':
        """Parse note name like 'C4', 'A#3'"""
        # Implementation here
        pass
    
    def to_name(self) -> str:
        """Convert to note name like 'C4'"""
        # Implementation here
        pass

@dataclass
class Velocity:
    """MIDI Velocity (0-127)"""
    value: int
    
    def __post_init__(self):
        if not 0 <= self.value <= 127:
            raise ValueError(f"Velocity must be 0-127, got {self.value}")

@dataclass
class ControlValue:
    """MIDI Control Change value (0-127)"""
    value: int
    
    def __post_init__(self):
        if not 0 <= self.value <= 127:
            raise ValueError(f"Control value must be 0-127, got {self.value}")
```

### `message/base.py`
```python
"""Base MIDI Message Class"""

from abc import ABC, abstractmethod
from typing import List

class Message(ABC):
    """Base class for all MIDI messages"""
    
    @abstractmethod
    def to_bytes(self) -> bytes:
        """Convert message to bytes"""
        pass
    
    @abstractmethod
    def to_list(self) -> List[int]:
        """Convert message to list of integers"""
        pass
    
    def to_hex_string(self) -> str:
        """Convert to hexadecimal string representation"""
        return " ".join(f"{b:02X}" for b in self.to_list())
```

### `message/channel_voice/note_on.py`
```python
"""Note On Message"""

from picomidi.message.base import Message
from picomidi.core.types import Note, Velocity
from picomidi.core.status import Status
from picomidi.core.channel import Channel

class NoteOn(Message):
    """MIDI Note On message"""
    
    def __init__(self, channel: Channel, note: Note, velocity: Velocity):
        self.channel = channel
        self.note = note
        self.velocity = velocity
    
    def to_list(self) -> List[int]:
        status = Status.NOTE_ON | self.channel.value
        return [status, self.note.value, self.velocity.value]
    
    def to_bytes(self) -> bytes:
        return bytes(self.to_list())
```

### `utils/conversion.py`
```python
"""MIDI Value Conversions"""

from picomidi.core.bitmask import BitMask

def combine_7bit_msb_lsb(msb: int, lsb: int) -> int:
    """Combine two 7-bit values into a 14-bit value"""
    return (msb << 7) | lsb

def split_14bit_to_7bit(value: int) -> tuple[int, int]:
    """Split a 14-bit value into two 7-bit values"""
    msb = (value >> 7) & BitMask.LOW_7_BITS
    lsb = value & BitMask.LOW_7_BITS
    return msb, lsb

def clamp_midi_value(value: int) -> int:
    """Clamp value to valid MIDI range (0-127)"""
    return max(0, min(127, value))
```

### `utils/timing.py`
```python
"""MIDI Timing Utilities"""

def bpm_to_microseconds_per_quarter(bpm: float) -> int:
    """Convert BPM to microseconds per quarter note"""
    return int(60_000_000 / bpm)

def microseconds_per_quarter_to_bpm(usec_per_quarter: int) -> float:
    """Convert microseconds per quarter note to BPM"""
    return 60_000_000 / usec_per_quarter

def ticks_to_milliseconds(ticks: int, ticks_per_beat: int, bpm: float) -> float:
    """Convert MIDI ticks to milliseconds"""
    beats = ticks / ticks_per_beat
    seconds = beats * (60 / bpm)
    return seconds * 1000
```

### `parser/parser.py`
```python
"""MIDI Message Parser"""

from typing import Iterator, Optional
from picomidi.message.base import Message

class Parser:
    """Parse raw MIDI bytes into message objects"""
    
    def __init__(self):
        self.buffer = bytearray()
    
    def feed(self, data: bytes) -> Iterator[Message]:
        """Feed raw bytes and yield complete messages"""
        self.buffer.extend(data)
        # Parse logic here
        yield from self._parse_buffer()
    
    def _parse_buffer(self) -> Iterator[Message]:
        """Parse buffer and yield messages"""
        # Implementation here
        pass
```

## Example Usage

```python
from picomidi import NoteOn, Channel, Note, Velocity
from picomidi.core.status import Status

# Create a Note On message
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

## Design Principles

1. **Lightweight**: Core library should have minimal dependencies
2. **Type-safe**: Use dataclasses and type hints throughout
3. **Composable**: Messages can be easily combined and extended
4. **Well-tested**: Each module should have comprehensive tests
5. **Documented**: Clear docstrings and examples

## Optional Extensions

- `file/` - MIDI file reading/writing (SMF format)
- `device/` - Device-specific implementations (Roland, etc.)
- `sysex/` - System Exclusive message handling
- `rpn/` - Registered Parameter Numbers
- `nrpn/` - Non-Registered Parameter Numbers

