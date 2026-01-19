# Unit Test Priorities for JD-Xi Editor

## Priority 1: Critical Core Functionality (Must Have)

### 1.1 SysEx Validation & Error Handling
**Files**: `jdxi_editor/midi/sysex/validation.py`
- ✅ Basic validation exists
- ❌ **Missing**: Edge cases and error conditions
  - Invalid message lengths (too short, too long, wrong lengths)
  - Invalid headers (wrong manufacturer ID, model ID)
  - Invalid checksums (various failure modes)
  - Invalid command bytes
  - Malformed messages (null bytes, out-of-range values)
  - Empty messages
  - Messages with missing start/end markers

**Priority**: **CRITICAL** - Prevents invalid data from corrupting synth state

### 1.2 SysEx Composer Error Handling
**Files**: `jdxi_editor/midi/sysex/composer.py`
- ✅ Basic composition exists (`test_sysex_composer_arpeggio_switch.py`)
- ❌ **Missing**: Error cases
  - Invalid parameter values (out of range)
  - Invalid addresses
  - Parameter validation failures
  - Value conversion errors (MIDI encoding failures)
  - Address offset application failures
  - LMB offset failures

**Priority**: **CRITICAL** - Ensures only valid SysEx messages are sent

### 1.3 Address Mapping & Parameter Resolution
**Files**: `jdxi_editor/midi/map/parameter_address.py`, `jdxi_editor/midi/data/address/helpers.py`
- ❌ **Missing**: Complete test coverage
  - Address to parameter mapping (all synth types)
  - Parameter to address resolution
  - Offset application (`apply_address_offset`)
  - Address arithmetic (add_offset)
  - Edge cases (unknown addresses, invalid offsets)
  - Multi-byte address handling

**Priority**: **CRITICAL** - Core functionality for parameter access

### 1.4 MIDI I/O Error Handling
**Files**: `jdxi_editor/midi/io/helper.py`, `jdxi_editor/midi/io/input_handler.py`, `jdxi_editor/midi/io/output_handler.py`
- ❌ **Missing**: Error scenarios
  - Port open/close failures
  - Message send failures
  - Callback errors
  - Thread safety (concurrent access)
  - Port disconnection handling
  - Invalid message handling

**Priority**: **CRITICAL** - Prevents crashes and data loss

---

## Priority 2: Core Business Logic (High Priority)

### 2.1 SysEx Parser Edge Cases
**Files**: `jdxi_editor/midi/sysex/parser/sysex.py`, `jdxi_editor/midi/sysex/parser/dynamic.py`
- ❌ **Missing**: Comprehensive parsing tests
  - Identity request parsing
  - Parameter message parsing (all message types)
  - Dynamic mapping resolution
  - Malformed data handling
  - Incomplete messages
  - Messages with extra data
  - Tone name parsing

**Priority**: **HIGH** - Ensures reliable data extraction

### 2.2 Parameter Value Conversion & Validation
**Files**: `jdxi_editor/midi/data/parameter/*.py`
- ❌ **Missing**: Parameter-specific tests
  - Value range validation (min/max)
  - Display value conversion
  - MIDI value conversion
  - Parameter type validation
  - Enum parameter handling
  - Float parameter handling (e.g., OSC_PULSE_WIDTH: 63.5)

**Priority**: **HIGH** - Ensures correct parameter values

### 2.3 Address Offset Application
**Files**: `jdxi_editor/midi/data/address/helpers.py`
- ❌ **Missing**: Comprehensive offset tests
  - Common vs Modify offset handling
  - Partial offset handling
  - Drum kit offset handling
  - Invalid offset handling
  - Offset overflow/underflow

**Priority**: **HIGH** - Critical for correct address calculation

### 2.4 JSON Composer for All Editor Types
**Files**: `jdxi_editor/midi/sysex/json_composer.py`
- ✅ Analog synth exists (`test_json_composer.py`)
- ❌ **Missing**: Other editor types
  - Digital synth (Common + Modify sections)
  - Drum kit (Common + Partial sections)
  - Program editor
  - Effects editor
  - Arpeggiator editor

**Priority**: **HIGH** - Complete feature coverage

---

## Priority 3: Edge Cases & Robustness (Medium Priority)

### 3.1 Byte Encoding/Decoding Utilities
**Files**: `jdxi_editor/midi/utils/byte.py`
- ❌ **Missing**: Comprehensive tests
  - Roland 7-bit encoding (`encode_roland_4byte`)
  - Value range edge cases (0, max, overflow)
  - Nibble splitting (`split_16bit_value_to_nibbles`)
  - Byte conversion utilities

**Priority**: **MEDIUM** - Foundation for SysEx encoding

### 3.2 SysEx Lexer Edge Cases
**Files**: `jdxi_editor/midi/sysex/lexer.py`
- ❌ **Missing**: Edge case handling
  - Incomplete addresses (3-byte patterns)
  - Unknown addresses
  - Address pattern matching
  - Multiple matches handling
  - Offset vs address distinction

**Priority**: **MEDIUM** - Improves debugging and error messages

### 3.3 Parameter Address Table Validation
**Files**: `jdxi_editor/midi/data/parameter/address/table.py`, `jdxi_editor/midi/data/parameter/offset/table.py`
- ❌ **Missing**: Table integrity tests
  - All addresses are valid
  - No duplicate addresses
  - Address ranges are correct
  - Parameter mappings are complete

**Priority**: **MEDIUM** - Prevents configuration errors

### 3.4 MIDI Message Conversion
**Files**: `jdxi_editor/midi/io/utils.py`, `jdxi_editor/midi/message/*.py`
- ❌ **Missing**: Conversion tests
  - rtmidi to mido conversion
  - mido to rtmidi conversion
  - Message type handling
  - Channel message handling
  - SysEx message conversion

**Priority**: **MEDIUM** - Ensures compatibility

---

## Priority 4: Integration & Workflow (Lower Priority)

### 4.1 Editor Parameter Synchronization
**Files**: `jdxi_editor/ui/editors/*/editor.py`
- ❌ **Missing**: Editor-specific tests
  - Parameter value updates from MIDI
  - Widget value synchronization
  - Address to widget mapping
  - Value validation in editors

**Priority**: **LOW-MEDIUM** - UI integration (may require Qt testing framework)

### 4.2 Preset Loading/Saving
**Files**: `jdxi_editor/jdxi/preset/helper.py`, `jdxi_editor/midi/program/*.py`
- ✅ MSZ round trip exists (`test_msz_round_trip.py`)
- ❌ **Missing**: Edge cases
  - Corrupted preset files
  - Incomplete preset data
  - Version compatibility
  - Preset validation

**Priority**: **LOW-MEDIUM** - Data persistence

### 4.3 MIDI File Processing
**Files**: `jdxi_editor/ui/editors/io/player.py`
- ✅ Many playback tests exist
- ❌ **Missing**: Edge cases
  - Corrupted MIDI files
  - Unsupported MIDI formats
  - Very large MIDI files
  - MIDI files with unusual timing

**Priority**: **LOW** - Already well tested

---

## Priority 5: Performance & Stress Tests (Nice to Have)

### 5.1 Large Message Handling
- SysEx messages with maximum data
- Many concurrent parameter updates
- Large preset files

### 5.2 Thread Safety
- Concurrent MIDI I/O
- Multiple editor updates
- Worker thread interactions

### 5.3 Memory Management
- Large MIDI file buffering
- Preset data caching
- Long-running sessions

**Priority**: **LOW** - Performance optimization

---

## Recommended Test Implementation Order

1. **Week 1**: Priority 1.1, 1.2, 1.3 (SysEx validation, composer errors, address mapping)
2. **Week 2**: Priority 1.4, 2.1, 2.2 (MIDI I/O errors, parser edge cases, parameter validation)
3. **Week 3**: Priority 2.3, 2.4, 3.1 (Address offsets, JSON composer, byte utilities)
4. **Week 4**: Priority 3.2, 3.3, 3.4 (Lexer, table validation, message conversion)
5. **Future**: Priorities 4 and 5 as needed

---

## Test Coverage Goals

- **Current**: ~30-40% (estimated)
- **Target**: 70-80% for critical paths
- **Focus Areas**: 
  - Error handling: 90%+
  - Core business logic: 80%+
  - UI components: 50%+ (lower priority)

---

## Notes

- Many existing tests focus on MIDI playback, which is good
- SysEx handling needs more comprehensive testing
- Error handling is under-tested across the board
- Address/parameter mapping is critical but untested
- Consider using pytest for better fixtures and parametrization
- Mock Qt components for UI tests to avoid GUI dependencies
