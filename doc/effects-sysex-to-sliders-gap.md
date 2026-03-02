# Effects SysEx → Sliders Gap Analysis

**Gap:** JDXI Editor does not correctly route incoming Delay and Reverb SysEx data to their sliders. Effect 1 and Effect 2 may also be affected.

**Root cause:** `JDXiMapSynthTone` (used by the SysEx parser to determine which parameter class to use) does not include PROGRAM section LMB values for EFFECT_1, EFFECT_2, DELAY, and REVERB.

---

## Flow: Perl vs JDXI Editor

### Perl (jdxi_manager.pl) — Expected Behavior

The Perl implementation (referenced in `doc/effects-sysex-address-map.md`, `doc/effects-migration-plan.md`) handles effects as follows:

1. **Request:** Sends RQ1 (Data Request) for each effect block:
   - Effect 1: `18 00 02 00` (0x111 bytes)
   - Effect 2: `18 00 04 00` (0x111 bytes)
   - Delay: `18 00 06 00` (0x64 bytes)
   - Reverb: `18 00 08 00` (0x63 bytes)

2. **Receive:** Device responds with DT1 (Data Set) containing the parameter bytes.

3. **Parse:** Maps address LMB (3rd byte of address) to section:
   - 0x02 → Effect 1 params (EFX1_TYPE, EFX1_LEVEL, …)
   - 0x04 → Effect 2 params
   - 0x06 → Delay params (On/Off, Level, Type, Time, Note, Feedback, HF Damp, …)
   - 0x08 → Reverb params (On/Off, Type, Time, HF Damp, Level, …)

4. **Update sliders:** For each parsed param, finds the corresponding Scale/Slider widget and calls `setValue()` (or equivalent) with the display value.

---

## JDXI Editor — Current Behavior

### 1. Parser (`jdxi_editor/midi/sysex/parser/utils.py`)

- `parse_sysex()` uses `get_temporary_area(data)` → `TEMPORARY_PROGRAM` for address `18 00 xx xx`.
- `_get_tone_from_data(data, "TEMPORARY_PROGRAM")` calls `get_synth_tone(data[LMB])`.
- `get_synth_tone()` uses `JDXiMapSynthTone.MAP`:

```python
# jdxi_editor/midi/map/synth_tone.py
SYNTH_TONE_MAP = {
    0x00: "COMMON",
    0x01: "VOCAL_EFFECT",
    0x20: "PARTIAL_1",
    0x21: "PARTIAL_2",
    0x22: "PARTIAL_3",
    0x50: "MODIFY",
}
```

**Missing:** `0x02` (EFFECT_1), `0x04` (EFFECT_2), `0x06` (DELAY), `0x08` (REVERB).

- For LMB = 0x02, 0x04, 0x06, 0x08 → `MAP.get(byte, "COMMON")` returns `"COMMON"`.

### 2. Parameter Class Selection

- `JDXiMapParameterAddress.MAP.get((temporary_area, synth_tone), DrumPartialParam)`:
  - For Delay: `("TEMPORARY_PROGRAM", "COMMON")` → **ProgramCommonParam** (wrong)
  - Expected: `("TEMPORARY_PROGRAM", "DELAY")` → **DelayParam**

### 3. Parsed Data

- With `ProgramCommonParam`, the parser fills `parsed_data` with PROGRAM_LEVEL, PROGRAM_TEMPO, TONE_NAME_1, etc., using byte offsets from Program Common (0x00–0x1F).
- Delay/Reverb bytes (e.g. DELAY_LEVEL at 0x01, DELAY_ON_OFF at 0x00) are misinterpreted as Program Common params at the same offsets.

### 4. Dispatch to Effects Editor

- `EffectsCommonEditor._dispatch_sysex_to_area()` receives the parsed JSON.
- `EffectsSysExDispatcher.dispatch()` iterates over `sysex_data`:
  - `param = registry.resolve(name)` — registry has DelayParam/ReverbParam names (DELAY_LEVEL, DELAY_ON_OFF, etc.).
  - But parsed_data has wrong keys (e.g. PROGRAM_LEVEL, TONE_NAME_1) when the message was actually Delay/Reverb.
- Result: Delay/Reverb params are never found in the registry, or wrong params are applied. Sliders are not updated.

---

## Summary of Gaps

| Component | Issue |
|-----------|-------|
| **JDXiMapSynthTone** | Missing 0x02→EFFECT_1, 0x04→EFFECT_2, 0x06→DELAY, 0x08→REVERB |
| **Parser** | Delay/Reverb SysEx is parsed as Program Common |
| **PARAMETER_ADDRESS_NAME_MAP** | Correct (EFFECT_1→Effect1Param, DELAY→DelayParam, REVERB→ReverbParam) |
| **EffectsSysExDispatcher** | Correct logic; fails because parsed_data has wrong keys |
| **EffectParamRegistry** | Correct; has DelayParam/ReverbParam members |

---

## Fix

### 1. Extend `JDXiMapSynthTone` for PROGRAM area — ✅ Implemented (Option B)

The same LMB byte can mean different things for TEMPORARY_PROGRAM vs TEMPORARY_TONE:

- **TEMPORARY_PROGRAM (0x18):** LMB 0x02=EFFECT_1, 0x04=EFFECT_2, 0x06=DELAY, 0x08=REVERB, 0x20=PART_DIGITAL_SYNTH_1, etc.
- **TEMPORARY_TONE (0x19):** LMB 0x20=PARTIAL_1, 0x21=PARTIAL_2, 0x22=PARTIAL_3, 0x50=MODIFY.

So mapping must be **area-aware**. Options:

**Option A:** Add PROGRAM-specific LMB values to a separate map and use it when `temporary_area == "TEMPORARY_PROGRAM"`:

```python
# In tone_mapper.py or a new module
PROGRAM_SECTION_MAP = {
    0x00: "COMMON",
    0x01: "VOCAL_EFFECT",
    0x02: "EFFECT_1",
    0x04: "EFFECT_2",
    0x06: "DELAY",
    0x08: "REVERB",
    0x20: "PART_DIGITAL_SYNTH_1",
    0x21: "PART_DIGITAL_SYNTH_2",
    0x22: "PART_ANALOG",
    0x23: "PART_DRUM",
    0x30: "ZONE_DIGITAL_SYNTH_1",
    0x31: "ZONE_DIGITAL_SYNTH_2",
    0x32: "ZONE_ANALOG",
    0x33: "ZONE_DRUM",
    0x40: "CONTROLLER",
}
```

**Option B:** In `_get_tone_from_data()`, branch on `temporary_area`:

```python
def _get_tone_from_data(data: bytes, temporary_area: str) -> tuple[str, int]:
    if len(data) <= JDXiSysExMessageLayout.ADDRESS.LMB:
        return UNKNOWN, 0
    byte_value = data[JDXiSysExMessageLayout.ADDRESS.LMB]
    if temporary_area == TemporaryToneUMB.DRUM_KIT.name:
        return get_drum_tone(byte_value)
    if temporary_area == "TEMPORARY_PROGRAM":
        return PROGRAM_SECTION_MAP.get(byte_value, "COMMON"), 0
    return get_synth_tone(byte_value)
```

### 2. Routing to Effects Editor

The `midi_sysex_json` signal is emitted to all connected editors. `EffectsCommonEditor._dispatch_sysex_to_area` already filters by `temporary_area == "TEMPORARY_PROGRAM"` and dispatches. Once the parser produces correct keys (DELAY_LEVEL, REVERB_TYPE, etc.), the dispatcher will find them in the registry and update the widgets.

### 3. Verification

After the fix:

1. Request Delay data (address `18 00 06 00`).
2. Parser should produce `synth_tone="DELAY"` and `parameter_cls=DelayParam`.
3. `parsed_data` should contain DELAY_ON_OFF, DELAY_LEVEL, DELAY_REVERB_SEND_LEVEL, DELAY_PARAM_1, etc.
4. Effects editor receives JSON, dispatcher resolves each name to DelayParam member, finds widget in `controls`, calls `setValue()`.

---

## Perl Reference (Inferred)

The Perl files (`doc/perl/jdxi_manager.pl`, `doc/perl/JDXidata.pm`) are gitignored (`.gitignore`: `*.pl`, `*.pm`). The behavior above is inferred from:

- `doc/effects-sysex-address-map.md` (Perl address tables)
- `doc/effects-migration-plan.md` (Perl vs JDXI Editor)
- `doc/midi-parameters-gap-analysis.md` (Perl comparison)
- `building/apple/jdxi_manager/build_jdxi_manager_mac.sh` (references jdxi_manager.pl, JDXidata.pm)

To fully validate Perl behavior, the user would need to provide the Perl source or run the Perl app and observe SysEx request/response and slider updates.
