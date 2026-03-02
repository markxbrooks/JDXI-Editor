# Patch Saving Gap Analysis: JDXI Editor vs Perl

Compares patch saving and loading in the JDXI Editor (Python) with the Perl `jdxi_manager.pl` implementation and Roland JD-Xi standard practices.

**Reference:** Roland JD-Xi MIDI Implementation Guide, `doc/perl/jdxi_manager.pl`, `doc/perl/JDXidata.pm`.

---

## Executive Summary

| Aspect | JDXI Editor | Perl (Confirmed) | Gap |
|--------|-------------|------------------|-----|
| **Save format** | JSON bundles (.jsz, .msz), **.syx** | Binary .syx (DT1 concatenated) | .syx export **implemented** |
| **Save source** | UI control values only | UI control values (`WritePatData`) | Same; both save from UI |
| **Load format** | .json, .jsz, .msz, **.syx** | .syx (validates `filelen`, per-section) | .syx load **wired** |
| **Dump-from-synth** | None | "Read from" → RQ1 → DT1 → UI | No RQ1-based load-then-save flow |
| **Compatibility** | JDXI-specific JSON | Per-editor .syx, Perl layout | No cross-editor exchange |

---

## JDXI Editor Patch Saving — Current Behavior

### Save Flow

| Step | Component | Behavior |
|------|-----------|----------|
| 1 | `PatchManager` (save_mode=True) | User selects path via file dialog |
| 2 | For each editor in `self.editors` | Skips: `PatternSequenceEditor`, `ProgramEditor`, `MidiFilePlayer` |
| 3 | `JDXiJSONComposer.process_editor()` | Writes JSON for editors with `address` and `get_controls_as_dict` |
| 4 | Temp folder | `jdxi_tone_data_{address_hex}.json` per section |
| 5 | Zip | Bundles JSON (+ optional `song.mid`) → `.jsz` or `.msz` |

**Key files:**
- `jdxi_editor/ui/windows/patch/manager.py` — PatchManager, save/load UI
- `jdxi_editor/midi/sysex/json_composer.py` — JDXiJSONComposer, JSON generation

### Save Source: UI State Only

The JDXI Editor **always saves from the current UI control values** (`get_controls_as_dict()`), not from data received from the synth.

- If a slider was never updated from the synth (e.g. no `midi_requests` or no SysEx received), the saved value may not match the hardware.
- There is no “request current patch from synth” step before save.

### Output Formats

| Extension | Content | Notes |
|-----------|---------|-------|
| `.jsz` | Zip of JSON files | Patch bundle only |
| `.msz` | Zip of JSON + `song.mid` | Music bundle (patch + MIDI) |
| `.syx` | **Supported** (load + save) | PatchManager saves as raw SysEx |

### Editors Included in Save

| Editor Type | Included | Notes |
|-------------|----------|-------|
| DigitalSynthEditor | Yes | Common + Modify sections, separate JSON |
| DrumCommonEditor | Yes | Common + Partial sections |
| AnalogSynthEditor | Yes | Single JSON |
| EffectsCommonEditor | Yes | Effect1, Effect2, Delay, Reverb |
| VocalFXEditor | Yes | Single JSON |
| ArpeggioEditor | Yes | If has `address` + `get_controls_as_dict` |
| PatternSequenceEditor | No | Explicitly skipped |
| ProgramEditor | No | Explicitly skipped |
| MidiFilePlayer | No | MIDI file saved separately in .msz |

---

## JDXI Editor Patch Loading — Current Behavior

### Load Flow

| Step | Component | Behavior |
|------|-----------|----------|
| 1 | `PatchManager` (save_mode=False) | User selects file |
| 2 | `midi_helper.load_patch(file_path)` | Dispatches by extension |
| 3 | `.jsz` / `.msz` | Zip → iterate `.json` files → `send_json_patch_to_instrument` |
| 4 | Single `.json` | Read file → `send_json_patch_to_instrument` |
| 5 | `send_json_patch_to_instrument` | Parse JSON, map to param classes, send DT1 SysEx |

**Key files:**
- `jdxi_editor/midi/io/helper.py` — `load_patch()`, `send_json_patch_to_instrument()`, `load_sysx_patch()`

### .syx Handling — Implemented

| Item | Status |
|------|--------|
| File dialog filter | Shows `(*.syx)` for Save and Load |
| `load_sysx_patch()` | Exists in `MidiIOHelper` |
| Called by PatchManager | **Yes** — `load_patch` detects `.syx` and delegates to `load_sysx_patch` |
| Load .syx via PatchManager | **Works** — binary read, split by F0…F7, each message sent via `send_raw_message` |

`load_patch` routes `.syx` to `load_sysx_patch`, which reads binary, splits concatenated SysEx messages, and sends each F0…F7 block to the instrument.

---

## Perl (jdxi_manager.pl) — Confirmed Behavior

Direct analysis of `doc/perl/jdxi_manager.pl` and `doc/perl/JDXidata.pm`.

### Perl Save Format and Flow

| Aspect | Perl Implementation | JDXI Editor |
|--------|---------------------|-------------|
| **Save format** | `.syx` (binary SysEx), or editor-specific hex (`.as`, `.ds`, `.dk`) | `.jsz`, `.msz` (JSON bundles only) |
| **Save source** | **UI control values** (`WritePatData` from `$$rf_hash{data}`) | UI control values |
| **Save subroutine** | `saveSub()` — iterates `addr[]`, `WritePatData()`, builds DT1 messages | `JDXiJSONComposer.process_editor()` |
| **Per-editor files** | Each editor saves its own `.syx` (Analog, Digital 1/2, Drums, FX, ARP, Vocal FX) | Single bundle with all editor JSON |
| **DT1 structure** | `F0 41 xx 00 00 00 0E 12` + addr (4B) + data + checksum + `F7` | Same DT1 format when sending |

### Perl Load Format and Flow

| Aspect | Perl | JDXI Editor |
|--------|------|-------------|
| **File types** | `.syx`, `.SYX` (+ `.as`/`.ds`/`.dk` when `okedext` set) | `.jsz`, `.msz`, `.json` |
| **Validation** | Exact `filelen` match; per-section `ValidatePatData` against `pattern` regex | JSON parse; no binary validation |
| **Split logic** | `$tmpsyx[$n] = substr($sysex, $start, datalen+14)` per section | Per-JSON-file in zip |
| **Populate UI** | `ReadPatData(\substr($tmpsyx[$n],12, datalen), $rf_hash, $n)` | `send_json_patch_to_instrument` → DT1 send |

### Perl Dump-from-Synth ("Read from")

| Feature | Perl | JDXI Editor |
|---------|------|-------------|
| **Button** | "Read from" → `SysexPatRcve($rf_hash)` | None |
| **Flow** | RQ1 (0x11) per `addr[]`+`rqlen[]` → `SyxReceive()` → validate → `ReadPatData()` | RQ1 used only for editor `data_request()` on show |
| **Result** | Populates UI from synth; clears `modified`; does not auto-save to file | Same RQ1 for display; never used as save source |

### Perl "Dump to" (Send to Synth)

| Feature | Perl | JDXI Editor |
|---------|------|-------------|
| **Button** | "Dump to" → `SysexPatSend($rf_hash)` | Load Patch sends to instrument |
| **Flow** | Build DT1 from UI (`WritePatData`), send via MIDI | `send_json_patch_to_instrument` on load |

### Perl Editor File Layouts (from JDXidata.pm)

| Editor | addr count | filelen | Sections (key) | Example addr |
|--------|------------|---------|----------------|---------------|
| **Analog** | 1 | 78 | AN tone | `19 42 00 00` |
| **Digital 1** | 5 | 354 | COM, P1–P3, MOD | `19 01 00 00`, `19 01 20 00`, … |
| **Digital 2** | 5 | 354 | COM, P1–P3, MOD | `19 21 00 00`, … |
| **Drums** | 39 | 7974 | COM + 38 partials | `19 70 00 00`, `19 70 2E 00`, … |
| **Effects** | 4 | 545 | EFX1, EFX2, Delay, Reverb | `18 00 02 00`–`18 00 08 00` |
| **Vocal FX** | 1 | 38 | Vocal FX block | `18 00 01 00` |
| **Arpeggio** | 1 | 26 | Program Controller | `18 00 40 00` |

### Perl inittone (Default Patch Data)

Each editor has `inittone` byte strings for "Reset to default" / "Generate random" flows. Example (VFX):  
`"\x7F\x40\x00\x00\x02\x01\x00\x01\x00\x00\x0A\x01\x64\x01\x00\x00\x50\x50\x00\x00\x40\x01\x40\x40"` (24 bytes).

### Roland Standard Patch Dump

1. **RQ1** (Command 0x11): Host requests data for an address block.
2. **DT1** (Command 0x12): Synth responds with parameter data.
3. **Save:** Host writes DT1 messages (or concatenated SysEx) to `.syx`.

JDXI Editor uses RQ1 for editor `midi_requests` (to populate sliders) but does **not** use this data as the source for a “Save from synth” operation.

---

## Gap Summary

### 1. No Dump-from-Synth Save

| Gap | Description | Priority |
|-----|-------------|----------|
| Save from synth | No “Request current patch from JD-Xi, then save” flow | Medium |

**Perl:** Has "Read from" button — RQ1 request → DT1 response → `ReadPatData` populates UI. Does not auto-save to file; user must Save after Read.

**JDXI Editor:** RQ1 used only for editor `data_request()` on show. No "Read from synth, then save" workflow.

**Impact:** Saved patches reflect UI state, which may lag behind or differ from hardware if:
- Editors were not focused when data was requested
- SysEx dispatch failed or was incomplete
- User edited on hardware without updating the editor

### 2. ~~No .syx Export~~ — Fixed

| Gap | Description | Status |
|-----|-------------|--------|
| Export to .syx | `save_patch_as_syx` converts editor JSON → SysEx bytes, writes to `.syx` | **Fixed** |

**Implementation:** PatchManager detects `.syx` on save; `MidiIOHelper.save_patch_as_syx` reads JSON from temp folder, calls `json_patch_to_sysex_bytes` per file, concatenates, writes. File dialog already includes `(*.syx)`.

### 3. ~~.syx Load Not Wired~~ — Fixed

| Gap | Description | Status |
|-----|-------------|--------|
| load_sysx_patch not used | `load_patch` now detects `.syx` and delegates to `load_sysx_patch` | **Fixed** |

### 4. Program and Pattern Excluded from Save

| Gap | Description | Priority |
|-----|-------------|----------|
| ProgramEditor skipped | Program (bank/program) data not in patch bundle | Low |
| PatternSequenceEditor skipped | Pattern/sequence data not in patch bundle | Low |

**Perl:** Uses separate editor windows (Analog, Digital 1/2, Drums, FX, Arpeggio, Vocal FX). No "Program" or "Pattern" editor in `@Part` — Perl does not save program-list or sequencer data either.

**Impact:** May be intentional (Program = program list metadata; Pattern = sequencer data). Perl confirms same scope.

### 5. No Perl Interoperability

| Gap | Description | Priority |
|-----|-------------|----------|
| Format mismatch | Perl: `.syx` (binary DT1 concatenated); JDXI: `.jsz` (JSON zip) | Low |

**Perl .syx layout:** Per-editor file with `filelen` bytes. Sections concatenated: each = 14-byte header (F0 41 xx 00 00 00 0E 12 + 4-byte addr) + `datalen` bytes + checksum + F7. Total per section = `datalen + 14`.

**JDXI → Perl:** Would need to convert JSON → DT1 byte layout matching Perl `addr[]`/`datalen[]` order. Perl expects exact `filelen`; per-editor files only.

**Perl → JDXI:** Would need to parse .syx, split by known lengths, map bytes to JSON param names, then use existing load path. Doable with JDXidata.pm layout.

**Impact:** Cannot load Perl-saved patches in JDXI Editor (or vice versa) without a conversion layer.

### 6. No Default (inittone) Data

| Gap | Description | Priority |
|-----|-------------|----------|
| inittone | Perl has default patch byte strings per area | Low |

**Impact:** JDXI Editor depends on hardware or user load; no built‑in “reset to default” patch data.

---

## Recommendations

### High Priority

1. ~~**Wire .syx load**~~ — **Done**
   - `load_patch` now detects `.syx` (case-insensitive) and delegates to `load_sysx_patch`.
   - `load_sysx_patch` splits concatenated SysEx messages (F0…F7) and sends each to the instrument.

### Medium Priority

2. ~~**Add .syx export**~~ — **Done**
   - PatchManager: when save path ends with `.syx`, calls `midi_helper.save_patch_as_syx`.
   - `save_patch_as_syx`: reads JSON from temp folder, converts via `json_patch_to_sysex_bytes`, writes concatenated SysEx bytes.
   - File dialog already shows `(*.syx)` for Save and Load.

3. **Dump-from-synth save (optional)**
   - New action: “Save current patch from synth”
   - Send RQ1 for all relevant areas (Program Common, Digital 1/2, Analog, Drum, Effects, etc.).
   - Collect DT1 responses.
   - Save collected SysEx as `.syx` or convert to JSON and save as `.jsz`.

### Low Priority

4. **Document Program/Pattern save policy**
   - Clarify whether Program and Pattern should be part of patch bundles.
   - If yes, add support; if no, document rationale.

5. **Perl .syx compatibility**
   - Perl format is confirmed: binary DT1 concatenated, per-editor files, `filelen`/`addr[]`/`datalen[]` in JDXidata.pm.
   - Add loader: parse .syx, split by known lengths (see Perl Editor File Layouts table), map to JSON, use `send_json_patch_to_instrument`.
   - Add exporter: from `get_controls_as_dict`, build DT1 per editor, write binary .syx matching Perl layout.

---

## File Reference

| File | Role |
|------|------|
| `jdxi_editor/ui/windows/patch/manager.py` | PatchManager UI, save/load orchestration |
| `jdxi_editor/midi/sysex/json_composer.py` | JSON composition from editors |
| `jdxi_editor/midi/io/helper.py` | `load_patch`, `load_sysx_patch`, `send_json_patch_to_instrument` |
| `jdxi_editor/midi/sysex/request/` | RQ1 request definitions |
| `doc/perl/jdxi_manager.pl` | Perl editor |
| `doc/perl/JDXidata.pm` | Perl data/address definitions |

---

## Related Docs

- `doc/arpeggiator-sysex-gap-analysis.md` — Arpeggiator SysEx flow
- `doc/effects-migration-plan.md` — Effects parity vs Perl
- `doc/midi-parameters-gap-analysis.md` — Parameter mapping, inittone
- `doc/arbitrary-cc-pc-sender-plan.md` — CC/PC sender (separate feature)
