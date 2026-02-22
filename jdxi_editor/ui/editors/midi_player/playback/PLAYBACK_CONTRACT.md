# Playback contract: who calls what

One-page contract for the MIDI player so the editor, worker, and transport don’t re-implement tempo or mute. All playback timing and filtering live in `PlaybackEngine`; the rest only call into it and handle I/O/UI.

---

## Roles

| Role | Responsibility |
|------|-----------------|
| **Editor** | Loads MIDI, owns `PlaybackEngine` (and worker/transport), wires UI to engine/transport. |
| **Worker** | Runs on a timer; calls `engine.process_until_now()`; sends bytes when engine invokes `on_event`. |
| **Transport** | Play/pause/stop/scrub; calls `engine.start` / `engine.stop` / `engine.scrub_to_tick`. |
| **Engine** | Pure playback: tempo, event list, mute/suppress, time→tick. No Qt, no I/O. |

---

## Contract

### Editor

- **Owns** the engine (and worker, transport).
- After user selects a file: load the `mido.MidiFile`, then call **`engine.load_file(midi_file)`**. Do not refill a separate buffer for playback; the engine is the source of truth.
- Sets **`engine.on_event = <callable>`** so that when the engine wants to send a message, the worker (or editor) can send it (e.g. to the MIDI port). Typically the worker holds the port and is given a reference to the engine’s `on_event` or the editor connects the engine’s callback to the worker’s send.
- Wires UI to engine/transport:
  - Mute (tracks/channels): call **`engine.mute_track(i, muted)`** / **`engine.mute_channel(ch, muted)`**.
  - Suppress program/control changes: set **`engine.suppress_program_changes`** / **`engine.suppress_control_changes`** (e.g. from checkboxes).
- Does **not** compute tempo or filter events for playback; the engine does that.

### Worker (timer / run loop)

- On a timer (e.g. every 10–20 ms): call **`engine.process_until_now()`**.
- The engine will advance over due events and call **`on_event(msg)`** for each message that passes mute/suppress. The worker (or whoever implements `on_event`) must **send** that message (e.g. `msg.bytes()` to the port).
- Does **not** walk a separate buffer, **not** compute message times from tempo, **not** apply mute/suppress. Only: call `process_until_now()`, and in `on_event` send the message.

### Transport (play / pause / stop / scrub)

- **Play** (from stopped or paused): call **`engine.start(start_tick)`**. Typically `start_tick` is 0 or the current scrub position. The worker will then drive playback by calling `process_until_now()` on its timer.
- **Pause**: **Stop calling `engine.process_until_now()`** (and optionally call **`engine.stop()`** if you want the engine to mark “not playing”). Do not advance the event index; the engine’s position is preserved until the next `start(...)` or `scrub_to_tick(...)`.
- **Stop**: call **`engine.stop()`**. Optionally call **`engine.scrub_to_tick(0)`** (or current start) to reset position for the next play.
- **Scrub / seek**: call **`engine.scrub_to_tick(tick)`** so the next `start(...)` or the next `process_until_now()` continues from that tick.

Transport does **not** compute start index or tempo; the engine does that in `start()` and `process_until_now()`.

### Engine

- **`load_file(midi_file)`**: Builds event list, tempo map, time map; resets playback state. Mute/suppress settings are left unchanged.
- **`start(start_tick)`**: Sets play position to `start_tick`, records start time, marks playing. Worker then drives by calling `process_until_now()`.
- **`process_until_now()`**: Advances over events whose scheduled time has passed; for each event that passes `_should_send` (track mute, channel mute, suppress program/control), calls **`on_event(msg)`**. Stops itself when the event list is exhausted (and sets internal “not playing”).
- **`stop()`**: Marks not playing. Does not clear position.
- **`scrub_to_tick(tick)`**: Sets play position to `tick` and resets start time so the next `process_until_now()` uses that position.
- **`on_event`**: Callback set by the owner; engine invokes it with a `mido.Message` when a message is due and not filtered. Owner must send that message to the MIDI port (or elsewhere).

Tempo, event scheduling, and mute/suppress are entirely inside the engine. No other component should re-implement them.

---

## Summary diagram

```
Editor
  ├── load_file(midi_file) → engine.load_file(midi_file)
  ├── engine.on_event = worker.send_message  (or equivalent)
  ├── Mute / suppress UI → engine.mute_track / mute_channel / suppress_*
  └── Transport UI → transport.play() / pause() / stop() / scrub()

Transport
  ├── play()  → engine.start(start_tick)
  ├── pause() → stop calling process_until_now(); optionally engine.stop()
  ├── stop()  → engine.stop(); optionally engine.scrub_to_tick(0)
  └── scrub(tick) → engine.scrub_to_tick(tick)

Worker (timer)
  └── every 10–20 ms → engine.process_until_now()
                           └── engine calls on_event(msg) for each due, non-filtered message
                           └── worker (in on_event) sends msg to MIDI port
```

---

## Don’t

- **Worker**: Don’t maintain a separate `(tick, bytes, tempo)` buffer or compute message times from tempo. Use the engine as the only playback source.
- **Editor**: Don’t run `process_tracks` / buffer refill for playback once the engine is the source of truth; that path should be removed after switchover.
- **Transport**: Don’t compute start index or elapsed time; the engine does that in `start()` and `process_until_now()`.
- **Any**: Don’t duplicate mute/suppress logic; only the engine’s `_should_send` should filter events for playback.
