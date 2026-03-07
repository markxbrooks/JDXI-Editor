# Pattern Editor: Save Notes Back to MIDI File — Gap Analysis

## Executive Summary

When a MIDI file is loaded into the Pattern Editor (from the MIDI File Player or via Load), the sequencer step buttons become non-selectable. Users cannot edit the pattern or save changes back to the MIDI file. This document analyzes the gap between current behavior and the desired workflow.

---

## 1. Current Behavior

### 1.1 Load Flow (MIDI File → Pattern Editor)

| Step | Location | Description |
|------|----------|-------------|
| 1 | `load_from_midi_file_editor()` | Entry when MIDI file is loaded in MidiFilePlayer |
| 2 | `_load_from_midi_file_object()` | Used when no filename (load from MidiFile object) |
| 3 | `_clear_measures_and_measures_list()` | Calls `pattern_widget.clear_and_reset(0)` — clears to 0 measures |
| 4 | `_create_new_measures(num_bars)` | `ensure_measure_count(num_bars)` — adds measures via `add_measure()` |
| 5 | `_load_notes_from_tracks_to_channels()` | Populates measure buttons with notes from MIDI tracks |
| 6 | `_select_first_measure_and_sync()` | Selects measure 0, calls `_button_manager.set_buttons(self.buttons)` |

**Alternative path (with filename):** `load_pattern(filename)` uses `_collect_notes_with_times_and_tempos_from_file`, `_assign_notes_and_durations_to_buttons`, and `_set_to_first_measure`.

### 1.2 Reported Issue

- **Symptom:** Sequencer step buttons (4×16 grid) are not selectable after a MIDI file is loaded.
- **Impact:** User cannot toggle notes, add/remove steps, or edit the pattern.
- **Consequence:** Save would write the loaded state only; no edits can be made.

### 1.3 Save Flow (Pattern Editor → MIDI File)

| Step | Location | Description |
|------|----------|-------------|
| 1 | `save_pattern(filename)` | Entry from Save button / dialog |
| 2 | `_create_tracks_per_row()` | Builds new `MidiFile` with 4 tracks (one per row) |
| 3 | `_add_motes_from_all_bars_to_track()` | Iterates `measure_widgets`, reads button state via `get_button_note_spec()` |
| 4 | `_save_midi_file()` | `midi_file.save(filename)` |
| 5 | `_update_midi_file_editor_with_file()` | Reloads saved file into MidiFilePlayer if connected |

**Data source for save:** `measure.buttons[row][step]` — `isChecked()`, `note`, `note_velocity`, `note_duration` via `get_button_note_spec()`.

---

## 2. Root Cause Hypotheses

### 2.1 Button Enable/Disable Logic

- **`_update_button_state(active_steps, row, step)`** — disables buttons when `step >= active_steps`.
- **`_update_button_states_for_beats_per_measure()`** — disables steps 12–15 when beats = 3/4.
- **`_on_button_clicked()`** — returns early if `not button.isEnabled()`.

**Gap:** After load, `_update_button_states_for_beats_per_measure()` is **not** called. If `measure_beats` or `active_steps` is wrong, buttons may remain disabled.

### 2.2 Button Manager / Sequencer Sync

- **`_button_manager.set_buttons(self.buttons)`** — `self.buttons` delegates to `pattern_widget.get_current_measure_widget().buttons`.
- After `clear_and_reset(0)`, there are 0 measures; `get_current_measure_widget()` returns `None`; `self.buttons` = `[[] for _ in range(4)]`.
- **Gap:** If `_button_manager` is set with empty buttons before measures exist, sequencer state may be inconsistent.

### 2.3 Measure Creation Order

- `_clear_measures_and_measures_list()` → `clear_and_reset(0)` → 0 measures.
- `_create_new_measures(num_bars)` → `ensure_measure_count(num_bars)` → N measures via `add_measure()`.
- Each `add_measure()` calls `_wire_button_clicks(widget)` — buttons should be wired.

**Gap:** If `_load_notes_from_tracks_to_channels` creates measures via its `while bar_index >= len(self.measure_widgets)` loop (safety path), those measures are created **outside** `add_measure()` and may **not** have `_wire_button_clicks` applied.

### 2.4 Data Model vs. UI Sync

- `PatternWidget` has `measures` (data) and `measure_widgets` (UI).
- `_load_notes_from_tracks_to_channels` writes to `measure.buttons[row][step]` (UI) but may not sync to `PatternMeasure.steps` (data).
- **Gap:** Save reads from buttons; if data model is out of sync, behavior may be inconsistent. Copy/paste and other operations rely on `PatternMeasure`.

### 2.5 midi_file / MidiFileController Mismatch

- Pattern Editor uses `_midi_file_controller` → `self.midi_file`, `self.midi_track`.
- When loading from MidiFileEditor, notes are loaded into measure widgets, but `_midi_file_controller` is **not** updated with the loaded file.
- **Gap:** `_calculate_note_on_time()` uses `self.midi_file.ticks_per_beat` — this comes from the controller’s default file, not the loaded one. PPQ mismatch could affect timing on save.

---

## 3. Desired Behavior

1. **Load:** MIDI file loads into Pattern Editor; notes appear in the grid.
2. **Edit:** User can click step buttons to add/remove notes; buttons remain selectable.
3. **Save:** User can save edits back to the same file (or a new file); MidiFilePlayer updates if connected.

---

## 4. Gap Analysis — Work Required

### 4.1 Fix Button Selectability (High Priority)

| Task | Description | Files |
|------|-------------|-------|
| **T1** | Call `_update_button_states_for_beats_per_measure()` after load (both `load_pattern` and `_load_from_midi_file_object`). | `pattern.py` |
| **T2** | Ensure `_button_manager.set_buttons(self.buttons)` runs **after** measures exist and first measure is selected. | `pattern.py` |
| **T3** | Avoid creating measures in `_load_notes_from_tracks_to_channels` via the `while` loop; rely on `ensure_measure_count` so all measures go through `add_measure()` and get `_wire_button_clicks`. | `pattern.py` |
| **T4** | Add logging around load flow to confirm: measure count, button enable state, click handler wiring. | `pattern.py` |

### 4.2 Align Data Model on Load (Medium Priority) — Phase 2 ✅

| Task | Description | Files | Status |
|------|-------------|-------|--------|
| **T5** | After populating buttons in `_load_notes_from_tracks_to_channels`, sync to `PatternMeasure.steps` (or ensure load path uses `sync_measure_to_ui` / `sync_ui_to_measure` correctly). | `pattern.py`, `widget.py` | ✅ Done |
| **T6** | Verify `PatternWidget.sync_ui_to_measure` / `sync_measure_to_ui` are used consistently when loading vs. editing. | `pattern.py`, `widget.py` | ✅ Done |

### 4.3 Align MIDI File State (Medium Priority) — Phase 3 ✅

| Task | Description | Files | Status |
|------|-------------|-------|--------|
| **T7** | When loading from MidiFileEditor, set `self.ppq` from the loaded file so PPQ matches for save/playback. | `pattern.py` | ✅ Done |
| **T8** | Ensure `_calculate_note_on_time` uses correct `ticks_per_beat` from the loaded file. | `pattern.py` | ✅ Done |

### 4.4 Save-Back to Same File (Lower Priority) — Phase 4 ✅

| Task | Description | Files | Status |
|------|-------------|-------|--------|
| **T9** | When saving after load from MidiFileEditor, optionally overwrite the same file instead of always prompting for a new path. | `pattern.py`, `ui.py` | ✅ Done |
| **T10** | Preserve non-pattern content (e.g., tempo, other tracks) when saving — current `_create_tracks_per_row` builds a fresh 4-track file. | `pattern.py` | Optional |

---

## 5. Implementation Order

1. **Phase 1 — Restore selectability:** T1, T2, T3, T4. ✅
2. **Phase 2 — Data consistency:** T5, T6. ✅
3. **Phase 3 — MIDI state alignment:** T7, T8. ✅
4. **Phase 4 — Save UX:** T9 ✅, T10 (optional).

---

## 6. Key Code References

| Area | File | Relevant Methods |
|------|------|------------------|
| Load from MidiFileEditor | `pattern.py` | `load_from_midi_file_editor`, `_load_from_midi_file_object`, `_load_notes_from_tracks_to_channels`, `_select_first_measure_and_sync` |
| Load from file | `pattern.py` | `load_pattern`, `_assign_notes_and_durations_to_buttons`, `_set_to_first_measure` |
| Button state | `pattern.py` | `_update_button_state`, `_update_button_states_for_beats_per_measure`, `_on_button_clicked` |
| Save | `pattern.py` | `save_pattern`, `_create_tracks_per_row`, `_add_motes_from_all_bars_to_track` |
| Pattern widget | `widget.py` | `add_measure`, `_wire_button_clicks`, `ensure_measure_count`, `clear_and_reset` |
| Measure widget | `measure_widget.py` | `PatternMeasureWidget`, `buttons` |

---

## 7. Testing Checklist

- [ ] Load MIDI file from MidiFilePlayer → Pattern Editor shows notes; buttons are clickable.
- [ ] Load MIDI file via Load button → same behavior.
- [ ] Toggle step buttons on/off after load → state updates correctly.
- [ ] Save after load → file contains edited notes; MidiFilePlayer refreshes if connected.
- [ ] Load multi-bar file → all bars editable; measure list navigation works.
- [ ] 3/4 time signature → steps 12–15 disabled as expected.
