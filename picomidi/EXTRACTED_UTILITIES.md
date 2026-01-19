# Extracted Generic MIDI Utilities

This document lists the generic MIDI utilities that were extracted from JDXI Editor and added to PicoMidi, in priority order.

## Priority 1: Value Conversion Utilities ✅

**Location:** `picomidi/utils/conversion.py`

### Added Functions:

1. **`midi_value_to_ms(midi_value, min_time=10, max_time=1000)`**
   - Converts MIDI value (0-127) to milliseconds
   - Useful for mapping MIDI CC to time-based parameters (attack, release, delay)

2. **`ms_to_midi_value(ms_time, min_time=10, max_time=1000)`**
   - Converts milliseconds to MIDI value (0-127)
   - Inverse of `midi_value_to_ms()`

3. **`fraction_to_midi_value(fractional_value, minimum=0.0, maximum=1.0)`**
   - Converts fractional value (0.0-1.0) to MIDI CC value (0-127)
   - Useful for mapping normalized UI values to MIDI

4. **`midi_value_to_fraction(midi_value, minimum=0.0, maximum=1.0)`**
   - Converts MIDI value (0-127) to fractional value (0.0-1.0)
   - Useful for mapping MIDI CC to normalized ranges for UI display

## Priority 2: Byte Manipulation Utilities ✅

**Location:** `picomidi/utils/conversion.py`

### Added Functions:

1. **`split_16bit_value_to_bytes(value)`**
   - Splits 16-bit integer into [MSB, LSB] bytes

2. **`split_8bit_value_to_nibbles(value)`**
   - Splits 8-bit integer into [upper_nibble, lower_nibble]

3. **`split_16bit_value_to_nibbles(value)`**
   - Splits 16-bit integer into 4 nibbles

4. **`split_32bit_value_to_nibbles(value)`**
   - Splits 32-bit integer into 8 nibbles
   - Useful for Roland SysEx DT1 data encoding

5. **`join_nibbles_to_16bit(nibbles)`**
   - Combines 4 nibbles into 16-bit integer

6. **`join_nibbles_to_32bit(nibbles)`**
   - Combines 8 nibbles into 32-bit integer

7. **`encode_14bit_to_7bit_midi_bytes(value)`**
   - Encodes 14-bit value into two 7-bit MIDI-safe bytes
   - Returns [MSB, LSB] where each is 0-127

## Priority 3: SysEx Checksum Calculation ✅

**Location:** `picomidi/sysex/conversion.py`

### Added Functions:

1. **`calculate_checksum(data)`**
   - Calculates Roland-style checksum for SysEx parameter messages
   - Formula: `(128 - (sum of data bytes & 0x7F)) & 0x7F`
   - Ensures checksum is always a valid 7-bit MIDI value (0-127)

### Enhanced Functions:

1. **`bytes_to_hex(byte_list, prefix="F0")`**
   - Improved type hints and error handling
   - Removed dependency on `decologr`

## Priority 4: Formatting Utilities ✅

**Location:** `picomidi/utils/formatting.py`

### Added Functions:

1. **`format_message_to_hex_string(message)`**
   - Converts iterable of MIDI byte values to space-separated hex string
   - Example: `[240, 65, 16, 0]` → `"F0 41 10 00"`

2. **`int_to_hex(value)`**
   - Converts integer to uppercase hex string without '0x' prefix
   - Example: `255` → `"FF"`

## Usage Examples

### Value Conversions

```python
from picomidi.utils.conversion import (
    midi_value_to_ms,
    ms_to_midi_value,
    fraction_to_midi_value,
    midi_value_to_fraction
)

# Convert MIDI CC to milliseconds (attack time)
attack_ms = midi_value_to_ms(64, min_time=10, max_time=1000)  # 505.0 ms

# Convert milliseconds back to MIDI
midi_value = ms_to_midi_value(505.0, min_time=10, max_time=1000)  # 64

# Convert UI slider (0.0-1.0) to MIDI
midi_cc = fraction_to_midi_value(0.5)  # 64

# Convert MIDI to UI slider value
ui_value = midi_value_to_fraction(64)  # 0.503937...
```

### Byte Manipulation

```python
from picomidi.utils.conversion import (
    split_16bit_value_to_bytes,
    split_8bit_value_to_nibbles,
    join_nibbles_to_16bit,
    encode_14bit_to_7bit_midi_bytes
)

# Split 16-bit value
msb, lsb = split_16bit_value_to_bytes(0x1234)  # [0x12, 0x34]

# Split to nibbles
nibbles = split_8bit_value_to_nibbles(0xAB)  # [0xA, 0xB]

# Join nibbles back
value = join_nibbles_to_16bit([0x1, 0x2, 0x3, 0x4])  # 0x1234

# Encode 14-bit for SysEx
bytes = encode_14bit_to_7bit_midi_bytes(0x1234)  # [0x24, 0x34]
```

### SysEx Checksum

```python
from picomidi.sysex.conversion import calculate_checksum

# Calculate checksum for SysEx data
data = [0x41, 0x10, 0x00, 0x00, 0x00, 0x0E]
checksum = calculate_checksum(data)  # Valid 7-bit checksum
```

### Formatting

```python
from picomidi.utils.formatting import format_message_to_hex_string, int_to_hex

# Format message bytes
hex_str = format_message_to_hex_string([240, 65, 16, 0])  # "F0 41 10 00"

# Convert integer to hex
hex_value = int_to_hex(255)  # "FF"
```

## Accessing the Utilities

All utilities are accessible through the PicoMidi package:

```python
import picomidi

# Value conversions
picomidi.utils.conversion.midi_value_to_ms(64)

# Byte manipulation
picomidi.utils.conversion.split_16bit_value_to_bytes(0x1234)

# SysEx utilities
picomidi.sysex.conversion.calculate_checksum([0x41, 0x10])

# Formatting
picomidi.utils.formatting.format_message_to_hex_string([240, 65])
```

## Priority 5: MIDI File Timing Utilities ✅

**Location:** `picomidi/utils/timing.py`

### Added Functions:

1. **`ticks_to_seconds_with_tempo(ticks, tempo, ticks_per_beat)`**
   - Converts MIDI ticks to seconds using tempo in microseconds per quarter note
   - More precise than BPM-based calculations
   - Uses exact tempo values from MIDI file tempo meta events

2. **`seconds_to_ticks_with_tempo(seconds, tempo, ticks_per_beat)`**
   - Converts seconds to MIDI ticks using tempo in microseconds per quarter note
   - Inverse of `ticks_to_seconds_with_tempo()`

### Usage Example:

```python
from picomidi.utils.timing import ticks_to_seconds_with_tempo, seconds_to_ticks_with_tempo

# Convert ticks to seconds using tempo (500000 = 120 BPM)
duration = ticks_to_seconds_with_tempo(
    ticks=480,
    tempo=500000,  # microseconds per quarter note
    ticks_per_beat=480
)  # 1.0 seconds

# Convert seconds back to ticks
ticks = seconds_to_ticks_with_tempo(
    seconds=1.0,
    tempo=500000,
    ticks_per_beat=480
)  # 480 ticks
```

## Priority 6: Roland SysEx Encoding Utilities ✅

**Location:** `picomidi/sysex/roland.py`

### Added Functions:

1. **`encode_roland_7bit(value)`**
   - Encodes a 28-bit value into 4×7-bit MIDI bytes (MSB first)
   - Returns [MSB, ..., LSB] where each byte is 0-127

2. **`decode_roland_4byte(data_bytes)`**
   - Decodes 4 Roland 7-bit bytes into a 28-bit signed integer
   - Handles signed values by converting from unsigned representation

3. **`encode_roland_4byte(value)`**
   - Encodes a signed 28-bit integer into 4 Roland 7-bit bytes
   - Standard encoding used in Roland SysEx DT1 (Data Set) messages
   - Negative values are converted to unsigned representation

### Usage Example:

```python
from picomidi.sysex.roland import encode_roland_4byte, decode_roland_4byte

# Encode a value for Roland SysEx
encoded = encode_roland_4byte(1048577)  # [0x08, 0x00, 0x00, 0x01]

# Decode back
value = decode_roland_4byte([0x08, 0x00, 0x00, 0x01])  # 1048577

# Encode 28-bit value as 7-bit bytes
bytes_7bit = encode_roland_7bit(0x1234567)  # [0x09, 0x1A, 0x2B, 0x67]
```

## Priority 7: Library Bridge Utilities ❌ (Not Extracted)

**Status:** Not extracted - Too library-specific

The following utilities were evaluated but **not extracted** because they:
- Depend on specific MIDI libraries (`mido`, `rtmidi`)
- Would add external dependencies to PicoMidi
- Are better suited as separate compatibility layers

### Utilities Not Extracted:

1. **`rtmidi_to_mido(byte_message)`** - Converts rtmidi bytes to mido.Message
2. **`mido_message_data_to_byte_list(message)`** - Converts mido message to byte list
3. **`convert_to_mido_message(message_content)`** - Converts raw bytes to mido.Message

**Recommendation:** These should remain in JDXI Editor or be moved to a separate compatibility package (e.g., `picomidi-bridges` or `picomidi-compat`) if needed.

## Priority 5: MIDI File Timing Utilities ✅

**Location:** `picomidi/utils/timing.py`

### Added Functions:

1. **`ticks_to_seconds_with_tempo(ticks, tempo, ticks_per_beat)`**
   - Converts MIDI ticks to seconds using tempo in microseconds per quarter note
   - More precise than BPM-based calculations
   - Uses exact tempo values from MIDI file tempo meta events

2. **`seconds_to_ticks_with_tempo(seconds, tempo, ticks_per_beat)`**
   - Converts seconds to MIDI ticks using tempo in microseconds per quarter note
   - Inverse of `ticks_to_seconds_with_tempo()`

### Usage Example:

```python
from picomidi.utils.timing import ticks_to_seconds_with_tempo, seconds_to_ticks_with_tempo

# Convert ticks to seconds using tempo (500000 = 120 BPM)
duration = ticks_to_seconds_with_tempo(
    ticks=480,
    tempo=500000,  # microseconds per quarter note
    ticks_per_beat=480
)  # 1.0 seconds

# Convert seconds back to ticks
ticks = seconds_to_ticks_with_tempo(
    seconds=1.0,
    tempo=500000,
    ticks_per_beat=480
)  # 480 ticks
```

## Priority 6: Roland SysEx Encoding Utilities ✅

**Location:** `picomidi/sysex/roland.py`

### Added Functions:

1. **`encode_roland_7bit(value)`**
   - Encodes a 28-bit value into 4×7-bit MIDI bytes (MSB first)
   - Returns [MSB, ..., LSB] where each byte is 0-127

2. **`decode_roland_4byte(data_bytes)`**
   - Decodes 4 Roland 7-bit bytes into a 28-bit signed integer
   - Handles signed values by converting from unsigned representation

3. **`encode_roland_4byte(value)`**
   - Encodes a signed 28-bit integer into 4 Roland 7-bit bytes
   - Standard encoding used in Roland SysEx DT1 (Data Set) messages
   - Negative values are converted to unsigned representation

### Usage Example:

```python
from picomidi.sysex.roland import encode_roland_4byte, decode_roland_4byte

# Encode a value for Roland SysEx
encoded = encode_roland_4byte(1048577)  # [0x08, 0x00, 0x00, 0x01]

# Decode back
value = decode_roland_4byte([0x08, 0x00, 0x00, 0x01])  # 1048577

# Encode 28-bit value as 7-bit bytes
bytes_7bit = encode_roland_7bit(0x1234567)  # [0x09, 0x1A, 0x2B, 0x67]
```

## Priority 7: Library Bridge Utilities ❌ (Not Extracted)

**Status:** Not extracted - Too library-specific

The following utilities were evaluated but **not extracted** because they:
- Depend on specific MIDI libraries (`mido`, `rtmidi`)
- Would add external dependencies to PicoMidi
- Are better suited as separate compatibility layers

### Utilities Not Extracted:

1. **`rtmidi_to_mido(byte_message)`** - Converts rtmidi bytes to mido.Message
2. **`mido_message_data_to_byte_list(message)`** - Converts mido message to byte list
3. **`convert_to_mido_message(message_content)`** - Converts raw bytes to mido.Message

**Recommendation:** These should remain in JDXI Editor or be moved to a separate compatibility package (e.g., `picomidi-bridges` or `picomidi-compat`) if needed.

## Notes

- All functions include comprehensive type hints
- Functions validate input ranges and raise `ValueError` for invalid inputs
- No external dependencies added (removed `decologr` dependency)
- All functions are generic and not JD-Xi specific
- Functions follow PicoMidi's design principles: lightweight, type-safe, well-documented
- Roland utilities are in a separate module to keep core library generic
- Roland utilities are in a separate module to keep core library generic