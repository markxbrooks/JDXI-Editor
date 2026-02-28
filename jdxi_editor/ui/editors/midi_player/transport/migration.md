Migration Workflow

## Phase 1 — Dual Representation (done)
Both exist: note, velocity, duration_ms, midi_note.
Existing code still works. New code can use spec.midi_note.

## Phase 2 — Soft Deprecation (done)
- `is_active` now reflects midi_note: `return self.midi_note is not None`
- `_sync_midi_note()` rebuilds midi_note from note, duration_ms, velocity
- `__setattr__` auto-syncs midi_note when note/velocity/duration_ms are mutated
- Property redirect for `note` was skipped (dataclass InitVar name collision with @property)

## Phase 3 — Final Model (future)
Eventually collapse to:
```python
@dataclass
class NoteButtonSpec:
    midi_note: Optional[MidiNote] = None
```

## Deferred: Property redirect
Using InitVar + @property with the same name causes dataclass to pass the property object as the default. Alternative approaches for Phase 3:
- Custom `__init__` with friendly param names + private storage
- Or collapse to midi_note-only and drop the redirect

---

## Other opportunities: MidiNote / NoteButtonSpec on buttons

### 1. Replace local `NoteSpec` with `NoteButtonSpec` — **low effort**
| Location | Current | Opportunity |
|----------|---------|-------------|
| `midi/file/controller.py` | `_get_button_note_spec()` defines local `NoteSpec` | Use `get_button_note_spec(button)` from helper, or return `NoteButtonSpec` |
| `midi/playback/controller.py` | `_get_button_note_spec()` defines local `NoteSpec` | Same |
| `ui/sequencer/button/manager.py` | `_create_note_spec()` returns local `NoteSpec` | Return `NoteButtonSpec(note=..., duration_ms=..., velocity=...)` |

### 2. SequencerButton: note_spec as canonical — **done**
`SequencerButton` now uses `note_spec` as canonical. Properties `note`, `note_duration`, `note_velocity` read/write through it. Aliases `duration`/`velocity` for manager compatibility.

### 3. ButtonState: use NoteButtonSpec — **done**
`ButtonState` now holds `note_spec: NoteButtonSpec` as canonical. Properties `note`, `velocity`, `duration_ms` read from it. `is_active()` uses `note_spec.is_active`.