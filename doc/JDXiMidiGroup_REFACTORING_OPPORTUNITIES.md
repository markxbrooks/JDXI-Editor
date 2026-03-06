# JDXiMidiGroup Refactoring Opportunities

This document identifies opportunities to convert UI groups to `JDXiMidiGroup` widgets across the codebase. The pattern provides consistent spec-driven UI construction, shared layout helpers, and a clear separation of concerns.

---

## Current JDXiMidiGroup Subclasses

| Widget | Location | Purpose |
|--------|----------|---------|
| **TransportWidget** | `jdxi_editor/ui/widgets/transport/transport.py` | Play, Stop, Pause buttons |
| **MidiFileGroup** | `jdxi_editor/ui/widgets/midi_file_group.py` | Load, Save MIDI file buttons |
| **EventSuppressionGroup** | `jdxi_editor/ui/widgets/event_suppression_group.py` | Program Changes, Control Changes checkboxes |
| **USBFileRecordingWidget** | `jdxi_editor/ui/widgets/usb/recording.py` | USB port, file selection, recording controls |
| **AutomationWidget** | `jdxi_editor/ui/editors/midi_player/automation.py` | Automation channel, type, program combos + Insert button |

---

## High Priority: MidiFilePlayer (Same Editor, Uses midi_state)

### 1. ClassificationGroup — Track Classification Buttons ✅ DONE

**Location:** `jdxi_editor/ui/widgets/classification_group.py`

**Implementation:**
- `_create_classify_tracks_widget()` — builds a composite widget
- `_build_classify_tracks_widgets()` — Detect Drums, Classify Tracks buttons
- `create_apply_all_button_and_label()` — Apply All Track Changes button

**Proposed:** Extract into `ClassificationGroup(JDXiMidiGroup)` with:
- **Buttons:** `detect_drums`, `classify_tracks`, `apply_all_track_changes`
- **Slots:** `parent.detect_and_assign_drum_tracks`, `parent.classify_and_assign_tracks`, `parent.apply_all_track_changes` (or equivalent)
- **Message boxes:** Group needs access to `no_midi_file`, `no_midi_file_classify`, `no_drum_tracks_found`, `no_tracks_classified`, `drum_tracks_detected`, `tracks_classified`, `error_detect_drums`, `error_classify_tracks` — these could stay on the parent or be passed via specs

**Complexity:** Medium. The classification logic and message boxes are tightly coupled to the editor. The group could own the button specs and layout; validation/message boxes could remain on the parent.

**Lines:** ~269–285, 297–317, 754–773

---

### 2. MuteChannelsGroup — Channel Mute Buttons

**Location:** `jdxi_editor/ui/editors/midi_player/editor.py`

**Current implementation:**
- `init_mute_controls()` — creates 16 channel mute buttons in a horizontal layout
- Uses `create_small_sequencer_square_for_channel(ch)` for each channel
- Callback: `_toggle_channel_mute(channel, checked, btn)`
- Syncs with `midi_state.muted_channels` and `midi_file.midi_track_viewer`

**Proposed:** Extract into `MuteChannelsGroup(JDXiMidiGroup)` with:
- **Layout:** QGroupBox "Mute Channels" with horizontal row of 16 buttons
- **State:** Reads/writes `midi_state.muted_channels`
- **Slots:** `_toggle_channel_mute` (or a wrapper that updates both viewer and state)

**Complexity:** Medium. Dynamic button creation (1–16) and two-way sync with track viewer. The group would need a reference to `midi_file.midi_track_viewer` for `_sync_mute_buttons_from_track_viewer` and `get_muted_channels`.

**Lines:** ~725–752, 775–880

---

## Medium Priority: Other Editors (Different State Types)

`JDXiMidiGroup` currently expects `(midi_state: MidiPlaybackState, parent: MidiFilePlayer)`. Pattern and Playlist editors use different state. Options:
- Make `midi_state` optional and add a generic `state` or `context` parameter
- Introduce a `JDXiButtonGroup` base that only requires `parent` and optional `state`
- Create editor-specific group base classes (e.g. `PatternEditorGroup`, `PlaylistEditorGroup`)

---

### 3. PatternFileGroup — Pattern Editor Load/Save/Clear

**Location:** `jdxi_editor/ui/editors/pattern/ui.py`

**Current implementation:**
- `_create_file_group()` — QGroupBox "Pattern" with Load, Save, Clear Learn buttons + drum selector combo
- Uses `_add_button_with_label_from_spec()` (same pattern as `create_jdxi_button_with_label_from_spec`)
- Specs: `load`, `save`, `clear_learn` in `self.specs["buttons"]`

**Proposed:** Extract into `PatternFileGroup(JDXiMidiGroup)` or a Pattern-specific base with:
- **Buttons:** Load, Save, Clear
- **Combo:** Drum selector (could stay in group or remain in parent)
- **Slots:** `_load_pattern_dialog`, `_save_pattern_dialog`, `_clear_learn` (or equivalent)

**Complexity:** Medium. Requires extending `JDXiMidiGroup` to support `parent` without `MidiPlaybackState`, or a new base class.

**Lines:** ~604–623, 730–750

---

### 4. PatternTransportGroup — Pattern Editor Transport

**Location:** `jdxi_editor/ui/editors/pattern/ui.py`

**Current implementation:**
- `_init_transport_controls()` — Play, Stop, Pause, Shuffle Play
- Same structure as `TransportWidget` but with pattern-specific slots
- Uses `TransportSpec`-like objects built inline

**Proposed:** Reuse or adapt `TransportWidget`:
- **Option A:** Make `TransportWidget` accept a `transport_specs` factory/callback so Pattern/Playlist can inject their own specs
- **Option B:** Create `PatternTransportWidget(JDXiMidiGroup)` that overrides `_build_transport_specs()` with pattern slots

**Complexity:** Low–Medium. Pattern and Playlist transports are nearly identical; a configurable transport component would reduce duplication.

**Lines:** ~713–728

---

### 5. PlaylistTransportGroup — Playlist Editor Transport

**Location:** `jdxi_editor/ui/editors/playlist/editor.py`

**Current implementation:**
- `_init_transport_controls()` — Play, Stop, Pause, Shuffle Play
- Same pattern as Pattern transport, different slots (`_playlist_transport_play`, etc.)

**Proposed:** Same as Pattern — configurable `TransportWidget` or `PlaylistTransportWidget(JDXiMidiGroup)`.

**Lines:** ~267–305

---

## Lower Priority / Different Patterns

### 6. Preset Selection Group — Preset Editor

**Location:** `jdxi_editor/ui/editors/preset/editor.py`

**Current implementation:**
- `_create_preset_selection_group()` — QGroupBox "Load a program" with combos, search box, preset list
- Complex: synth type combo, search, preset combo, category combo, etc.

**Proposed:** Lower priority. Structure is form-like (combos, search) rather than a simple button/checkbox group. Could be refactored later if a more general `JDXiFormGroup` or similar emerges.

---

### 7. Pattern Editor Other Groups

**Location:** `jdxi_editor/ui/editors/pattern/ui.py`

- `_create_duration_group()` — Duration control
- `_create_velocity_group()` — Velocity control
- `_create_beats_group()` — Beats per measure
- `_create_tempo_group()` — Tempo control
- `_create_learn_group()` — Learn Pattern
- `_create_measure_group()` — Measure management

These are smaller, control-specific groups. Converting them would require a shared state/context for the Pattern editor. Consider after ClassificationGroup and MuteChannelsGroup.

---

## JDXiMidiGroup Base Class (Updated)

Base class (`jdxi_editor/ui/widgets/jdxi/midi_group.py`) now supports:

```python
def __init__(
    self,
    parent: Optional[QWidget] = None,
    midi_state: Optional[MidiPlaybackState] = None,
):
```

- **Optional midi_state:** Groups that need it (e.g. EventSuppressionGroup) validate and raise if None
- **Relaxed parent type:** `QWidget | None` — works with MidiFilePlayer, PatternUI, PlaylistEditor

---

## Recommended Order

1. **ClassificationGroup** — High impact, same editor, clear button/spec pattern
2. **MuteChannelsGroup** — High impact, reduces `init_mute_controls` complexity
3. **TransportWidget generalization** — Enable reuse in Pattern and Playlist
4. **PatternFileGroup** — After base class supports optional/generic state
5. **PlaylistTransportGroup** — With generalized TransportWidget
6. **Pattern control groups** — After Pattern state/context is established

---

## Summary Table

| Opportunity | Editor | Priority | Effort | Notes |
|-------------|--------|----------|--------|-------|
| ClassificationGroup | MidiFilePlayer | High | Medium | 3 buttons, message box coupling |
| MuteChannelsGroup | MidiFilePlayer | High | Medium | 16 dynamic buttons, viewer sync |
| TransportWidget generalization | Pattern, Playlist | Medium | Low | Configurable specs |
| PatternFileGroup | Pattern | Medium | Medium | Needs base class extension |
| PlaylistTransportGroup | Playlist | Medium | Low | With TransportWidget |
| Preset selection | Preset | Low | High | Form-like, complex |
| Pattern control groups | Pattern | Low | Medium | Multiple small groups |
