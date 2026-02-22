# Critique: MIDI Player Refactoring and PlaybackEngine Migration

## 1. Refactoring strategy (refactoring.md)

**What’s right**

- **Responsibility split** – Separating UI, domain, playback, worker, transport, and USB is the right direction. The proposed modules (layout, playback_engine, worker_controller, midi_analyzer, transport, usb_recorder, message_factory) match real boundaries.
- **Incremental order** – “MidiAnalyzer first → PlaybackEngine → Transport → USB → Worker last” is sensible: low UI coupling first, worker (most Qt/thread coupling) last.
- **Thin editor** – Reducing the editor to orchestration + `_connect_components()` is the right goal.
- **Pure engine** – Keeping the playback engine free of Qt and UI is good for testing and reuse.

**Gaps / risks**

- **Dual playback paths** – The doc says “move process_tracks, buffer_message, … into PlaybackEngine” but the current system is **buffer-based** (precompute `(tick, raw_bytes, tempo)` and the worker walks that list). The new engine is **event-list + process_until_now()**. You will have two different models until the old path is removed. The migration plan should explicitly say: “Phase 1: Engine built and tested in parallel; Phase 2: Worker/editor switch to engine; Phase 3: Remove old buffer/process_tracks path.”
- **Who owns mute/suppress?** – Mute (tracks/channels) and “suppress program/control changes” are currently applied during **buffer build** (editor’s `process_track_messages` / `_is_program_or_bank_select`). The engine has `_muted_channels` and `suppress_*` and applies them in `_should_send`. That’s consistent, but the refactor doc doesn’t state that mute/suppress live in the engine (and are set by the UI/controller). Worth making explicit so nobody re-implements them in the worker.
- **Transport ↔ engine contract** – The doc doesn’t define the contract between TransportController and PlaybackEngine (e.g. who calls `start`/`stop`, who drives `process_until_now` — worker timer vs engine). That should be spelled out so the worker layer doesn’t duplicate transport logic.
- **Layout extraction** – Moving “UI builders only” into `layout.py` is good, but the editor currently holds a lot of **state** (midi_state, specs, refs to child widgets). The doc doesn’t say whether layout only **builds** widgets (and editor keeps state) or whether some state moves into a “MidiPlayerLayout” or similar. Clarifying that avoids a half-extract where layout and editor both know about the same state.

---

## 2. PlaybackEngine implementation (engine.py)

**What’s right**

- No Qt, no UI, callback-based (`on_event`) — good for testing and reuse.
- Uses a single sorted event list and `bisect` for start index — good.
- Mute/suppress live in the engine and are applied in one place (`_should_send`).
- `scrub_to_tick` and `start(start_tick)` support seek and start-from-position.

**Bugs and missing pieces**

1. **`ScheduledEvent` is a stub**  
   Used as `ScheduledEvent(absolute_tick, msg.copy())` but the class body is `pass`, so it has no `absolute_tick` or `message`. This will raise at runtime (e.g. in `process_until_now` when accessing `event.absolute_tick` / `event.message`). Fix: define a dataclass or explicit `__init__(self, absolute_tick, message)` and store both.

2. **`reset()` is missing**  
   `load_file` calls `self.reset()`. If `reset()` isn’t defined, playback will fail after load. You need at least: clear or reset `_event_index`, `_start_tick`, `_start_time`, `_is_playing`, and optionally mute/suppress state if you want “load = clean state.”

3. **Tempo map is per-track and overwritten**  
   `_build_tempo_map` does:
   ```python
   for track in self.midi_file.tracks:
       absolute_tick = 0  # reset per track!
       for msg in track:
           absolute_tick += msg.time
           if msg.type == "set_tempo":
               self._tempo_map[absolute_tick] = msg.tempo
   ```
   So only the **last** track’s tempo events end up in `_tempo_map`. For Type 1 MIDI, tempo usually lives in track 0; other tracks don’t define tempo. So in practice you might only see track 0’s tempo if it’s first, or only the last track’s. Fix: either build one global tempo map (e.g. merge all tracks into one chronological stream of (tick, set_tempo) and then build the map), or follow the spec (Type 1: track 0 is usually the “conductor” track; use only track 0 for tempo, or merge tempo events from all tracks into a single timeline).

4. **`_tick_to_seconds` is wrong for variable tempo**  
   Current logic:
   ```python
   def _tick_to_seconds(self, tick: int) -> float:
       tempo = self._get_tempo_at_tick(tick)
       seconds_per_tick = tempo / 1_000_000 / self.ticks_per_beat
       return tick * seconds_per_tick
   ```
   This assumes one constant tempo from 0 to `tick`. With tempo changes, time from 0 to `tick` must be computed by integrating segment by segment (each segment has constant tempo). The existing worker does this correctly in `_calculate_message_time` (iterate ordered events, add `delta_ticks * (current_tempo/1e6)/ticks_per_beat`, update tempo on set_tempo). The engine should do the same: e.g. `tick_to_seconds(tick)` = sum of segment durations from 0 to `tick` using `_tempo_map`, or maintain a cached list of (tick, time_sec) and interpolate.

5. **Muted tracks are not applied**  
   The engine has `_muted_tracks` and `_muted_channels`. `_should_send` only checks `_muted_channels`. So track mute is never used. The current editor applies track mute at **buffer build** time (skip non–program/bank-select messages for muted tracks). So either:
   - the engine must also skip events that belong to muted tracks (you need to store `track_index` on each event and check `_muted_tracks` in `_should_send`), or
   - the worker/editor only feeds the engine events from non-muted tracks (so the engine doesn’t need track mute). The refactor doc should decide which layer owns “track mute” and implement it there.

6. **Channel attribute on messages**  
   `_should_send` uses `msg.channel`. In mido, channel messages have `.channel`; some meta or system messages might not. Defensive check (e.g. `getattr(msg, 'channel', None)`) or filtering to channel messages only in `_build_event_list` avoids surprises.

---

## 3. Aligning engine and current buffer-based design

The current playback path is:

1. **Refill** – `midi_message_buffer_refill` → `process_tracks` → `process_track_messages` → build `(absolute_ticks, raw_bytes, tempo)` with mute/suppress and PC/CC rules applied per track.
2. **Worker** – Timer fires; worker walks `buffered_msgs`, uses **segment-wise** tempo (per-message tempo or `_calculate_message_time`) to decide which messages are due, sends raw bytes.

The engine path is:

1. **Load** – `load_file` → build `_events` (and tempo map).
2. **Timer** – Something (worker or controller) calls `process_until_now()`; engine advances `_event_index` and invokes `on_event(msg)` for each due message.

So the **worker** must change from “walk buffered_msgs and compute time from tempo segments” to “call `engine.process_until_now()` and handle `on_event` (e.g. send raw bytes). That implies:

- The engine must output the same semantics as today: correct wall-clock time for each message (segment-wise tempo), and only messages that pass mute/suppress. Fixing `_tick_to_seconds` and tempo map (and optionally track mute) is therefore required before switching the worker over.
- **Pause** – The current design can “pause” by not advancing the worker or by not sending. With the engine, pause = “don’t call `process_until_now`” and/or “don’t invoke `on_event`.” So transport “pause” can be implemented in the controller/worker without the engine needing a pause state, unless you want the engine to track “paused at tick X” for resume. The doc could note that.

---

## 4. Recommended next steps

1. **Fix engine.py first**
   - Define `ScheduledEvent` (e.g. `absolute_tick`, `message`, and optionally `track_index`).
   - Implement `reset()` and call it from `load_file`.
   - Build a single global tempo map (e.g. from track 0 only for Type 1, or merge all set_tempo events by global tick).
   - Replace `_tick_to_seconds(tick)` with segment-wise integration (or equivalent cached time map).
   - Either add track index to events and respect `_muted_tracks` in `_should_send`, or document that track mute is applied by the caller before feeding the engine.
   - Add a short docstring on how the engine is driven (who calls `process_until_now`, who sets `on_event`).

2. **Lock the migration contract**
   - One-page “playback contract”: editor/worker calls `engine.load_file`, `engine.start(start_tick)`, and on a timer `engine.process_until_now()`; engine calls `on_event(msg)`; transport calls `engine.start`/`stop`/`scrub_to_tick`. That avoids the worker re-implementing tempo or mute.

3. **Keep incremental order, add a clear “switchover” step**
   - After MidiAnalyzer (and optionally layout) extraction, add: “Introduce PlaybackEngine and a **feature flag or parallel path**: worker can run in ‘legacy buffer mode’ or ‘engine mode’. When engine mode is correct (including tempo/mute), remove legacy buffer and process_tracks from the editor.”

4. **Tests**
   - Unit tests for the engine: load a tiny MIDI (one track, a few notes and one set_tempo), call `start(0)`, advance time (or mock time), call `process_until_now`, assert `on_event` is called for the right messages at the right times. That will lock the tempo and `ScheduledEvent` behavior and catch regressions when you fix the bugs above.

---

## Summary

| Area | Verdict |
|------|--------|
| Refactoring strategy (doc) | Sound; add explicit “dual path then switchover,” ownership of mute/suppress, and Transport–Engine contract. |
| PlaybackEngine design | Good (pure, callback-based). |
| Engine implementation | Needs fixes: ScheduledEvent, reset(), global tempo map, segment-wise tick→time, track mute handling, and defensive channel access. |
| Migration | Fix engine first and add tests; then define the playback contract and switch the worker over; then remove the old buffer path. |
