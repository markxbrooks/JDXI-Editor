# Effects Editor Migration Plan

A phased plan to bring the JDXI Editor Effects section to feature parity with the Perl `jdxi_manager.pl` implementation, including polymorphic UI, complete Delay/Reverb parameters, and improved Compressor controls.

**Reference:** `doc/perl/jdxi_manager.pl`, `doc/perl/JDXidata.pm`

---

## Phase 0: Preparation & Validation ✅ COMPLETE

**Goal:** Establish baseline, validate SysEx addresses, and document current gaps.

**Duration:** 1–2 days

### Tasks

1. **SysEx address audit** ✅
   - Map Perl addresses (`180002xx`, `180004xx`, `180006xx`, `180008xx`) to JDXI Editor `JDXiSysExOffset` / `JDXiSysExAddress`
   - Confirm Delay params: 0x00 (on/off), 0x04 (type), 0x08 (time/note), 0x0C (time ms), 0x10 (note), 0x14 (tap %), 0x18 (feedback), 0x1C (HF damp), 0x20 (level)
   - Confirm Reverb params: 0x00 (on/off), 0x03 (type), 0x07 (time), 0x0B (HF damp), 0x0F (level)
   - Document any JD-Xi hardware differences from Perl assumptions

2. **Gap analysis document** ✅
   - Create checklist of missing parameters per effect
   - Note which `EffectsData` / parameter enums need extension

3. **Test harness** ✅
   - Ensure effects editor can be exercised in isolation (unit/integration tests or manual test script)
   - Baseline behavior for current Delay/Reverb/Compressor

**Deliverables**

- `doc/effects-sysex-address-map.md` ✅
- `doc/effects-gap-analysis.md` ✅
- `tests/test_effects_editor.py` ✅ (run: `uv run pytest tests/test_effects_editor.py -v` or `python -m unittest tests.test_effects_editor -v` with venv active)

---

## Phase 1: Data Layer & Lookup Tables ✅ COMPLETE

**Goal:** Add missing lookup tables and parameter definitions so UI can use human-readable options.

**Duration:** 2–3 days

**Dependencies:** Phase 0

### Tasks

1. **Extend `EffectsData`** (`jdxi_editor/ui/editors/effects/data.py`)
   - Add `rev_type`: `["Room 1", "Room 2", "Stage 1", "Stage 2", "Hall 1", "Hall 2"]` (expand if JD-Xi supports Plate/Spring)
   - Add `hf_damp`: 18 options from JDXidata.pm (200Hz … BYPASS)
   - Add `delay_types`: `["SINGLE", "PAN"]`
   - Add `delay_time_note_modes`: `["Time", "Note"]`
   - Add `coarse_tune` or `note_names`: 128 entries for Side Note (C -1 … G 9)
   - Confirm `flanger_notes` matches Perl `dly_notes` (22 entries); alias or unify if needed

2. **Add Delay parameter specs** (`jdxi_editor/midi/data/parameter/effects/effects.py`)
   - `DELAY_ON_OFF` (0x00)
   - `DELAY_TYPE` (0x04): SINGLE / PAN
   - `DELAY_TIME_NOTE_MODE` (0x08): Time / Note
   - `DELAY_NOTE` (0x10): note dropdown
   - `DELAY_TIME_MS` (0x0C): 0–2600
   - `DELAY_TAP_TIME` (0x14): 0–100
   - `DELAY_FEEDBACK` (0x18): 0–98
   - `DELAY_HF_DAMP` (0x1C): HF damp options
   - `DELAY_LEVEL` (0x20): 0–127
   - Update `DelayParam` address mapping if current `DELAY_PARAM_*` differ

3. **Add Reverb parameter specs**
   - `REVERB_ON_OFF` (0x00)
   - `REVERB_TYPE` (0x03): rev_type options
   - `REVERB_TIME` (0x07): 0–127
   - `REVERB_HF_DAMP` (0x0B): hf_damp options
   - `REVERB_LEVEL` (0x0F): 0–127
   - Align with existing `REVERB_PARAM_*` if addresses overlap

4. **Compressor parameter extensions**
   - Add `Effect1Param.EFX1_PARAM_COMPRESSOR_SIDE_CHAIN` (0x25)
   - Add `Effect1Param.EFX1_PARAM_COMPRESSOR_SIDE_SYNC` (0x39)
   - Ensure Side Note (0x2D) uses `coarse_tune` for display

**Deliverables**

- Updated `EffectsData` with new lookup tables ✅
- New/updated `DelayParam`, `ReverbParam`, `Effect1Param` entries ✅
- Param registry / dispatcher updated for new params ✅ (auto-discovered from enum members)

---

## Phase 2: Delay & Reverb UI Completion ✅ COMPLETE

**Goal:** Implement full Delay and Reverb UIs to match Perl.

**Duration:** 3–4 days

**Dependencies:** Phase 1

### Tasks

1. **Delay tab**
   - On/Off switch
   - Type: SINGLE / PAN (combo or switch)
   - Time/Note mode switch
   - Note dropdown (when Note mode)
   - Time [ms] slider (0–2600)
   - Tap Time [%] slider (0–100)
   - Feedback [%] slider (0–98)
   - HF Damp dropdown
   - Reverb send level
   - Level slider
   - Wire all controls to `send_midi_parameter` and SysEx dispatcher

2. **Reverb tab**
   - On/Off switch
   - Type dropdown (Room 1/2, Stage 1/2, Hall 1/2)
   - Time slider
   - HF Damp dropdown
   - Level slider
   - Wire all controls to MIDI/SysEx

3. **SysEx dispatcher**
   - Extend `EffectsSysExDispatcher` / param registry for new Delay and Reverb params
   - Ensure incoming SysEx updates these widgets correctly

4. **Testing**
   - Manual test: change each new control, verify JD-Xi response
   - Load preset with non-default Delay/Reverb; verify UI reflects values

**Deliverables**

- Complete Delay and Reverb tabs ✅
- All new params sending and receiving SysEx ✅ (param registry auto-discovers)

---

## Phase 3: Compressor Enhancements ✅ COMPLETE

**Goal:** Add Side Chain, Side Sync, and note-name dropdown for Compressor.

**Duration:** 1–2 days

**Dependencies:** Phase 1

### Tasks

1. **Side Chain controls**
   - Add Side Chain On/Off switch (0x25)
   - Add Side Sync On/Off switch (0x39)
   - Add to `_build_effect1_layout_spec` when Compressor is selected

2. **Side Note dropdown**
   - Replace generic Side Note control with combo using `coarse_tune` (or `note_names`)
   - Map display index to MIDI value (0–127)

3. **Conditional visibility**
   - Show Side Chain block only when Compressor is selected
   - Ensure `update_efx1_labels` (or equivalent) shows/hides these controls

**Deliverables**

- Compressor with Side Chain, Side Sync, and note-name Side Note ✅

---

## Phase 4: Polymorphic Effect Sections

**Goal:** Replace show/hide with true polymorphic sections that swap UI per effect type.

**Duration:** 4–6 days

**Dependencies:** Phases 1–3 (or at least Phase 1)

### Tasks

1. **Effect section factory**
   - Define `Effect1SectionFactory` (or similar) that returns a widget for each effect type:
     - Thru: empty or minimal
     - Distortion/Fuzz: shared frame (Type, Drive, Presence, Level)
     - Compressor: full frame (Ratio, Threshold, Attack, Release, Level, Side Chain block)
     - Bit Crusher: Rate, Bit, Filter, Level
   - Define `Effect2SectionFactory`:
     - Thru: empty
     - Flanger: Rate/Note, Rate, Note, Depth, Feedback, Manual, Balance, Level
     - Phaser: Rate/Note, Rate, Note, Depth, Resonance, Manual, Level
     - Ring Mod: Frequency, Sens, Balance, Level
     - Slicer: Timing Pattern, Rate [Note], Attack, Trigger Level, Level

2. **Replace static form with dynamic section**
   - Add a container (e.g. `QStackedWidget` or placeholder) for effect-specific content
   - On EFX1/EFX2 type change: clear container, build new section from factory, add to container
   - Preserve control references for `controls` dict and MIDI wiring

3. **Preserve control registration**
   - Ensure new section widgets register with `self.controls` so `_on_parameter_changed` and SysEx dispatch still work
   - Reuse existing slider/switch/combo builders where possible

4. **Layout integration**
   - Integrate polymorphic section into existing tab layout (below common controls)
   - Maintain scrollable layout and styling

**Deliverables**

- Polymorphic Effect 1 and Effect 2 sections
- No regression in MIDI send/receive

---

## Phase 5: Layout & UX Refinements ✅

**Goal:** Improve layout and UX to better match Perl and common workflows.

**Duration:** 2–3 days

**Dependencies:** Phase 4

### Tasks

1. **Layout options** ✅
   - Implemented 2-column grid layout (EFX1 | EFX2, Delay | Reverb) via `SimpleEditorHelper(layout_mode="grid")`
   - Sections wrapped in QGroupBox with titles; `_GridSectionsAdapter` for test compatibility

2. **Distortion/Fuzz type** ✅
   - Type (0–5) exposed for both Distortion and Fuzz via `effects_generic_types`; tooltips added

3. **Phaser parameter alignment** ✅
   - Renamed "Center Freq" to "Resonance" for EFX2_PARAM_5_PHASER_CENTER_FREQ (0x21)

4. **Polish** ✅
   - Tooltips for key controls via `EffectsData.effect_tooltips` and `_apply_effect_tooltips()`
   - Consistent labeling: "Balance [dry->wet]" for Flanger and Ring Mod

**Deliverables**

- Final layout and UX improvements
- Documentation updates for Effects Editor

---

## Phase 6: Documentation & Cleanup ✅

**Goal:** Update docs and remove obsolete code.

**Duration:** 1 day

**Dependencies:** Phases 1–5

### Tasks

1. **Update `doc/effects.rst`** ✅
   - Added "JD-Xi Implementation" section with polymorphic behavior, 2-column layout, Delay/Reverb parameters

2. **Code cleanup** ✅
   - Removed unused `efx1_param_labels` / `efx2_param_labels` (replaced by polymorphic layout specs)
   - Fixed Phaser docstring/log messages (was incorrectly "Flanger")

3. **Changelog** ✅
   - See changelog entry below

**Deliverables**

- Updated effects documentation
- Cleaner codebase
- Changelog entry

### Changelog Entry (Effects Editor)

**Effects Editor improvements (Phases 1–6)**

- **Data layer**: Added Delay/Reverb params (On/Off, Type, HF Damp, Time/Note mode), Compressor Side Chain/Side Sync, coarse_tune for Side Note
- **Delay & Reverb UI**: Full parameter set with Time/Note mode, Note dropdown, HF Damp
- **Compressor**: Side Chain, Side Sync switches; Side Note as coarse_tune combo
- **Polymorphic sections**: Effect 1 and Effect 2 use QStackedWidget—one page per effect type; no more show/hide
- **Layout**: 2-column grid (EFX1|EFX2, Delay|Reverb) via SimpleEditorHelper layout_mode="grid"
- **Phaser**: Renamed "Center Freq" to "Resonance" (0x21)
- **Polish**: Tooltips for key controls; "Balance [dry->wet]" labeling
- **Cleanup**: Removed efx1_param_labels, efx2_param_labels

---

## Summary Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| 0. Preparation | 1–2 days | 1–2 days |
| 1. Data Layer | 2–3 days | 3–5 days |
| 2. Delay & Reverb UI | 3–4 days | 6–9 days |
| 3. Compressor | 1–2 days | 7–11 days |
| 4. Polymorphic Sections | 4–6 days | 11–17 days |
| 5. Layout & UX | 2–3 days | 13–20 days |
| 6. Documentation | 1 day | 14–21 days |

**Total estimate:** ~3–4 weeks

---

## Risk Mitigation

- **SysEx address drift:** Phase 0 audit reduces risk of wrong parameter mapping.
- **Regression:** Run existing effects tests after each phase; manual spot-checks on hardware.
- **Scope creep:** Phases 5–6 can be deferred if time is limited; Phases 1–4 deliver most value.

---

## Optional / Future Work

- Preset management for effects (save/load effect chains)
- Visual routing diagram (EFX1 → EFX2 → DLY → REV)
- MIDI Learn for effect parameters
- A/B comparison for effect settings
