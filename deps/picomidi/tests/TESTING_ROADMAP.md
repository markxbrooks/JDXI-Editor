# PicoMidi Testing Roadmap

This document outlines what could be unit tested in PicoMidi, organized by priority and module.

## Currently Tested ✅

- **RolandSysExMessage** (`picomidi/tests/test_roland_sysex_message.py`)
  - Message creation and validation
  - Conversion to bytes/list
  - Parsing from bytes
  - Checksum calculation
  - Edge cases and error handling

---

## High Priority Tests (Core Functionality)

### 1. Utility Functions (`picomidi/utils/`)

#### `utils/conversion.py` - **CRITICAL**
These functions are used throughout the codebase and need comprehensive testing:

- ✅ `combine_7bit_msb_lsb(msb, lsb)` - Combine two 7-bit values into 14-bit
- ✅ `split_14bit_to_7bit(value)` - Split 14-bit value into two 7-bit values
- ✅ `clamp_midi_value(value)` - Clamp to 0-127 range
- ✅ `clamp_14bit_value(value)` - Clamp to 0-16383 range
- ✅ `signed_to_unsigned_14bit(value)` - Convert signed to unsigned 14-bit
- ✅ `unsigned_to_signed_14bit(value)` - Convert unsigned to signed 14-bit
- ✅ `midi_value_to_ms(midi_value, min_time, max_time)` - Convert MIDI to milliseconds
- ✅ `ms_to_midi_value(ms_time, min_time, max_time)` - Convert milliseconds to MIDI
- ✅ `fraction_to_midi_value(fractional_value, min, max)` - Convert fraction to MIDI
- ✅ `midi_value_to_fraction(midi_value, min, max)` - Convert MIDI to fraction
- ✅ `split_16bit_value_to_bytes(value)` - Split 16-bit into two bytes
- ✅ `split_8bit_value_to_nibbles(value)` - Split 8-bit into two nibbles
- ✅ `split_16bit_value_to_nibbles(value)` - Split 16-bit into 4 nibbles
- ✅ `split_32bit_value_to_nibbles(value)` - Split 32-bit into 8 nibbles
- ✅ `join_nibbles_to_16bit(nibbles)` - Join 4 nibbles to 16-bit
- ✅ `join_nibbles_to_32bit(nibbles)` - Join 8 nibbles to 32-bit
- ✅ `encode_14bit_to_7bit_midi_bytes(value)` - Encode 14-bit to 7-bit MIDI bytes

**Test Coverage Needed:**
- Normal operation with valid inputs
- Edge cases (min/max values, boundaries)
- Error handling (invalid ranges, wrong types)
- Round-trip conversions (split/join, convert/convert back)

#### `utils/formatting.py` - **HIGH**
- ✅ `format_message(message, include_bytes)` - Format MIDI message
- ✅ `format_bytes(data, separator, prefix)` - Format raw bytes as hex
- ✅ `format_message_list(messages, separator)` - Format list of messages
- ✅ `format_message_to_hex_string(message)` - Convert message list to hex string
- ✅ `get_message_type_name(status)` - Get human-readable message type name
- ✅ `int_to_hex(value)` - Convert int to hex string

**Test Coverage Needed:**
- Various message types
- Edge cases (empty lists, single bytes)
- Formatting options (separators, prefixes)

#### `utils/validation.py` - **HIGH**
- ✅ `validate_note(note)` - Validate MIDI note (0-127)
- ✅ `validate_velocity(velocity)` - Validate velocity (0-127)
- ✅ `validate_control_value(value)` - Validate CC value (0-127)
- ✅ `validate_program_number(program)` - Validate program (0-127)
- ✅ `validate_channel(channel)` - Validate channel 0-based (0-15)
- ✅ `validate_channel_display(channel)` - Validate channel 1-based (1-16)
- ✅ `validate_status_byte(status)` - Validate status byte
- ✅ `validate_14bit_value(value)` - Validate 14-bit value (0-16383)

**Test Coverage Needed:**
- Valid ranges
- Boundary conditions (min, max, min-1, max+1)
- Invalid inputs (negative, too large, wrong types)

#### `utils/timing.py` - **HIGH**
- ✅ `bpm_to_microseconds_per_quarter(bpm)` - Convert BPM to microseconds
- ✅ `microseconds_per_quarter_to_bpm(usec_per_quarter)` - Convert microseconds to BPM
- ✅ `ticks_to_milliseconds(ticks, ticks_per_beat, bpm)` - Convert ticks to ms
- ✅ `milliseconds_to_ticks(ms, ticks_per_beat, bpm)` - Convert ms to ticks
- ✅ `ticks_to_seconds(ticks, ticks_per_beat, bpm)` - Convert ticks to seconds
- ✅ `seconds_to_ticks(seconds, ticks_per_beat, bpm)` - Convert seconds to ticks
- ✅ `ticks_to_seconds_with_tempo(ticks, tempo, ticks_per_beat)` - Convert with tempo
- ✅ `seconds_to_ticks_with_tempo(seconds, tempo, ticks_per_beat)` - Convert with tempo

**Test Coverage Needed:**
- Round-trip conversions
- Edge cases (zero values, very large values)
- Error handling (negative values, zero BPM)
- Precision (floating point accuracy)

#### `sysex/conversion.py` - **MEDIUM**
- ✅ `calculate_checksum(data)` - Calculate Roland checksum
- ✅ `bytes_to_hex(byte_list, prefix)` - Convert bytes to hex string
- ✅ `int_to_hex(value)` - Convert int to hex

**Test Coverage Needed:**
- Checksum calculation with various data lengths
- Edge cases (empty data, single byte, large data)
- Hex formatting with different prefixes/separators

---

### 2. Core Types (`picomidi/core/types.py`) - **HIGH**

#### `Note` class
- ✅ `__init__(value)` - Create note with validation
- ✅ `from_name(name)` - Parse note name ("C4", "A#3", "Bb5")
- ✅ `to_name(use_sharps)` - Convert to note name
- ✅ Validation (0-127 range)

**Test Coverage Needed:**
- Valid note names (all octaves, sharps/flats)
- Invalid note names (malformed, out of range)
- Edge cases (C-1, G9, boundary values)
- Sharps vs flats conversion

#### `Velocity`, `ControlValue`, `ProgramNumber`, `PitchBendValue` classes
- ✅ Value validation (0-127 or appropriate range)
- ✅ Edge cases and boundaries

---

### 3. Message Classes (`picomidi/message/channel_voice/`) - **HIGH**

#### `NoteOn`, `NoteOff`
- ✅ Message creation
- ✅ `to_list()` conversion
- ✅ `to_bytes()` conversion
- ✅ `to_hex_string()` formatting
- ✅ `__repr__()` representation

#### `ControlChange`
- ✅ Message creation
- ✅ Conversion methods
- ✅ Various control numbers

#### `ProgramChange`
- ✅ Message creation
- ✅ Conversion methods

#### `PitchBend`
- ✅ Message creation
- ✅ 14-bit value handling
- ✅ Conversion methods

#### `NRPN`, `RPN`
- ✅ Message creation
- ✅ Parameter number encoding
- ✅ Value encoding

**Test Coverage Needed:**
- All message types
- Edge cases (min/max values)
- Channel handling (0-15)
- Round-trip conversions (create → bytes → parse)

---

### 4. Parser (`picomidi/parser/parser.py`) - **HIGH**

#### `Parser` class
- ✅ `feed(data)` - Feed bytes and yield messages
- ✅ Running status handling
- ✅ Incomplete message buffering
- ✅ Various message types parsing

**Test Coverage Needed:**
- Complete messages
- Incomplete messages (buffering)
- Running status (omitted status bytes)
- Multiple messages in one feed
- Edge cases (empty data, single bytes)
- Error handling (invalid status bytes)

---

### 5. Status Utilities (`picomidi/core/status.py`) - **MEDIUM**

#### `Status` class static methods
- ✅ `is_channel_voice(status)` - Check if channel voice message
- ✅ `is_system_common(status)` - Check if system common message
- ✅ `is_system_realtime(status)` - Check if system realtime message
- ✅ `get_message_type(status)` - Extract message type
- ✅ `get_channel(status)` - Extract channel number
- ✅ `make_channel_voice(msg_type, channel)` - Create status byte

**Test Coverage Needed:**
- All status byte ranges
- Edge cases (boundaries)
- Invalid status bytes

---

## Medium Priority Tests

### 6. Channel Handling (`picomidi/core/channel.py`) - **MEDIUM**
- Channel enum values
- 0-based vs 1-based conversion
- Display formatting

### 7. BitMask (`picomidi/core/bitmask.py`) - **MEDIUM**
- Bit mask constants
- Bit manipulation utilities (if any)

### 8. Base Message (`picomidi/message/base.py`) - **MEDIUM**
- Abstract base class
- Common methods (`to_bytes()`, `to_hex_string()`)

---

## Lower Priority Tests

### 9. Legacy Message Classes (`picomidi/messages/`) - **LOW**
- `Aftertouch`, `ControlChangeStatus`, `MidiNote`, etc.
- These appear to be legacy/constant classes

### 10. RPN/NRPN Maps (`picomidi/rpn/`) - **LOW**
- Parameter mapping utilities

### 11. Constants (`picomidi/constant.py`) - **LOW**
- Constant values (mostly just data, not logic)

---

## Recommended Test Implementation Order

1. **Week 1**: `utils/conversion.py` (most critical, used everywhere)
2. **Week 2**: `utils/validation.py` + `utils/formatting.py`
3. **Week 3**: `utils/timing.py` + `core/types.py` (Note class)
4. **Week 4**: Message classes (`NoteOn`, `NoteOff`, `ControlChange`, etc.)
5. **Week 5**: `parser/parser.py` (complex, needs thorough testing)
6. **Week 6**: `core/status.py` + remaining utilities

---

## Test File Organization

Suggested structure:
```
picomidi/tests/
├── __init__.py
├── test_roland_sysex_message.py  ✅ (already exists)
├── test_utils_conversion.py      (NEW)
├── test_utils_formatting.py      (NEW)
├── test_utils_validation.py      (NEW)
├── test_utils_timing.py          (NEW)
├── test_sysex_conversion.py      (NEW)
├── test_core_types.py            (NEW - Note, Velocity, etc.)
├── test_message_note.py          (NEW - NoteOn, NoteOff)
├── test_message_control.py      (NEW - ControlChange, ProgramChange)
├── test_message_pitch.py         (NEW - PitchBend)
├── test_parser.py                (NEW)
└── test_status.py                (NEW)
```

---

## Test Coverage Goals

- **Critical utilities**: 95%+ coverage
- **Message classes**: 90%+ coverage
- **Parser**: 85%+ coverage
- **Core types**: 90%+ coverage
- **Overall**: 80%+ coverage

---

## Notes

- Focus on edge cases and error handling
- Test round-trip conversions where applicable
- Use parametrized tests for similar test cases
- Mock external dependencies if needed
- Test both valid and invalid inputs
- Verify error messages are helpful
