# System Common & System Controller — Gap Analysis

Gap analysis of **System Common** (0x02 00 00 00) and **System Controller** (0x02 00 03 00) UI coverage, comparing JDXI Editor with the Perl implementation and the Parameter Guide (`doc/midi_parameters.txt`).

**Reference:** `doc/midi_parameters.txt` (lines 167–227)  
**Perl source:** `doc/perl/jdxi_manager.pl`, `doc/perl/JDXidata.pm`

---

## Executive Summary

| Area | Parameter Guide | JDXI Editor Data | JDXI Editor UI | Perl |
|------|-----------------|-----------------|----------------|------|
| **System Common** | 6 parameters | SystemCommonParam ✓ | ❌ None | ❌ None |
| **System Controller** | 5 parameters | SystemControllerParam ✓ | ❌ None | ❌ None |

**Main gaps:**
1. **No UI** — Neither area has a dedicated editor; parameters are not exposed to users.
2. **Parser / map** — `PARAMETER_ADDRESS_NAME_MAP` and `JDXiMapTemporaryArea` do not include System (0x02); incoming SysEx for these areas resolves to "Unknown".
3. **SystemCommonParam bug** — `get_display_value` uses `ParameterSpec(value - 1024) / 10` instead of `(value - 1024) / 10`.
4. **Perl** — No System Common or System Controller support.

---

## 1. Parameter Guide Reference

### System Common (Address 02 00 00 00, Size 0x2B)

| Offset | Parameter | Raw Range | Display Range |
|--------|-----------|-----------|---------------|
| 0x00–0x03 | Master Tune | 24–2024 | -100.0 – +100.0 [cent] |
| 0x04 | Master Key Shift | 40–88 | -24 – +24 |
| 0x05 | Master Level | 0–127 | — |
| 0x06–0x10 | (reserve) | — | — |
| 0x11 | Program Control Channel | 0–16 | 1–16, OFF |
| 0x12–0x28 | (reserve) | — | — |
| 0x29 | Receive Program Change | 0–1 | OFF, ON |
| 0x2A | Receive Bank Select | 0–1 | OFF, ON |

### System Controller (Address 02 00 03 00, Size 0x11)

| Offset | Parameter | Raw Range | Display Range |
|--------|-----------|-----------|---------------|
| 0x00 | Transmit Program Change | 0–1 | OFF, ON |
| 0x01 | Transmit Bank Select | 0–1 | OFF, ON |
| 0x02 | Keyboard Velocity | 0–127 | REAL, 1–127 |
| 0x03 | Keyboard Velocity Curve | 1–3 | LIGHT, MEDIUM, HEAVY |
| 0x04 | Keyboard Velocity Curve Offset | 54–73 | -10 – +9 |
| 0x05–0x10 | (reserve) | — | — |

---

## 2. JDXI Editor — Data Layer

### 2.1 SystemCommonParam (`jdxi_editor/midi/data/parameter/system/common.py`)

| Parameter | Offset | Status | Notes |
|-----------|--------|--------|-------|
| MASTER_TUNE | 0x00 | ✓ | 4-byte encoding; `SystemCommonMessage` handles nibbles |
| MASTER_KEY_SHIFT | 0x04 | ✓ | |
| MASTER_LEVEL | 0x05 | ✓ | |
| PROGRAM_CTRL_CH | 0x11 | ✓ | |
| RX_PROGRAM_CHANGE | 0x29 | ✓ | |
| RX_BANK_SELECT | 0x2A | ✓ | |

**Bug:** `get_display_value` line 56:
```python
cents = ParameterSpec(value - 1024) / 10  # WRONG: ParameterSpec is a class
```
Should be:
```python
cents = (value - 1024) / 10
```

**Missing:** `get_by_name` (unlike `SystemControllerParam`).

### 2.2 SystemControllerParam (`jdxi_editor/midi/data/parameter/system/controller.py`)

| Parameter | Offset | Status | Notes |
|-----------|--------|--------|-------|
| TRANSMIT_PROGRAM_CHANGE | 0x00 | ✓ | |
| TRANSMIT_BANK_SELECT | 0x01 | ✓ | |
| KEYBOARD_VELOCITY | 0x02 | ✓ | |
| KEYBOARD_VELOCITY_CURVE | 0x03 | ✓ | |
| KEYBOARD_VELOCITY_CURVE_OFFSET | 0x04 | ✓ | |

Has `get_by_name`.

### 2.3 SysEx Messages

- **SystemCommonMessage** (`jdxi_editor/midi/message/areas/system_common.py`): Exists; uses msb=SYSTEM (0x01). *Note: Address map says 02 00 00 00 = System; verify msb vs. Setup (0x01 vs 0x02).*
- **SystemControllerMessage** (`jdxi_editor/midi/message/areas/system_controller.py`): Exists; uses msb=SETUP (0x02), lmb=CONTROLLER (0x03).

---

## 3. JDXI Editor — Parser & Map Gaps

### 3.1 PARAMETER_ADDRESS_NAME_MAP (`jdxi_editor/midi/map/parameter_address.py`)

The map uses `(AreaMSB.name, ProgramLMB.name)` keys. It only covers:

- `AreaMSB.TEMPORARY_PROGRAM` (0x18) — Program Common, Vocal Effect, Effects, Arpeggio, etc.
- `TemporaryToneUMB` — Digital Synth 1/2, Analog, Drum Kit

**System (0x02) is not in the map.** There are no entries for:

- System Common (02 00 00 xx)
- System Controller (02 00 03 xx)

### 3.2 JDXiMapTemporaryArea (`jdxi_editor/midi/map/temporary_area.py`)

`get_temporary_area()` maps address bytes to area names. It only includes:

- (0x18, 0x00) → TEMPORARY_PROGRAM
- (0x19, 0x00) → DIGITAL_SYNTH_1
- (0x19, 0x20) → DIGITAL_SYNTH_2
- (0x19, 0x40) → ANALOG_SYNTH
- (0x19, 0x60) → DRUM_KIT

**For (0x02, 0x00, 0x00) or (0x02, 0x00, 0x03):** the map returns `"Unknown"`.

### 3.3 Parser Flow (`jdxi_editor/midi/sysex/parser/dynamic.py`)

1. `get_temporary_area(data)` → "Unknown" for System addresses
2. `JDXiMapParameterAddress.MAP.get((temporary_area, synth_tone), ...)` → no match
3. Fallback to `DrumPartialParam` (wrong for System Common/Controller)
4. Incoming System SysEx is not routed to any System-specific editor

---

## 4. JDXI Editor — UI Coverage

| Parameter | UI Location | Status |
|-----------|-------------|--------|
| Master Tune | — | ❌ No UI |
| Master Key Shift | — | ❌ No UI |
| Master Level | — | ❌ No UI (Program Mixer uses ProgramCommonParam.PROGRAM_LEVEL, not System Master Level) |
| Program Control Channel | — | ❌ No UI |
| Receive Program Change | — | ❌ No UI |
| Receive Bank Select | — | ❌ No UI |
| Transmit Program Change | — | ❌ No UI |
| Transmit Bank Select | — | ❌ No UI |
| Keyboard Velocity | — | ❌ No UI |
| Keyboard Velocity Curve | — | ❌ No UI |
| Keyboard Velocity Curve Offset | — | ❌ No UI |

**Note:** The Program Mixer "Master" track uses `ProgramCommonParam.PROGRAM_LEVEL` (Program Common 0x18 00 00 xx), which is per-program level, not System Common Master Level (0x02 00 00 05).

---

## 5. Perl Implementation

Searches for `02 00`, `0200`, `System Common`, `System Controller`, `Master Tune`, `velocity`, etc. in `doc/perl/jdxi_manager.pl` and `doc/perl/JDXidata.pm` return **no matches**.

The Perl app uses addresses such as:

- `\x18\x00\x02\x00` (Program Effect 1)
- `\x18\x00\x40\x00` (Program Controller / Arpeggio)
- `\x19\x01\x00\x00` (Digital Synth 1 Tone)
- etc.

**Conclusion:** Perl does not implement System Common or System Controller. No SysEx read/write or UI for these areas.

---

## 6. Recommended Actions

| Priority | Action | Status |
|----------|--------|--------|
| **P1** | Fix `SystemCommonParam.get_display_value` bug (line 56) | Done |
| **P1** | Add System Common and System Controller to `PARAMETER_ADDRESS_NAME_MAP` | Done |
| **P1** | Add System area to `JDXiMapTemporaryArea` (e.g. SYSTEM_COMMON, SYSTEM_CONTROLLER) | Done |
| **P1** | Extend `dynamic_map_resolver` to handle System addresses and route to correct param class | Done |
| **P2** | Add `get_by_name` to `SystemCommonParam` for consistency | Done |
| **P2** | Create System Settings editor UI (Master Tune, Master Level, Key Shift, RX/TX Program Change/Bank Select, Keyboard Velocity, Velocity Curve) | Done |
| **P2** | Add MidiRequests for System Common and System Controller (data request on editor show) | Done |
| **P3** | Verify SystemCommonMessage msb (0x01 vs 0x02) against Roland address map | Done (use SETUP=0x02) |

---

## 7. Related Files

| File | Purpose |
|------|---------|
| `jdxi_editor/midi/data/parameter/system/common.py` | SystemCommonParam |
| `jdxi_editor/midi/data/parameter/system/controller.py` | SystemControllerParam |
| `jdxi_editor/midi/map/parameter_address.py` | PARAMETER_ADDRESS_NAME_MAP |
| `jdxi_editor/midi/map/temporary_area.py` | JDXiMapTemporaryArea |
| `jdxi_editor/midi/sysex/parser/dynamic.py` | dynamic_map_resolver |
| `jdxi_editor/midi/message/areas/system_common.py` | SystemCommonMessage |
| `jdxi_editor/midi/message/areas/system_controller.py` | SystemControllerMessage |
| `doc/midi_parameters.txt` | Parameter Guide (lines 167–227) |
| `doc/midi-parameters-gap-analysis.md` | Broader gap analysis |
