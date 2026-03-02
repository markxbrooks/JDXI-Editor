# Arbitrary Control Change & Program Change Sender — Plan

A plan for sending arbitrary MIDI Control Change (CC) and Program Change (PC) messages for testing, debugging, and manual control of the JD-Xi.

---

## Current State

| Component | Capability |
|-----------|------------|
| **MidiIOHelper** | `send_control_change(controller, value, channel)`, `send_program_change(program, channel)`, `send_bank_select_and_program_change(channel, msb, lsb, program)` |
| **MidiOutHandler** | `send_raw_message(message)` — accepts any bytes |
| **MIDIDebugger** | SysEx hex input + Send; decode; no CC/PC form |
| **MIDIMessageMonitor** | Log only; no send |

CC and PC are sent only through editor UI (sliders, preset buttons, etc.). There is no way to send arbitrary CC/PC for ad‑hoc testing.

---

## Options

### Option A: Extend MIDIDebugger (Recommended)

Add a **CC/PC tab** or **panel** to the existing MIDI SysEx Debugger.

**Pros:** Reuses existing window, menu entry, and MIDI helper; keeps debug tools in one place.  
**Cons:** Debugger is SysEx-focused; UI may become crowded.

**UI sketch:**
```
[CC/PC Tab]
  Channel:  [1 ▼]  (1–16)
  
  Control Change:
    Controller: [7  ]  (0–127)  Value: [100]  (0–127)  [Send CC]
  
  Program Change:
    Program: [0  ]  (0–127)  [Send PC]
  
  Bank Select + Program Change:
    Bank MSB: [0  ]  Bank LSB: [0  ]  Program: [0  ]  [Send Bank+PC]
```

---

### Option B: New "MIDI Sender" Window

Create a dedicated `MIDISenderWindow` or `CCPCSenderWindow`.

**Pros:** Focused UI; can grow (NRPN, SysEx presets, etc.) without cluttering the debugger.  
**Cons:** New menu item; another window to maintain.

**UI sketch:**
```
MIDI Sender
  Channel: [1 ▼]
  
  [Control Change]  Controller [__]  Value [___]  [Send]
  [Program Change]  Program [___]  [Send]
  [Bank Select]    MSB [__]  LSB [__]  [Send]
  [Bank + PC]      MSB [__]  LSB [__]  PC [___]  [Send]
  
  Quick CC presets: [Vol] [Pan] [Mod] [Sustain] ...
```

---

### Option C: Extend MIDIMessageMonitor

Add a send section below the log.

**Pros:** Monitor + send in one place; good for debugging.  
**Cons:** Monitor is read‑heavy; send UI may feel secondary.

---

### Option D: Command-Line / Script

Add a CLI or script, e.g. `jdxi_manager send-cc 7 100 --channel 1`.

**Pros:** Scriptable; CI/testing; no GUI.  
**Cons:** Requires port selection; less convenient for interactive use.

---

## Recommended Approach: Option A + D

1. **Phase 1:** Extend MIDIDebugger with a CC/PC panel (Option A).
2. **Phase 2 (optional):** Add a CLI subcommand for scripting (Option D).

---

## Implementation Plan (Option A)

### Phase 1: CC/PC Panel in MIDIDebugger

| Step | Task | Est. |
|------|------|------|
| 1.1 | Add `QTabWidget` to MIDIDebugger: "SysEx" (existing) and "CC/PC" (new) | 0.5h |
| 1.2 | Build CC/PC form: channel spinbox, controller/value for CC, program for PC | 1h |
| 1.3 | Wire Send CC → `midi_helper.send_control_change(controller, value, channel)` | 0.5h |
| 1.4 | Wire Send PC → `midi_helper.send_program_change(program, channel)` | 0.5h |
| 1.5 | Add Bank Select + PC section → `send_bank_select_and_program_change` | 0.5h |
| 1.6 | Optional: CC presets (e.g. Vol=7, Pan=10, Mod=1, Sustain=64) | 0.5h |
| 1.7 | Optional: hex input for raw CC/PC (e.g. `B0 07 64` = CC#7=100 on ch 1) | 1h |

### Phase 2: CLI (Optional)

| Step | Task | Est. |
|------|------|------|
| 2.1 | Add `send-cc`, `send-pc` subcommands to `jdxi_manager` entry point | 1h |
| 2.2 | Port selection (e.g. `--port "JD-Xi"` or `--port-index 0`) | 0.5h |
| 2.3 | Use `mido` to open port and send; no MidiIOHelper dependency | 1h |

---

## File Changes (Phase 1)

| File | Change |
|------|--------|
| `jdxi_editor/ui/windows/midi/debugger.py` | Add `QTabWidget`; add `_build_cc_pc_panel()` with form and send handlers |
| `jdxi_editor/midi/io/helper.py` | No change (methods exist) |
| `jdxi_editor/ui/windows/jdxi/ui.py` | Optional: rename menu to "MIDI Debugger (SysEx & CC/PC)" |

---

## Validation

1. Open Debug → MIDI SysEx Debugger → CC/PC tab.
2. Send CC#7 (Volume) = 100 on channel 1 → verify JD-Xi responds.
3. Send Program Change 0 on channel 1 → verify program change.
4. Send Bank Select (0, 0) + PC 0 → verify bank/program change.

---

## Future Extensions

- NRPN sender (CC#99, 98, 6, 38)
- SysEx hex input in CC/PC tab (or keep in SysEx tab)
- MIDI Learn: capture CC from hardware and show controller number
- Preset buttons for common JD-Xi CC mappings
