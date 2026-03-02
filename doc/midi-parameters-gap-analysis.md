# MIDI Parameters Gap Analysis

Gap analysis of JDXI Editor vs. Roland JD-Xi Parameter Guide (`doc/midi_parameters.txt`, lines 1–1484), with comparison to the Perl implementation (`doc/perl/jdxi_manager.pl`, `doc/perl/JDXidata.pm`).

**Reference:** `doc/midi_parameters.txt`  
**Perl source:** `doc/perl/jdxi_manager.pl`, `doc/perl/JDXidata.pm`  
**Scope:** SysEx Parameter Address Map, Control Changes, NRPN

---

## Roland Address Hierarchy (from Parameter Address Map PDF)

Addresses are **hierarchical**: Start Address + Offset = full address.

| Start Address | Description |
|---------------|-------------|
| 01 00 00 00 | Setup |
| 02 00 00 00 | System |
| 18 00 00 00 | Temporary Program |
| 19 00 00 00 | Temporary Tone (Digital Synth Part 1) |
| 19 20 00 00 | Temporary Tone (Digital Synth Part 2) |
| 19 40 00 00 | Temporary Tone (Analog Synth Part) |
| 19 60 00 00 | Temporary Tone (Drums Part) |

**Program** offsets (relative to 18 00 00 00): 00 00 00, 00 01 00, 00 02 00, 00 04 00, 00 06 00, 00 08 00, 00 20–23 00, 00 30–33 00, 00 40 00.

**Temporary Tone** offsets (relative to each part base):
- SuperNATURAL: **01 00 00**
- Analog: **02 00 00**
- Drum Kit: **10 00 00**

So full addresses are: **Base + Offset** (e.g. 19 00 00 00 + 01 00 00 = **19 01 00 00** for Digital Synth 1 tone data).

---

## Perl vs Guide vs JDXI Editor — Address Summary

| Area | Full address (Base + Offset) | Perl addr | Perl rqlen/datalen | JDXI Editor |
|------|-----------------------------|-----------|---------------------|-------------|
| Program Effect 1 | 18 00 02 00 | `\x18\x00\x02\x00` | 0x111 (273), 145 | Effect1Param ✓ |
| Program Effect 2 | 18 00 04 00 | `\x18\x00\x04\x00` | 0x111, 145 | Effect2Param ✓ |
| Program Delay | 18 00 06 00 | `\x18\x00\x06\x00` | 0x64 (100), 100 | DelayParam ✓ |
| Program Reverb | 18 00 08 00 | `\x18\x00\x08\x00` | 0x63 (99), 99 | ReverbParam ✓ |
| Program Vocal Effect | 18 00 01 00 | `\x18\x00\x01\x00` | 0x18 (24), 24 | VocalFXParam ✓ |
| Program Controller (Arp) | 18 00 40 00 | `\x18\x00\x40\x00` | 0x0C (12), 12 | ArpeggioParam ✓ |
| Digital Synth 1 Tone | 19 00 00 00 + 01 00 00 = **19 01 00 00** | `\x19\x01\x00\x00` | 0x40, 64 | DigitalCommonParam ✓ |
| Digital Synth 2 Tone | 19 20 00 00 + 01 00 00 = **19 21 00 00** | `\x19\x21\x00\x00` | 0x40, 64 | DigitalCommonParam ✓ |
| Analog Tone | 19 40 00 00 + 02 00 00 = **19 42 00 00** | `\x19\x42\x00\x00` | 0x40, 64 | AnalogParam ✓ |
| Drum Kit | 19 60 00 00 + 10 00 00 = **19 70 00 00** | `\x19\x70\x00\x00` | 0x12, 18 | DrumCommonParam ✓ |

**Perl addresses are correct.** They use the full computed address (Base + Temporary Tone offset). The Guide lists the base and offset separately; Perl combines them.

---

## Executive Summary

| Area | Guide | JDXI Editor | Status |
|------|-------|-------------|--------|
| Setup | 0x01 00 00 00 | — | ❌ Not implemented |
| System Common | 0x02 00 00 00 | SystemCommonParam | ⚠ Partial |
| System Controller | 0x02 00 03 00 | — | ❌ Not implemented |
| Program Common | 0x18 00 00 00 | ProgramCommonParam | ⚠ Address mismatches |
| Program Vocal Effect | 0x18 00 01 00 | VocalFXParam | ✓ Match |
| Program Effect 1 | 0x18 00 02 00 | Effect1Param | ✓ Present |
| Program Effect 2 | 0x18 00 04 00 | Effect2Param | ✓ Present |
| Program Delay | 0x18 00 06 00 | DelayParam | ⚠ Address mismatch (0x00) |
| Program Reverb | 0x18 00 08 00 | ReverbParam | ✓ Present |
| Program Part | 0x18 00 20–23 00 | PartMessage (hardcoded lsb) | ⚠ No PartParam enum |
| Program Zone | 0x18 00 30–33 00 | ProgramZoneParam | ⚠ Partial |
| Program Controller | 0x18 00 40 00 | ArpeggioParam | ✓ Present |
| SuperNATURAL Tone | 0x19 xx 00 00 | DigitalCommonParam, DigitalPartialParam, DigitalModifyParam | ✓ Present |
| Analog Tone | 0x19 40 00 00 | AnalogParam | ✓ Present |
| Drum Kit | 0x19 60 00 00 | DrumCommonParam, DrumPartialParam | ✓ Present |
| Control Changes / NRPN | CC# 12–119, NRPN | — | ❌ Not systematically mapped |

---

## 1. Setup (0x01 00 00 00)

**Guide offsets** (Roland PDF): 0x00–0x03 reserve; then:
| Offset | Parameter | Value |
|--------|-----------|-------|
| 0x04 | Program BS MSB (CC# 0) | 0–127 |
| 0x05 | Program BS LSB (CC# 32) | 0–127 |
| 0x06 | Program PC | 0–127 |
| 0x07–0x3A | (reserve) | — |
| Total size | 0x3B | |

**JDXI Editor:** No Setup parameter class. Bank Select / Program Change handled via MIDI CC, not SysEx.

| Gap | Action |
|-----|--------|
| Setup SysEx read/write | Optional: add SetupParam for Program BS MSB/LSB, PC if SysEx-based program switching is needed |

---

## 2. System Common (0x02 00 00 00)

**Guide offsets:**
| Offset | Parameter | Value |
|--------|-----------|-------|
| 0x00–0x03 | Master Tune (4 bytes) | 24–2024 (−100.0–+100.0 cent) |
| 0x04 | Master Key Shift | 40–88 (−24–+24) |
| 0x05 | Master Level | 0–127 |
| 0x11 | Program Control Channel | 0–16 (1–16, OFF) |
| 0x29 | Receive Program Change | 0–1 |
| 0x2A | Receive Bank Select | 0–1 |

**JDXI Editor:** `SystemCommonParam` — MASTER_TUNE (0x00), MASTER_KEY_SHIFT (0x04), MASTER_LEVEL (0x05), PROGRAM_CTRL_CH (0x11), RX_PROGRAM_CHANGE (0x29), RX_BANK_SELECT (0x2A).

| Gap | Action |
|-----|--------|
| Master Tune 4-byte encoding | Verify nibble/byte packing matches guide |

---

## 3. System Controller (0x02 00 03 00)

**Guide offsets:**
| Offset | Parameter | Value |
|--------|-----------|-------|
| 0x00 | Transmit Program Change | 0–1 |
| 0x01 | Transmit Bank Select | 0–1 |
| 0x02 | Keyboard Velocity | 0–127 (REAL, 1–127) |
| 0x03 | Keyboard Velocity Curve | 1–3 (LIGHT, MEDIUM, HEAVY) |
| 0x04 | Keyboard Velocity Curve Offset | 54–73 (−10–+9) |

**JDXI Editor:** Not implemented.

| Gap | Action |
|-----|--------|
| System Controller params | Add SystemControllerParam if global transmit/velocity settings are needed |

---

## 4. Program Common (0x18 00 00 00)

**Guide offsets** (Roland PDF): Program Names are **sequential** 0x00–0x0B:
| Offset | Parameter | JDXI Editor | Status |
|--------|-----------|-------------|--------|
| 0x00 | Program Name 1 | TONE_NAME_1 @ 0x00 | ✓ |
| 0x01 | Program Name 2 | TONE_NAME_2 @ 0x01 | ✓ |
| … | … | … | ✓ |
| 0x0B | Program Name 12 | TONE_NAME_12 @ 0x0B | ✓ |
| 0x0C–0x0F | (reserve) | — | — |
| 0x16 | Program Level (0–127) | PROGRAM_LEVEL @ 0x10 | ⚠ Addr: JDXI 0x10 vs Guide 0x16 |
| 0x17–0x1A | Program Tempo (4 bytes) | PROGRAM_TEMPO @ 0x11 | ⚠ Addr: JDXI 0x11 vs Guide 0x17 |
| 0x1B | (reserve) | VOCAL_EFFECT_NUMBER @ 0x1B | ⚠ Undocumented |
| 0x1C | Vocal Effect | VOCAL_EFFECT @ 0x1C | ✓ |
| 0x1D | Vocal Effect Part | VOCAL_EFFECT_PART @ 0x1D | ✓ |
| 0x1E | Auto Note Switch | AUTO_NOTE_SWITCH @ 0x1E | ✓ |

**Program Name layout:** Roland PDF confirms sequential 0x00–0x0B for names 1–12. JDXI Editor matches. ✓

**Program Level / Tempo:** `midi_parameters.txt` lists Level @ 0x16, Tempo @ 0x17–0x1A. JDXI Editor uses 0x10, 0x11. Confirm with PDF/hardware which is correct.

| Gap | Action |
|-----|--------|
| PROGRAM_LEVEL, PROGRAM_TEMPO | If PDF/guide use 0x16, 0x17–0x1A, align JDXI Editor addresses |
| VOCAL_EFFECT_NUMBER | Guide marks 0x1B reserve; effect preset number not documented |

---

## 5. Program Vocal Effect (0x18 00 01 00)

**Guide offsets 0x00–0x13:** Level, Pan, Delay/Reverb Send, Output Assign, Auto Pitch (Switch, Type, Scale, Key, Note, Gender, Octave, Balance), Vocoder (Switch, Envelope, Level, Mic Sens, Synth Level, Mic Mix, Mic HPF).

**JDXI Editor:** `VocalFXParam` — all offsets 0x00–0x13 match. ✓

---

## 6. Program Effect 1 (0x18 00 02 00)

**Guide:** EFX1 Type (0x00), Level (0x01), Delay/Reverb Send (0x02–0x03), Output Assign (0x04), reserve 0x05–0x10, EFX1 Parameter 1–32 (4-byte, 0x11–0x10D).

**JDXI Editor:** `Effect1Param` — Type, Level, Delay/Reverb Send, Output Assign, Param 1–32. ✓

---

## 7. Program Effect 2 (0x18 00 04 00)

**Guide:** EFX2 Type (0x00, 0 or 5–8), Level, Delay/Reverb Send, reserve 0x04–0x10, Param 1–32 (4-byte).

**JDXI Editor:** `Effect2Param` — matches. ✓

---

## 8. Program Delay (0x18 00 06 00)

**Guide offsets:**
| Offset | Parameter | JDXI Editor | Status |
|--------|-----------|-------------|--------|
| 0x00 | (reserve) | DELAY_ON_OFF @ 0x00 | ⚠ Guide says reserve |
| 0x01 | Delay Level | DELAY_LEVEL @ 0x01 | ✓ |
| 0x02 | (reserve) | — | — |
| 0x03 | Delay Reverb Send | DELAY_REVERB_SEND_LEVEL @ 0x03 | ✓ |
| 0x04+ | Delay Param 1–24 (4-byte) | DELAY_PARAM_1, etc. | ✓ |

**JDXI Editor:** `DelayParam` includes `DELAY_ON_OFF` at 0x00; guide marks 0x00 as reserve. On/Off may be part of another block or undocumented.

| Gap | Action |
|-----|--------|
| DELAY_ON_OFF @ 0x00 | Confirm with hardware; guide may omit or use different encoding |

---

## 9. Program Reverb (0x18 00 08 00)

**Guide:** 0x00 reserve, 0x01 Level, 0x02 reserve, 0x03+ Reverb Param 1–24 (4-byte).

**JDXI Editor:** `ReverbParam` — REVERB_ON_OFF @ 0x00, REVERB_LEVEL @ 0x01, REVERB_TYPE @ 0x03, etc. Guide marks 0x00 as reserve; REVERB_ON_OFF may be undocumented or elsewhere.

| Gap | Action |
|-----|--------|
| REVERB_ON_OFF @ 0x00 | Same as Delay; verify with hardware |

---

## 10. Program Part (0x18 00 20–23 00)

**Guide:** Receive Channel (0x00), Part Switch (0x01), Tone Bank MSB/LSB (0x06–0x07), Program Number (0x08), Part Level (0x09), Pan (0x0A), Coarse/Fine Tune (0x0B–0x0C), Mono/Poly, Legato, Pitch Bend Range, Portamento, Cutoff/Resonance/Envelope offsets, Octave Shift, Velocity Sens, Delay/Reverb Send, Output Assign, Scale Tune, Receive switches (0x3D–0x46), etc. Total size 0x4C.

**JDXI Editor:** `PartMessage` in `roland.py` uses hardcoded `lsb` values (0x0B, 0x0C, 0x11, 0x13–0x1A, 0x1B, 0x1C) for conversion. No `PartParam` enum or `ParameterSpec` definitions.

| Gap | Action |
|-----|--------|
| PartParam class | Add `PartParam` with all guide parameters for consistency and maintainability |
| Part SysEx request | Verify Program Part is requested and parsed correctly |

---

## 11. Program Zone (0x18 00 30–33 00)

**Guide:** 0x00–0x02 reserve, 0x03 Arpeggio Switch, 0x04–0x0D reserve, 0x0E–0x18 reserve, 0x19 Zone Octave Shift, 0x1A–0x22 reserve. Total 0x23.

**JDXI Editor:** `ProgramZoneParam` — ARPEGGIO_SWITCH (0x03), ZONAL_OCTAVE_SHIFT (0x19). Other zone params not implemented.

| Gap | Action |
|-----|--------|
| Zone reserve blocks | Low priority; guide marks most as reserve |

---

## 12. Program Controller (0x18 00 40 00)

**Guide:** Arpeggio Grid (0x01), Duration (0x02), Switch (0x03), Style (0x05), Motif (0x06), Octave Range (0x07), Accent Rate (0x09), Velocity (0x0A). Total 0x0C.

**JDXI Editor:** `ArpeggioParam` / controller params — ARPEGGIO_GRID, ARPEGGIO_DURATION, ARPEGGIO_SWITCH, ARPEGGIO_STYLE, ARPEGGIO_MOTIF, ARPEGGIO_OCTAVE_RANGE, ARPEGGIO_ACCENT_RATE, ARPEGGIO_VELOCITY. ✓

---

## 13. SuperNATURAL Synth Tone (Digital)

**Common (0x00–0x40):** Tone Name 1–12, Tone Level, Portamento, Mono, Octave Shift, Pitch Bend Range, Partial switches, RING, Unison, Analog Feel, Wave Shape, etc.

**Partial (0x00–0x3D):** OSC, Filter, AMP, LFO, Modulation LFO, Aftertouch, Wave Gain/Number, HPF, Super Saw Detune, etc.

**Modify (0x00–0x25):** Attack/Release Interval Sens, Envelope Loop, Chromatic Portamento, etc.

**JDXI Editor:** `DigitalCommonParam`, `DigitalPartialParam`, `DigitalModifyParam` — comprehensive coverage. ✓

---

## 14. Analog Synth Tone (0x19 40 00 00)

**Guide:** Tone Name 1–12, LFO (Shape, Rate, Fade, Tempo Sync, Key Trigger, Depths), OSC (Waveform, Pitch, Pulse Width, Env), Filter, AMP, Portamento, Legato, Octave Shift, Pitch Bend, LFO Modulation Controls. Total 0x40.

**JDXI Editor:** `AnalogParam` — full coverage. ✓

---

## 15. Drum Kit

**Common (0x00–0x12):** Kit Name 1–12, Kit Level.

**Partial (0x00–0x143):** Partial Name, Assign Type, Mute Group, Level, Tune, Pan, Env Mode, Output, WMT1–4, Pitch Env, TVF, TVA, One Shot, Relative Level.

**JDXI Editor:** `DrumCommonParam`, `DrumPartialParam` — comprehensive. ✓

---

## 16. Control Changes (Guide lines 1–54, 1367–1484)

**Guide CC# / NRPN:**
- Effect 1 (14), Effect 2 (15), Delay (13), Reverb (12), Vocoder Level (83)
- Cutoff (102–104), Resonance (105–107), Level (117–119) per partial
- NRPN LSB 3–5 LFO Shape, 16–18 LFO Rate, 15–17 Pitch Depth, 18–20 Filter Depth, 21–23 Amp Depth, 124–126 Envelope
- Drum: NRPN MSB 89/92/64/119 + Note LSB for Cutoff, Resonance, Level, Envelope

**JDXI Editor:** CC/NRPN handling is used for real-time control and parameter dispatch, but there is no central mapping document or enum for all guide CC/NRPN values.

| Gap | Action |
|-----|--------|
| CC/NRPN reference map | Add `doc/control-change-map.md` or equivalent for CC# 12–119 and NRPN LSB values |
| NRPN MSB/LSB routing | Document drum NRPN (MSB + Note) routing if used |

---

## 17. Parameter Address Map Mismatch (PARAMETER_ADDRESS_NAME_MAP)

**Current mapping** (`jdxi_editor/midi/map/parameter_address.py`):
- `EFFECT_1` (0x02) → `ReverbParam` — **wrong**; should be `Effect1Param`
- `EFFECT_2` (0x04) → `Effect2Param` ✓
- `DELAY` (0x06) — **missing** from map; should add `DelayParam`
- `REVERB` (0x08) — **missing** from map; should add `ReverbParam`

| Entry | Current | Should be |
|-------|---------|-----------|
| EFFECT_1 | ReverbParam | Effect1Param |
| EFFECT_2 | Effect2Param | Effect2Param ✓ |
| DELAY | (not in map) | DelayParam |
| REVERB | (not in map) | ReverbParam |

---

## Perl Implementation Comparison

### Perl Areas Not in Gap Analysis

The Perl implementation (`JDXidata.pm`) does **not** define:
- **Setup** (0x01 00 00 00) — Program BS MSB/LSB, PC
- **System Common** (0x02 00 00 00)
- **System Controller** (0x02 00 03 00)
- **Program Common** (0x18 00 00 00) — name, level, tempo, vocal effect
- **Program Part** (0x18 00 20–23 00)
- **Program Zone** (0x18 00 30–33 00)

Perl focuses on: **Effects** (EFX1, EFX2, Delay, Reverb), **Vocal FX**, **Arpeggio**, **Digital Synth** (SN1, SN2), **Analog** (AN), **Drum Kit** (DR).

### Perl Lookup Tables (JDXidata.pm) — JDXI Editor Adoption

| Perl table | Purpose | JDXI Editor |
|------------|---------|-------------|
| `@rev_type` | Reverb types (Room 1/2, Stage 1/2, Hall 1/2) | `EffectsData.rev_type` ✓ |
| `@hf_damp` | HF damp options (200Hz … BYPASS) | `EffectsData.hf_damp` ✓ |
| `@dly_notes` | Delay/Flanger note sync (22 entries) | `flanger_notes` / `delay_notes` ✓ |
| `@coarse_tune` | Note names C-1 … G9 | `coarse_tune` ✓ |
| `@ratio` | Compressor ratios | `compression_ratios` ✓ |
| `@comp_att`, `@comp_rel` | Compressor attack/release | `compression_attack_times`, `compression_release_times` ✓ |
| `@fx1_type`, `@fx2_type` | Effect types | Effect type combos ✓ |
| `@arp_grid`, `@arp_duration`, `@arp_motif` | Arpeggio options | ArpeggioParam options ✓ |
| `@vc_hpf` | Vocoder HPF | VocalFXParam VOCODER_MIC_HPF ✓ |
| `@ap_key` | Auto Pitch keys | Auto Pitch key combo ✓ |

### Perl vs Guide: Effects Parameter Alignment

Perl and the Guide agree on:
- **Delay:** 0x00 (Perl: On/Off), 0x01 Level, 0x03 Reverb Send, 0x04+ Params. Perl uses On/Off at 0x00; Guide marks 0x00 reserve. **Perl supports On/Off at 0x00** — suggests JDXI Editor `DELAY_ON_OFF` may be correct despite Guide.
- **Reverb:** 0x00 (Perl: On/Off), 0x01 Level, 0x03 Type, 0x07 Time, 0x0B HF Damp. Perl uses On/Off at 0x00; Guide marks 0x00 reserve. **Perl supports On/Off at 0x00** — same conclusion for `REVERB_ON_OFF`.
- **Effect 1/2:** Type 0x00, Level 0x01, Delay/Reverb Send 0x02–0x03, Output Assign 0x04, Params 0x11+ (4-byte). Full alignment.

### Perl transf64 / transf4 — Bipolar and 4-Byte Params

Perl uses `transf64` (value + 64 for bipolar) and `transf4` (4-byte signed) for parameter conversion. JDXI Editor uses `Midi.value.min.SIGNED_SIXTEEN_BIT` (+32768) for 4-byte params and explicit `convert_to_midi` for bipolar (e.g. Pan, Gender). Logic is equivalent.

### Perl inittone — Default Patch Data

Perl defines `inittone` byte strings for each area (AN, SN1/2, DR, FX, ARP, VFX). JDXI Editor does not ship default patch data; it relies on hardware or user load.

---

## Priority Recommendations

1. **High:** Fix Program Common address mismatches (PROGRAM_LEVEL 0x10 vs 0x16, PROGRAM_TEMPO 0x11 vs 0x17–0x1A) — validate with hardware. ✅ **Done** — aligned to midi_parameters.txt (0x16, 0x17).
2. **High:** Fix PARAMETER_ADDRESS_NAME_MAP EFFECT_1 → Effect1Param. ✅ **Done** — EFFECT_1→Effect1Param, added DELAY→DelayParam, REVERB→ReverbParam.
3. **Medium:** Add PartParam enum for Program Part parameters. ✅ **Done** — `jdxi_editor/midi/data/parameter/program/part.py`.
4. **Low:** Add Setup, System Controller parameter support if needed. ✅ **Done** — `jdxi_editor/midi/data/parameter/system/controller.py` (Setup already in `areas/setup.py`).
5. **Low:** Document Control Change / NRPN map for reference. ✅ **Done** — `doc/control-change-map.md`.
