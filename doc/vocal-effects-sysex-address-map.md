# Vocal Effects SysEx Address Map

Mapping between JD-Xi Parameter Guide (`doc/midi_parameters.txt`) and JDXI Editor parameter definitions.

**Roland SysEx structure:** `F0 41 10 00 00 00 0E 12 [addr4] [data...] F7`

**Base address:** Temporary Program (0x18 00 00 00)
- Program Common: LMB=0x00 (COMMON)
- Program Vocal Effect: LMB=0x01 (VOCAL_EFFECT)

---

## Program Common (LMB=0x00)

Vocal-related parameters in Program Common section. Offsets from JD-Xi Parameter Guide (Program Name 1–12 at 0x00–0x14, then):

| JD-Xi offset | Param | JDXI Editor | Status |
|--------------|-------|-------------|--------|
| 0x16 | Program Level (0–127) | ProgramCommonParam.PROGRAM_LEVEL (0x10) | ⚠ Code uses 0x10; guide says 0x16 |
| 0x17–0x1A | Program Tempo (500–30000) | ProgramCommonParam.PROGRAM_TEMPO (0x11) | ⚠ Code uses 0x11; guide says 0x17 |
| 0x1B | (reserve) | — | — |
| 0x1C | Vocal Effect (0–2) OFF, VOCODER, AUTO-PITCH | ProgramCommonParam.VOCAL_EFFECT | ✓ Fixed (Phase 1) |
| 0x1D | Vocal Effect Part (0–1) 1–2 | ProgramCommonParam.VOCAL_EFFECT_PART | ✓ Match |
| 0x1E | Auto Note Switch (0–1) OFF, ON | ProgramCommonParam.AUTO_NOTE_SWITCH | ✓ Match |

### VOCAL_EFFECT_NUMBER (Phase 1)

- **ProgramCommonParam.VOCAL_EFFECT_NUMBER** uses address **0x1B** (reserve). JD-Xi guide does not document Vocal Effect preset (1–21). Address is a placeholder until the correct offset is found.

---

## Program Vocal Effect (LMB=0x01, base 18 00 01 00)

| JD-Xi offset | Param | JDXI Editor | Status |
|--------------|-------|-------------|--------|
| 0x00 | Level (0–127) | VocalFXParam.LEVEL | ✓ Match |
| 0x01 | Pan (0–127) L64–63R | VocalFXParam.PAN | ✓ Match |
| 0x02 | Delay Send Level | VocalFXParam.DELAY_SEND_LEVEL | ✓ Match |
| 0x03 | Reverb Send Level | VocalFXParam.REVERB_SEND_LEVEL | ✓ Match |
| 0x04 | Output Assign (0–4) EFX1, EFX2, DLY, REV, DIR | VocalFXParam.OUTPUT_ASSIGN | ✓ Match |
| 0x05 | Auto Pitch Switch (0–1) | VocalFXParam.AUTO_PITCH_SWITCH | ✓ Match |
| 0x06 | Auto Pitch Type (0–3) SOFT, HARD, ELECTRIC1, ELECTRIC2 | VocalFXParam.AUTO_PITCH_TYPE | ✓ Match |
| 0x07 | Auto Pitch Scale (0–1) CHROMATIC, Maj(Min) | VocalFXParam.AUTO_PITCH_SCALE | ✓ Match |
| 0x08 | Auto Pitch Key (0–23) | VocalFXParam.AUTO_PITCH_KEY | ✓ Match |
| 0x09 | Auto Pitch Note (0–11) | VocalFXParam.AUTO_PITCH_NOTE | ✓ Match |
| 0x0A | Auto Pitch Gender (0–20) -10 to +10 | VocalFXParam.AUTO_PITCH_GENDER | ✓ Match |
| 0x0B | Auto Pitch Octave (0–2) -1 to +1 | VocalFXParam.AUTO_PITCH_OCTAVE | ✓ Match |
| 0x0C | Auto Pitch Balance (0–100) D100:0W–D0:100W | VocalFXParam.AUTO_PITCH_BALANCE | ✓ Match |
| 0x0D | Vocoder Switch (0–1) | VocalFXParam.VOCODER_SWITCH | ✓ Match |
| 0x0E | Vocoder Envelope (0–2) SHARP, SOFT, LONG | VocalFXParam.VOCODER_ENVELOPE | ✓ Match |
| 0x0F | Vocoder Level (0–127) | VocalFXParam.VOCODER_LEVEL | ✓ Match |
| 0x10 | Vocoder Mic Sens | VocalFXParam.VOCODER_MIC_SENS | ✓ Match |
| 0x11 | Vocoder Synth Level | VocalFXParam.VOCODER_SYNTH_LEVEL | ✓ Match |
| 0x12 | Vocoder Mic Mix Level | VocalFXParam.VOCODER_MIC_MIX | ✓ Match |
| 0x13 | Vocoder Mic HPF (0–13) | VocalFXParam.VOCODER_MIC_HPF | ✓ Match |

**Program Vocal Effect:** All offsets 0x00–0x13 match JDXI Editor VocalFXParam. ✓

---

## JDXI Editor Address Factory

```python
# Vocal FX uses Program Vocal Effect section (LMB=0x01)
create_vocal_fx_address() -> JDXiSysExAddress(
    JDXiSysExAddressStartMSB.TEMPORARY_PROGRAM,  # 0x18
    JDXiSysExOffsetTemporaryToneUMB.COMMON,     # 0x00
    JDXiSysExOffsetProgramLMB.VOCAL_EFFECT,     # 0x01
    0
)
```

---

## Bipolar Parameter Conversion

- **Pan:** Display -64..+63, MIDI 0..127 (center 64)
- **Auto Pitch Gender:** Display -10..+10, MIDI 0..20 (center 10)

Verify `VocalFXParam.convert_to_midi` and `convert_from_midi` for these params.
