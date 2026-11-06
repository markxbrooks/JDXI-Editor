# Playback contract: who calls what

One-page contract for the MIDI file player so the editor, transport and UI don’t re-implement timing, tempo or mute. All playback timing and filtering live in `PlaybackEngine`; `TransportController` is the only thing that drives it; the editor only issues commands and renders signals.

---

## Roles

| Role | Where | Responsibility |
|------|-------|----------------|
| **Engine** | `picomidi.playback.engine.PlaybackEngine` | Pure playback: tempo map, event list, mute/suppress, position, held-note tracking. No Qt, no I/O, not thread-safe. |
| **Transport** | `jdxi_editor.midi.playback.transport.TransportController` | Owns the engine and a scheduler thread. Single source of transport state. Publishes Qt signals. |
| **Editor** | `MidiFilePlayer` | Loads files, forwards button clicks / slider / mutes to the transport, renders its signals. |
| **Pattern Sequencer** | `PatternSequenceEditor` + `jdxi_editor.midi.pattern.compiler` | Compiles the step pattern with `compile_pattern()` and plays it through its own `TransportController` (whole-file loop). Save writes the same compiled file. |
| **TransportWidget** | `jdxi_editor.ui.widgets.transport.transport` | Buttons only. Clicks call editor slots; `set_state(TransportState)` is the only thing that changes what they show. |

---

## Engine

- **`load_file(midi_file)`**: Builds event list, tempo map, time map; resets to STOPPED at tick 0. Mute/suppress settings are kept.
- **`start(start_tick)`**: Play from `start_tick`.
- **`pause()` / `resume()`**: Pause keeps the position (and event index); resume continues from it. Time spent paused never counts, so there is no burst of events on resume.
- **`stop()`**: STOPPED, position kept (`seek_tick(0)` rewinds).
- **`seek_tick(tick)` / `seek_seconds(s)`**: Move the position in any state; the state is unchanged.
- **`process_until_now() -> bool`**: Sends due, non-filtered events via `on_event`. Returns **True exactly once**, on the call that reaches the end of the file (the engine is then STOPPED at the end).
- **`position_seconds` / `position_tick` / `duration_seconds`**: The only playback clock. Valid in every state.
- **`tick_to_seconds` / `seconds_to_tick` / `tempo_at_tick`**: Tempo-map aware conversions.
- **Held notes**: The engine remembers notes and sustain pedals it sounded and sends note-off / sustain-off on pause, stop, seek and mute. `all_notes_off()` additionally sends All Sound Off / All Notes Off on every channel (panic).
- **Controller restore ("chase")**: Starting, seeking or looping mid-file sends the bank select + program change, controllers (except RPN/NRPN data and channel-mode CCs) and pitch bend in effect at that point, through the same mute/suppress filter. Only values that differ from what the engine last sent go out, so looping does not make the JD-Xi reload its tone on every pass. Stop forgets what was sent.
- **Loop**: `set_loop(enabled, (start_tick, end_tick) | None)`. None loops the whole file. Events at the loop end are not played; held notes are released at the wrap. Starting beyond the loop end plays on to the end of the file.
- **Speed**: `set_speed(0.25–2.0)`; file time advances at `speed` × wall-clock time. The position is kept when it changes.
- **MIDI clock**: `set_send_clock(True)` sends 24 clocks per beat following the tempo map and speed, Start (from 0) or Song Position Pointer + Continue (from elsewhere), and Stop on pause/stop/end. Off by default: with the JD-Xi Sync set to MIDI/AUTO, Start also starts its own pattern sequencer.
- **Bars**: `bar_beat_at_tick`, `time_signature_at_tick`, `nearest_bar_tick` follow `time_signature` meta events (default 4/4).

## Transport

- **Commands**: `load(file, keep_position=False)`, `play()` (also resumes), `pause()`, `toggle_play_pause()`, `stop()` (silence + rewind), `seek_seconds(s)`, `set_loop(enabled, a_s, b_s)`, `clear_loop_range()`, `set_speed(x)`, `set_send_clock(on)`, `set_mutes(tracks, channels)`, `set_suppression(...)`, `panic()`, `shutdown()`. `load(..., keep_position=True)` also keeps the A–B range.
- **Signals**:
  - `state_changed(TransportState)` after every change, including end of song
  - `position_changed(float)` every 50 ms while playing, and after seeks/stop
  - `tempo_changed(int)` when the tempo at the position changes
  - `finished()` once when the end of the file is reached (position already rewound to 0); never while looping
  - `loop_changed()` when loop on/off or the A–B range changes
- **Threading**: a dedicated thread calls `process_until_now()` every 5 ms on a precise timer. Every engine call (both threads) is made under one lock, so MIDI sends are serialised. The end-of-song notification is queued back to the GUI thread.

## Editor

- Play / Pause / Stop / slider / mute / suppress → transport commands. Mute and suppress changes apply immediately.
- `state_changed` → `TransportWidget.set_state`, digital display. `position_changed` → slider, label, bar. `tempo_changed` → tempo display.
- On Play from STOPPED the file is reloaded with `keep_position=True`, so track-viewer edits are heard and a seek made while stopped is honoured.
- Other editors (Playlist, Patch Manager) load files via `midi_load_file_from_path(...)` and listen to `transport_controller.finished`.
- **One file**: the track viewer's `file_changed(midi_file)` makes that file `midi_state.file` and reloads the transport (keeping position), so track edits are heard, saved to `.msz`, and shown as program-change markers.
- Ruler: `seek_requested` → seek; `marker_moved` / `marker_delete_requested` → move/delete a program change (with its bank select).

## Pattern Sequencer

- `compile_pattern(PatternSpec)` is pure: Type 1 file, track 0 = tempo + time signature, one named track per row on its channel, every track ending exactly at the last bar (so the loop repeats whole bars with no gap). Velocities 1–127; overlapping same notes are clipped; no program changes are added.
- Play compiles and loads when stopped; edits, tempo and bar changes while playing call `schedule_recompile()`, which reloads with `keep_position=True` (tick-based, so a tempo change stays on the beat).
- Row mutes are channel mutes on the transport (live). The step highlight follows `position_tick`, not the last event sent.
- Messages go straight to the output port, like the MIDI File Player.
- Note lengths are stored in steps (`StepNoteEvent.duration_steps`); `duration_ms` is derived from the pattern tempo, so changing tempo keeps the musical length. A step entered by clicking takes the current Velocity and Duration controls.
- A step can hold several notes (`StepNoteEvent.extra_notes`, each with its own velocity and length): Shift+click a used step to add/remove the row's selected note, right-click to list/remove notes. All of them are compiled; the button shows the count. (The Analog part is monophonic on the JD-Xi, so it plays one note of a chord.)
- `import_pattern()` (`jdxi_editor.midi.pattern.importer`) is used by both Load Pattern and loading from the MIDI File Player: nearest-step rounding, real lengths and velocities, and notes sharing a step kept as a chord, and a count of what could not be placed (the same note twice on one step, channels without a row, extra tempo changes). Load Pattern shows that summary when anything was dropped.

---

## Summary diagram

```
TransportWidget ──click──▶ Editor ──command──▶ TransportController ──lock──▶ PlaybackEngine
       ▲                     ▲                    │   ▲                         │
       └──── set_state ──────┴──── signals ───────┘   └── scheduler thread ─────┘
                                                        process_until_now() → on_event → MIDI out
```

---

## Don’t

- **Editor / widgets**: Don’t start timers, read `time.time()` or keep a "start time" for playback. Ask the transport for the position.
- **Buttons**: Don’t rely on a button's own checked state; render `state_changed`.
- **Any**: Don’t duplicate mute/suppress logic; only the engine’s `_should_send` filters events.
- **Any**: Don’t call engine methods directly from the GUI while the transport is running; go through the transport (it holds the lock).
