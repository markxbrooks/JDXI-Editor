# Vocal Effects Migration Plan

A phased plan to bring the JDXI Editor Vocal Effects section to feature parity with the Perl `jdxi_manager.pl` implementation and the JD-Xi Parameter Guide.

**Reference:** `doc/perl/jdxi_manager.pl`, `doc/perl/JDXidata.pm` (when available)  
**Authoritative source:** `doc/midi_parameters.txt` (JD-Xi Parameter Guide)

---

## Current State Summary

### JDXI Editor Implementation

| Component | Location | Status |
|-----------|----------|--------|
| VocalFXEditor | `jdxi_editor/ui/editors/effects/vocal.py` | 4 tabs: Common, Vocal FX, Mixer, Auto Pitch |
| VocalFXParam | `jdxi_editor/midi/data/parameter/vocal_fx.py` | 0x00–0x13 (Program Vocal Effect) |
| Vocal enums | `jdxi_editor/midi/data/vocal_effects/vocal.py` | VocoderEnvelope, VocoderHPF, VocalAutoPitchType, etc. |
| Program Common | `jdxi_editor/midi/data/parameter/program/common.py` | VOCAL_EFFECT, VOCAL_EFFECT_NUMBER, VOCAL_EFFECT_PART, AUTO_NOTE_SWITCH |

### JD-Xi Parameter Guide (midi_parameters.txt)

**Program Common** (offsets 0x1C–0x1E):
- 0x1C: Vocal Effect (0–2) OFF, VOCODER, AUTO-PITCH
- 0x1D: Vocal Effect Part (0–1) 1–2
- 0x1E: Auto Note Switch (0–1) OFF, ON

**Program Vocal Effect** (offset 00 01 00, params 0x00–0x13):
- 0x00: Level (0–127)
- 0x01: Pan (0–127) L64–63R
- 0x02: Delay Send Level
- 0x03: Reverb Send Level
- 0x04: Output Assign (0–4) EFX1, EFX2, DLY, REV, DIR
- 0x05: Auto Pitch Switch
- 0x06: Auto Pitch Type (0–3) SOFT, HARD, ELECTRIC1, ELECTRIC2
- 0x07: Auto Pitch Scale (0–1) CHROMATIC, Maj(Min)
- 0x08: Auto Pitch Key (0–23)
- 0x09: Auto Pitch Note (0–11)
- 0x0A: Auto Pitch Gender (0–20) -10 to +10
- 0x0B: Auto Pitch Octave (0–2) -1 to +1
- 0x0C: Auto Pitch Balance (0–100) D100:0W – D0:100W
- 0x0D: Vocoder Switch
- 0x0E: Vocoder Envelope (0–2) SHARP, SOFT, LONG
- 0x0F: Vocoder Level (0–127)
- 0x10: Vocoder Mic Sens
- 0x11: Vocoder Synth Level
- 0x12: Vocoder Mic Mix Level
- 0x13: Vocoder Mic HPF (0–13) BYPASS, 1000–16000 Hz

---

## Gap Analysis

### Parameter Coverage

| Parameter | JD-Xi addr | JDXI Editor | Notes |
|-----------|------------|-------------|-------|
| **Program Common** | | | |
| Vocal Effect | 0x1C | ✓ ProgramCommonParam.VOCAL_EFFECT (0x16) | Verify address: 0x16 vs 0x1C |
| Vocal Effect Part | 0x1D | ✓ ProgramCommonParam.VOCAL_EFFECT_PART | |
| Auto Note Switch | 0x1E | ✓ ProgramCommonParam.AUTO_NOTE_SWITCH | |
| **Program Vocal Effect** | | | |
| Level | 0x00 | ✓ VocalFXParam.LEVEL | |
| Pan | 0x01 | ✓ VocalFXParam.PAN | |
| Delay Send | 0x02 | ✓ VocalFXParam.DELAY_SEND_LEVEL | |
| Reverb Send | 0x03 | ✓ VocalFXParam.REVERB_SEND_LEVEL | |
| Output Assign | 0x04 | ✓ VocalFXParam.OUTPUT_ASSIGN | |
| Auto Pitch Switch | 0x05 | ✓ VocalFXParam.AUTO_PITCH_SWITCH | |
| Auto Pitch Type | 0x06 | ✓ VocalFXParam.AUTO_PITCH_TYPE | |
| Auto Pitch Scale | 0x07 | ✓ VocalFXParam.AUTO_PITCH_SCALE | |
| Auto Pitch Key | 0x08 | ✓ VocalFXParam.AUTO_PITCH_KEY | |
| Auto Pitch Note | 0x09 | ✓ VocalFXParam.AUTO_PITCH_NOTE | |
| Auto Pitch Gender | 0x0A | ✓ VocalFXParam.AUTO_PITCH_GENDER | |
| Auto Pitch Octave | 0x0B | ✓ VocalFXParam.AUTO_PITCH_OCTAVE | |
| Auto Pitch Balance | 0x0C | ✓ VocalFXParam.AUTO_PITCH_BALANCE | |
| Vocoder Switch | 0x0D | ✓ VocalFXParam.VOCODER_SWITCH | |
| Vocoder Envelope | 0x0E | ✓ VocalFXParam.VOCODER_ENVELOPE | |
| Vocoder Level | 0x0F | ✓ VocalFXParam.VOCODER_LEVEL | |
| Vocoder Mic Sens | 0x10 | ✓ VocalFXParam.VOCODER_MIC_SENS | |
| Vocoder Synth Level | 0x11 | ✓ VocalFXParam.VOCODER_SYNTH_LEVEL | |
| Vocoder Mic Mix | 0x12 | ✓ VocalFXParam.VOCODER_MIC_MIX | |
| Vocoder Mic HPF | 0x13 | ✓ VocalFXParam.VOCODER_MIC_HPF | |

### Architecture / UX Gaps (vs. Effects Editor & Perl)

| Feature | Perl / Effects | Vocal FX | Gap |
|---------|----------------|----------|-----|
| Polymorphic UI | Dynamic frame per effect type | Static tabs; all params visible | No show/hide per Vocal Effect (OFF/VOCODER/AUTO-PITCH) |
| Layout | 2-column grid in tabs | Single-column form per tab | Could use 2-col (Vocoder \| Auto Pitch) when both relevant |
| SysEx request on show | data_request() in showEvent | Not present in VocalFXEditor | May not sync from hardware on open |
| MIDI send on change | send_midi_parameter | Inherited from BasicEditor | Verify wiring |
| Tooltips | EffectsData.effect_tooltips | None | Missing |
| Consistent labeling | "Balance [dry->wet]" | "D/W Balance" | Minor |
| Tab structure | Effects 1&2 \| Delay&Reverb | Common \| Vocal FX \| Mixer \| Auto Pitch | Different organization; Perl may group differently |

### Data / Lookup Gaps

| Item | JD-Xi / Perl | JDXI Editor | Action |
|------|--------------|-------------|--------|
| Output Assign labels | EFX1, EFX2, DLY, REV, DIR | VocalOutputAssign enum | ✓ Present |
| Vocoder Envelope | SHARP, SOFT, LONG | VocoderEnvelope enum | ✓ Present |
| Vocoder HPF | BYPASS, 1000–16000 Hz | VocoderHPF enum | ✓ Present |
| Auto Pitch Type | SOFT, HARD, ELECTRIC1, ELECTRIC2 | VocalAutoPitchType | ✓ Present |
| Auto Pitch Key | 24 keys (C…Bm) | VocalAutoPitchKey | ✓ Present |
| Auto Pitch Note | 12 notes | VocalAutoPitchNote | ✓ Present |
| Balance label | D100:0W – D0:100W | "D/W Balance" | Consider "Balance [dry->wet]" for consistency |

### Potential Issues

1. **VOCAL_EFFECT address**: ProgramCommonParam.VOCAL_EFFECT uses 0x16; JD-Xi lists 0x1C. Confirm base offset for Program Common.
2. **VOCAL_EFFECT_NUMBER**: Present in Common tab; JD-Xi Parameter Guide does not list "Effect Number" in Program Vocal Effect. May be Program Common or a different area.
3. **Vocal Effect Part**: VOCAL_EFFECT_PART (Part 1/2) is in Program Common; not clearly exposed in Vocal FX UI.
4. **Duplicate Vocoder Switch**: Common tab has "Effect Part" (VOCODER_SWITCH); Vocal FX tab has "Vocoder" (same param). Clarify or consolidate.

---

## Phased Upgrade Plan

### Phase 0: Preparation & Validation (1–2 days) ✅

**Goal:** Establish baseline and validate addresses.

**Tasks:**
1. **SysEx address audit** ✅
   - Map Program Common offsets (0x1C, 0x1D, 0x1E) to ProgramCommonParam
   - Map Program Vocal Effect (00 01 00) offsets 0x00–0x13 to VocalFXParam
   - Document any mismatches
   - **Deliverable:** `doc/vocal-effects-sysex-address-map.md`

2. **Gap analysis document** ✅
   - Finalize checklist (this document)
   - Note VOCAL_EFFECT_NUMBER source and usage

3. **Test harness** ✅
   - Add `tests/test_vocal_effects_editor.py`
   - Baseline: init, tabs, key controls registered, send_midi_parameter
   - Run: `uv run pytest tests/test_vocal_effects_editor.py -v` (or `python -m unittest tests.test_vocal_effects_editor -v` with venv active)

**Deliverables:** `doc/vocal-effects-sysex-address-map.md` ✅, test baseline ✅

---

### Phase 1: Data Layer & Address Verification (1–2 days) ✅

**Goal:** Align parameter definitions with JD-Xi Parameter Guide.

**Tasks:**
1. **Verify Program Common addresses** ✅
   - VOCAL_EFFECT: 0x16 → 0x1C (per JD-Xi guide)
   - VOCAL_EFFECT_NUMBER: 0x1C → 0x1B (placeholder; undocumented in guide)
   - apply_lmb_offset: ProgramCommonParam uses LMB=COMMON for correct routing

2. **VocalFXParam verification** ✅
   - Pan, Auto Pitch Gender, Auto Pitch Octave: convert_to_midi / convert_from_midi verified
   - convert_from_display delegates to convert_to_midi

3. **Lookup tables** ✅
   - VocalEffectsData with vocal_effect_tooltips
   - Balance label: "Balance [dry→wet]"
   - _apply_vocal_effect_tooltips in VocalFXEditor

**Deliverables:** Verified parameter specs ✅, VocalEffectsData ✅

---

### Phase 2: SysEx Sync & MIDI Wiring (1–2 days) ✅

**Goal:** Ensure Vocal FX editor syncs from and sends to hardware.

**Tasks:**
1. **data_request on show** ✅
   - showEvent override with data_request()
   - midi_requests = [PROGRAM_COMMON, PROGRAM_VOCAL_EFFECT]
   - MidiRequests.PROGRAM_VOCAL_EFFECT added (address 01 00 00, size 0x18)

2. **SysEx dispatcher** ✅
   - midi_sysex_json.connect(_dispatch_sysex_to_area)
   - _dispatch_sysex_to_area handles COMMON and VOCAL_EFFECT
   - JDXiMapSynthTone: 0x01 → VOCAL_EFFECT
   - VocalFXParam.get_by_name added

3. **MIDI send on change** ✅
   - Controls use parent _on_parameter_changed → send_midi_parameter
   - apply_lmb_offset routes ProgramCommonParam to LMB=COMMON

**Deliverables:** Sync on open ✅, bidirectional MIDI ✅

---

### Phase 3: Polymorphic UI (2–3 days) ✅

**Goal:** Show only relevant controls based on Vocal Effect type (OFF / VOCODER / AUTO-PITCH).

**Tasks:**
1. **Effect-type-driven layout** ✅
   - OFF: Minimal placeholder (label)
   - VOCODER: Vocoder settings (Envelope, HPF, Level, Mic Sens, Synth Level, Mic Mix)
   - AUTO-PITCH: Auto Pitch settings (Type, Scale, Key, Note, Gender, Octave, Balance)

2. **Implementation** ✅
   - QStackedWidget (like Effects 1/2) with 3 pages: OFF, Vocoder, Auto Pitch
   - Tab "Vocoder & Auto Pitch" replaces separate Vocal FX and Auto Pitch tabs
   - Vocal Effect combo drives stack index

3. **Common controls** ✅
   - Vocal Effect (OFF/VOCODER/AUTO-PITCH) always visible
   - Effect Part: VOCAL_EFFECT_PART (Part 1/Part 2) — fixed from VOCODER_SWITCH
   - Auto Note Switch in Common
   - Mixer tab (Level, Pan, Delay/Reverb send, Output Assign) unchanged

**Deliverables:** Polymorphic Vocal FX section ✅

---

### Phase 4: Layout & UX (1–2 days)

**Goal:** Improve layout and match Effects editor patterns.

**Tasks:**
1. **Layout options**
   - Evaluate 2-column layout: Vocoder | Auto Pitch (when both applicable)
   - Or: Tab "Vocoder & Auto Pitch" with 2-col grid (like Effects 1&2, Delay&Reverb)

2. **Tab structure**
   - Consider: "Common" | "Vocoder & Auto Pitch" (2 tabs) vs current 4 tabs
   - Or keep 4 tabs but apply 2-col within tabs where it helps

3. **Polish**
   - Tooltips for key controls
   - Consistent labeling (Balance [dry->wet])
   - Remove duplicate Vocoder Switch if redundant

**Deliverables:** Updated layout, tooltips, consistent labels

---

### Phase 5: Documentation & Cleanup (1 day)

**Goal:** Update docs and remove obsolete code.

**Tasks:**
1. **Update doc/vocal_effects.rst**
   - Add "JD-Xi Implementation" section (like effects.rst)
   - Document polymorphic behavior, parameter list

2. **Code cleanup**
   - Remove duplicate controls or dead code
   - Consolidate Common vs Vocal FX tab logic if needed

3. **Changelog**
   - Add Vocal Effects improvements to CHANGELOG.md

**Deliverables:** Updated docs, changelog entry

---

## Summary Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| 0. Preparation | 1–2 days | 1–2 days |
| 1. Data Layer | 1–2 days | 2–4 days |
| 2. SysEx Sync | 1–2 days | 3–6 days |
| 3. Polymorphic UI | 2–3 days | 5–9 days |
| 4. Layout & UX | 1–2 days | 6–11 days |
| 5. Documentation | 1 day | 7–12 days |

**Total estimate:** ~1.5–2.5 weeks

---

## Risk Mitigation

- **Address drift:** Phase 0 audit reduces risk of wrong parameter mapping.
- **Regression:** Run tests after each phase; manual spot-checks on hardware.
- **Scope creep:** Phases 4–5 can be deferred; Phases 1–3 deliver most value.

---

## Optional / Future Work

- Vocal Effect Number / preset browsing (if supported by JD-Xi)
- Visual routing diagram (Mic → Vocoder → Output)
- MIDI Learn for vocal parameters
