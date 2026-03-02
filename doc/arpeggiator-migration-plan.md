# Arpeggiator SysEx Migration Plan

A phased plan to bring the JDXI Editor Arpeggio Editor to feature parity with the Perl `jdxi_manager.pl` implementation, enabling bidirectional SysEx sync (receive and display incoming Arpeggiator data from the device).

**Reference:** `doc/arpeggiator-sysex-gap-analysis.md`, Roland MIDI Implementation Guide (PDF), `doc/perl/jdxi_manager.pl`, `doc/perl/JDXidata.pm`

---

## Current State Summary

### JDXI Editor Implementation

| Component | Location | Status |
|-----------|----------|--------|
| ArpeggioEditor | `jdxi_editor/ui/editors/arpeggio/arpeggio.py` | Extends BasicEditor; sends params via `_on_parameter_changed` |
| ArpeggioParam | `jdxi_editor/midi/data/parameter/arpeggio.py` | ✓ Correct: Grid, Duration, Switch, Style, Motif, Octave Range, Accent, Velocity |
| Arpeggio data enums | `jdxi_editor/midi/data/arpeggio/` | ArpeggioGrid, ArpeggioDuration, ArpeggioMotif, ArpeggioOctaveRange, etc. |
| Program Zone | `jdxi_editor/midi/data/parameter/program/zone.py` | ProgramZoneParam.ARPEGGIO_SWITCH (per-zone) |

### Gaps (from `doc/arpeggiator-sysex-gap-analysis.md`)

| Component | Status | Issue |
|-----------|--------|-------|
| PROGRAM_SECTION_MAP | ✓ Fixed | 0x40→CONTROLLER (Option B) |
| PARAMETER_ADDRESS_NAME_MAP | ✓ Fixed | Added `(TEMPORARY_PROGRAM, CONTROLLER)` → `ArpeggioParam` |
| Parser | ✓ Fixed | Uses ArpeggioParam; produces correct param names |
| helper.py (send) | ✓ Fixed | TEMPORARY_PROGRAM handles CONTROLLER → ArpeggioParam |
| ArpeggioEditor | ✓ Fixed | Connected to `midi_sysex_json`; receives SysEx |
| Arpeggio SysEx Dispatcher | ✓ Fixed | `_dispatch_sysex_to_area` maps parsed data → widgets |
| MidiRequests | ✓ Fixed | PROGRAM_CONTROLLER request for data_request on show |

---

## Phase 0: Preparation & Validation

**Goal:** Establish baseline, validate SysEx addresses, and ensure test harness exists.

**Duration:** 0.5–1 day

### Tasks

1. **SysEx address validation** ✅ (documented in gap analysis)
   - Program Controller: `18 00 40 00`, size 0x0C (12 bytes)
   - Offsets: 0x01 Grid, 0x02 Duration, 0x03 Switch, 0x05 Style, 0x06 Motif, 0x07 Octave Range, 0x09 Accent, 0x0A Velocity

2. **Test harness**
   - Add or extend `tests/test_arpeggio_editor.py` (if missing)
   - Baseline: init, controls registered, send_midi_parameter
   - Run: `uv run pytest tests/test_arpeggio_editor.py -v`

**Deliverables**

- Gap analysis doc ✅ (`doc/arpeggiator-sysex-gap-analysis.md`)
- Test baseline for ArpeggioEditor

---

## Phase 1: Data Layer & Parameter Mapping

**Goal:** Ensure parser and helper use `ArpeggioParam` for Program Controller SysEx.

**Duration:** 1 day

**Dependencies:** Phase 0

### Tasks

1. **Add ArpeggioParam to PARAMETER_ADDRESS_NAME_MAP**
   - File: `jdxi_editor/midi/map/parameter_address.py`
   - Add import: `from jdxi_editor.midi.data.parameter.arpeggio import ArpeggioParam`
   - Add entry: `(AreaMSB.TEMPORARY_PROGRAM.name, ProgramLMB.CONTROLLER.name): ArpeggioParam`

2. **Add CONTROLLER handling in helper.py**
   - File: `jdxi_editor/midi/io/helper.py`
   - In `send_json_patch_to_instrument`, within `temporary_area == "TEMPORARY_PROGRAM"` block:
   - Add: `elif synth_tone == "CONTROLLER": param_class = ArpeggioParam`
   - Add import for `ArpeggioParam`

3. **Verify ArpeggioParam.get_by_name**
   - Ensure `ArpeggioParam` has `get_by_name` class method (like VocalFXParam, ProgramCommonParam)
   - If missing, add: `@classmethod def get_by_name(cls, name: str) -> Optional[AddressParameter]`

**Deliverables**

- Parser produces correct param names (ARPEGGIO_GRID, ARPEGGIO_STYLE, etc.) for Program Controller SysEx
- helper.py can send Arpeggio params when applying patches

---

## Phase 2: SysEx Request & Data Request on Show

**Goal:** Request Program Controller data when Arpeggio Editor is shown (like Vocal FX).

**Duration:** 0.5–1 day

**Dependencies:** Phase 1

### Tasks

1. **Add MidiRequests.PROGRAM_CONTROLLER**
   - File: `jdxi_editor/midi/sysex/request/hex.py`
   - Add: `PROGRAM_CONTROLLER_AREA = "40"` (or equivalent for address `00 40 00`)
   - File: `jdxi_editor/midi/sysex/request/midi_requests.py`
   - Add: `PROGRAM_CONTROLLER = create_request(TEMPORARY_PROGRAM_RQ11_HEADER, JDXISysExHex.PROGRAM_CONTROLLER_AREA, "00 00 00 00 00 0C")`
   - Verify RQ1 format: address `18 00 40 00`, size `00 00 00 0C` (12 bytes)

2. **Add data_request on show**
   - File: `jdxi_editor/ui/editors/arpeggio/arpeggio.py`
   - Add `midi_requests = [MidiRequests.PROGRAM_CONTROLLER]` (or include in existing list)
   - Override `showEvent` to call `self.data_request()` when editor is shown
   - Ensure `data_request` uses `midi_helper` to send RQ1 for Program Controller

**Deliverables**

- Arpeggio Editor requests current arpeggiator settings from device when opened
- Device responds with DT1; parser produces correct JSON

---

## Phase 3: SysEx Receive & Dispatcher

**Goal:** Connect ArpeggioEditor to `midi_sysex_json` and update widgets from parsed SysEx.

**Duration:** 1.5–2 days

**Dependencies:** Phases 1–2

### Tasks

1. **Connect to midi_sysex_json**
   - File: `jdxi_editor/ui/editors/arpeggio/arpeggio.py`
   - In `__init__`, after `setup_ui`:
   - Add: `self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)`
   - (Follow VocalFXEditor pattern)

2. **Implement _dispatch_sysex_to_area**
   - Filter: `temporary_area == "TEMPORARY_PROGRAM"` and `synth_tone == "CONTROLLER"`
   - Use `filter_sysex_keys` (from `jdxi_editor.ui.editors.digital.utils`) to get param dict
   - For each param: resolve via `ArpeggioParam.get_by_name`, find widget in `self.controls`
   - Update widget: `setValue` for sliders, `combo_box.setCurrentIndex` for combos (use `values` for MIDI→index mapping), `setChecked` for switches
   - Use `blockSignals(True/False)` to avoid feedback loops
   - Handle `convert_from_midi` for Octave Range (61–67 → -3 to +3) and other params with display mapping

3. **Widget mapping**
   - ArpeggioEditor uses `self.controls: Dict[AddressParameter, QWidget]`
   - Ensure all ArpeggioParam members used in layout are registered in `controls` during `_build_widgets` / `_build_switches` / `_build_sliders` / `_build_combo_boxes`
   - Note: ArpeggioEditor has two ARPEGGIO_SWITCH controls (ProgramZoneParam and ArpeggioParam). Program Controller SysEx only updates ArpeggioParam.ARPEGGIO_SWITCH.

**Deliverables**

- Arpeggio Editor receives SysEx JSON and updates Grid, Duration, Switch, Style, Motif, Octave Range, Accent, Velocity
- No regression on send (slider/combo changes still send to device)

---

## Phase 4: Enum & Display Value Handling ✅ COMPLETE

**Goal:** Correctly map MIDI values to combo box indices and display values.

**Duration:** 0.5–1 day

**Dependencies:** Phase 3

### Tasks

1. **Combo boxes with value lists** ✅
   - ArpeggioGrid, ArpeggioDuration, ArpeggioMotif: index = MIDI value (0–8, 0–9, 0–11)
   - ArpeggioOctaveRange: MIDI 61–67 → display -3 to +3; use `ArpeggioParam.convert_from_midi` or `ArpeggioOctaveRange` enum
   - ArpeggioStyle: 0–127 → combo index (if ARPEGGIO_STYLE has 128 entries)

2. **Sliders**
   - ARPEGGIO_ACCENT_RATE: 0–100, direct
   - ARPEGGIO_VELOCITY: 0–127 (REAL=0 or 1–127); verify display mapping

3. **Switches**
   - ARPEGGIO_SWITCH: 0=OFF, 1=ON; use `setChecked(bool(value))`

**Deliverables**

- All params display correctly when SysEx is received
- Manual test: change param on hardware, verify editor updates; change in editor, verify hardware updates

---

## Phase 5: Documentation & Cleanup ✅ COMPLETE

**Goal:** Update docs and changelog.

**Duration:** 0.5 day

**Dependencies:** Phases 1–4

### Tasks

1. **Update doc/arpeggiator.rst** ✅
   - Add "JD-Xi Implementation" section
   - Document SysEx sync (request on show, receive, bidirectional)

2. **Changelog**
   - Add Arpeggiator SysEx sync to CHANGELOG.md

3. **Gap analysis**
   - Mark gaps as resolved in `doc/arpeggiator-sysex-gap-analysis.md`

**Deliverables**

- Updated docs
- Changelog entry

---

## Summary Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| 0. Preparation | 0.5–1 day | 0.5–1 day |
| 1. Data Layer | 1 day | 1.5–2 days |
| 2. SysEx Request | 0.5–1 day | 2–3 days |
| 3. SysEx Receive | 1.5–2 days | 3.5–5 days |
| 4. Enum Handling | 0.5–1 day | 4–6 days |
| 5. Documentation | 0.5 day | 4.5–6.5 days |

**Total estimate:** ~1 week

---

## Risk Mitigation

- **Address drift:** Gap analysis and MIDI Implementation Guide PDF are authoritative.
- **Regression:** Run Arpeggio tests after each phase; manual spot-checks on hardware.
- **Program Zone vs Program Controller:** ArpeggioEditor has both ProgramZoneParam.ARPEGGIO_SWITCH and ArpeggioParam.ARPEGGIO_SWITCH. Program Controller SysEx updates only the latter. Program Zone (per-zone Arpeggio Switch, Zone Octave Shift) is out of scope for this migration.

---

## Optional / Future Work

- Program Zone SysEx sync (per-zone Arpeggio Switch, Zone Octave Shift) if zone-specific UI is added
- Arpeggio preset management
- MIDI Learn for arpeggiator parameters
