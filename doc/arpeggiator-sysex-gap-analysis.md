# Arpeggiator SysEx → Sliders Gap Analysis

**Gap:** JDXI Editor does not correctly route incoming Arpeggiator (Program Controller) SysEx data to the Arpeggio Editor sliders. The editor can send parameters to the device but does not receive and display incoming SysEx updates.

**Reference:** Roland MIDI Implementation Guide (PDF), Perl `jdxi_manager.pl` / `JDXidata.pm`, Roland Parameter Guide (`midi_parameters.txt`), JDXI Editor codebase.

---

## MIDI Implementation Guide (PDF) — Authoritative Reference

The Roland MIDI Implementation Guide defines two distinct SysEx blocks related to arpeggiator control:

### Program Controller (address `18 00 40 00`) — Main Arpeggiator

| Offset | Description |
|--------|-------------|
| 00 00 | (reserve) |
| 00 01 | Arpeggio Grid (0–8): 04_, 08_, 08L, 08H, 08t, 16_, 16L, 16H, 16t |
| 00 02 | Arpeggio Duration (0–9): 30, 40, 50, 60, 70, 80, 90, 100, 120, FUL |
| 00 03 | Arpeggio Switch (0–1): OFF, ON |
| 00 04 | (reserve) |
| 00 05 | Arpeggio Style (0–127): 1–128 |
| 00 06 | Arpeggio Motif (0–11): UP/L, UP/H, UP/_, dn/L, dn/H, dn/_, Ud/L, Ud/H, Ud/_, rn/L, rn/_, PHRASE |
| 00 07 | Arpeggio Octave Range (61–67): -3 to +3 |
| 00 08 | (reserve) |
| 00 09 | Arpeggio Accent Rate (0–100) |
| 00 0A | Arpeggio Velocity (0–127): REAL, 1–127 |
| 00 0B | (reserve) |
| **Total Size** | **0x0C (12 bytes)** |

### Program Zone (per-zone) — Arpeggio Switch & Octave per Zone

| Offset | Description |
|--------|-------------|
| 00 00 – 00 02 | (reserve) |
| 00 03 | Arpeggio Switch (0–1): OFF, ON |
| 00 04 – 00 18 | (reserve) |
| 00 19 | Zone Octave Shift (61–67): -3 to +3 |
| 00 1A – 00 22 | (reserve) |
| **Total Size** | **0x23 (35 bytes)** |

**Note:** Program Zone is a separate block (per Digital Synth 1/2, Analog, Drum zone). The Arpeggio Editor in JDXI Editor primarily targets **Program Controller** (main arpeggiator params). Program Zone’s per-zone Arpeggio Switch and Zone Octave Shift may require separate handling if zone-specific UI is added.

---

## Flow: Perl vs JDXI Editor

### Perl (jdxi_manager.pl) — Expected Behavior

1. **Request:** Sends RQ1 (Data Request) for Arpeggio block:
   - Address: `18 00 40 00` (Program Controller)
   - Length: 0x0C (12 bytes)

2. **Receive:** Device responds with DT1 containing 12 bytes:
   - 0x00: (reserve)
   - 0x01: Arpeggio Grid (0–8)
   - 0x02: Arpeggio Duration (0–9)
   - 0x03: Arpeggio Switch (0–1)
   - 0x04: (reserve)
   - 0x05: Arpeggio Style (0–127)
   - 0x06: Arpeggio Motif (0–11)
   - 0x07: Arpeggio Octave Range (61–67, display -3 to +3)
   - 0x08: (reserve)
   - 0x09: Arpeggio Accent Rate (0–100)
   - 0x0A: Arpeggio Velocity (0–127)
   - 0x0B: (reserve)

3. **Parse:** `ReadPatData` for `preset_type eq 'AR'`:
   - Sets `$PDM_val{18004005}` = `$arp_type[data[0x05]]` (Style)
   - Sets `$PDM_val{18004006}` = `$arp_motif[data[0x06]]` (Motif)

4. **Update sliders:** Sliders/combo boxes are bound to `$PDM_val{180040xx}`. When `ReadPatData` updates these, the UI reflects the device state.

### Roland Parameter Guide (`midi_parameters.txt`)

- **Program Controller** at offset `00 40 00` (relative to `18 00 00 00`)
- Full address: `18 00 40 00`
- Total size: 0x0C (12 bytes) — matches MIDI Implementation Guide PDF

---

## JDXI Editor — Current Behavior

### 1. Parser and PROGRAM_SECTION_MAP

- **Option B fix (effects-sysex-to-sliders-gap.md)** added `PROGRAM_SECTION_MAP` including:
  - `0x40: "CONTROLLER"`
- For address `18 00 40 00`, `_get_tone_from_data(data, "TEMPORARY_PROGRAM")` returns `("CONTROLLER", 0)` ✓

### 2. Parameter Class Selection — ❌ Gap

- `PARAMETER_ADDRESS_NAME_MAP` in `jdxi_editor/midi/map/parameter_address.py` does **not** include:
  - `(TEMPORARY_PROGRAM, CONTROLLER)` → `ArpeggioParam`
- Fallback: `JDXiMapParameterAddress.MAP.get((temporary_area, synth_tone), DrumPartialParam)` returns **DrumPartialParam** for unknown keys.
- Result: Arpeggio SysEx is parsed with **DrumPartialParam**, producing wrong parameter names (e.g. drum partial params instead of ARPEGGIO_GRID, ARPEGGIO_STYLE, etc.).

### 3. MidiIOHelper / helper.py — ❌ Gap

- In `jdxi_editor/midi/io/helper.py`, when `temporary_area == "TEMPORARY_PROGRAM"`:
  - Only `synth_tone == "COMMON"` is handled → `ProgramCommonParam`
  - **CONTROLLER** (Arpeggio) is not handled; falls through to `param_class = None` and returns early.
- Sending patch data to the device for Arpeggio parameters is not supported.

### 4. ArpeggioEditor — ❌ Gap

- `ArpeggioEditor` extends `BasicEditor` → `SynthEditor`.
- `SynthEditor` has `midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)` **commented out** (line 170).
- `ArpeggioEditor` does **not** override or add its own connection to `midi_sysex_json`.
- Result: ArpeggioEditor **never receives** SysEx JSON and never updates its sliders from incoming data.

### 5. No Arpeggio SysEx Dispatcher — ❌ Gap

- Effects editor uses `EffectsSysExDispatcher` to map parsed param names to widgets and call `setValue()`.
- Arpeggio editor has **no equivalent dispatcher**. Even if parsed data had correct keys (ARPEGGIO_GRID, ARPEGGIO_STYLE, etc.), there is no logic to:
  - Resolve param names to widgets
  - Update combo boxes and sliders from parsed values

### 6. ArpeggioParam Definition — ✓ Present

- `jdxi_editor/midi/data/parameter/arpeggio.py` defines `ArpeggioParam` with correct addresses and ranges:
  - ARPEGGIO_GRID (0x01), ARPEGGIO_DURATION (0x02), ARPEGGIO_SWITCH (0x03), ARPEGGIO_STYLE (0x05), ARPEGGIO_MOTIF (0x06), ARPEGGIO_OCTAVE_RANGE (0x07), ARPEGGIO_ACCENT_RATE (0x09), ARPEGGIO_VELOCITY (0x0A)
- Matches Roland Parameter Guide and Perl.

---

## Summary of Gaps

| Component | Status | Issue |
|-----------|--------|-------|
| **PROGRAM_SECTION_MAP** | ✓ Fixed | 0x40→CONTROLLER included (Option B) |
| **PARAMETER_ADDRESS_NAME_MAP** | ✓ Fixed | Added `(TEMPORARY_PROGRAM, CONTROLLER)` → `ArpeggioParam` |
| **Parser** | ✓ Fixed | Uses ArpeggioParam; produces correct param names |
| **helper.py (send)** | ✓ Fixed | TEMPORARY_PROGRAM handles CONTROLLER → ArpeggioParam |
| **ArpeggioEditor** | ✓ Fixed | Connected to `midi_sysex_json`; receives SysEx |
| **Arpeggio SysEx Dispatcher** | ✓ Fixed | `_dispatch_sysex_to_area` maps parsed data → widgets |
| **ArpeggioParam** | ✓ Present | Correct parameter definitions |

---

## Recommended Fixes

### 1. Add ArpeggioParam to PARAMETER_ADDRESS_NAME_MAP

```python
# jdxi_editor/midi/map/parameter_address.py
from jdxi_editor.midi.data.parameter.arpeggio import ArpeggioParam

PARAMETER_ADDRESS_NAME_MAP = {
    # ... existing entries ...
    (AreaMSB.TEMPORARY_PROGRAM.name, ProgramLMB.CONTROLLER.name): ArpeggioParam,
}
```

### 2. Add CONTROLLER handling in helper.py

In the `temporary_area == "TEMPORARY_PROGRAM"` block, add:

```python
elif synth_tone == "CONTROLLER":
    param_class = ArpeggioParam
```

### 3. Connect ArpeggioEditor to midi_sysex_json

- Option A: Override `__init__` in `ArpeggioEditor` and connect `midi_sysex_json` to a new `_dispatch_sysex_to_area` method.
- Option B: Add Arpeggio to the same pattern as Effects/Vocal: a dedicated editor that inherits from a base that connects to `midi_sysex_json` and filters by `synth_tone == "CONTROLLER"`.

### 4. Add Arpeggio SysEx dispatcher

- Create `ArpeggioSysExDispatcher` (or extend `SimpleEditorHelper` / shared dispatcher) that:
  - Accepts parsed `sysex_data` with keys ARPEGGIO_GRID, ARPEGGIO_STYLE, etc.
  - Resolves each param name to ArpeggioParam member
  - Finds the corresponding widget in `ArpeggioEditor.controls` (or equivalent)
  - Calls `setValue()` / `setCurrentIndex()` with the correct display value
- Handle enum/display mappings (e.g. ARPEGGIO_GRID index → combo display text, ARPEGGIO_OCTAVE_RANGE 61–67 → -3 to +3).

### 5. Data layout note

Program Controller data is 12 bytes with **no tone name**. The parser uses `get_byte_offset_by_tone_name(data, param.address, offset=12)`. For address `18 00 40 00`, the payload starts at byte 12 in the SysEx (after F0 41 xx 00 00 00 0E 12 18 00 40 00). So `data[12]` = offset 0x00, `data[13]` = offset 0x01 (Grid), etc. The existing `parse_parameters` logic should work with `ArpeggioParam` once the correct parameter class is selected.

---

## Perl Reference

`doc/perl/JDXidata.pm` (lines 521–556):

```perl
our %ARP=(
    preset_type => 'AR',
    addr     => ["\x18\x00\x40\x00"],
    rqlen    => ["\x00\x00\x00\x0C"],
    datalen  => [12],
    ...
);
```

`doc/perl/jdxi_manager.pl` (lines 3272–3289): `ARP_Frame` builds sliders with addresses `18004001`, `18004002`, `18004003`, `18004005`, `18004006`, `18004007`, `18004009`, `1800400A`.
