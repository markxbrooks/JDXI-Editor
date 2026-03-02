# Vocal Effects midi_requests Gap Analysis

Comparison of Vocal Effects Editor `midi_requests` vs Perl `jdxi_manager.pl`.

---

## Perl (jdxi_manager.pl) — Expected Behavior

From `doc/midi-parameters-gap-analysis.md`, `doc/vocal-effects-migration-plan.md`:

| Block              | Address      | Size        |
|--------------------|--------------|-------------|
| Program Common     | 18 00 00 00  | 0x40 (64)   |
| Program Vocal Effect | 18 00 01 00 | 0x18 (24)   |

The Vocal FX tab needs both:
- **Program Common** — VOCAL_EFFECT (0x1C), VOCAL_EFFECT_PART (0x1D), AUTO_NOTE_SWITCH (0x1E), VOCAL_EFFECT_NUMBER (0x1B)
- **Program Vocal Effect** — Level, Pan, Delay/Reverb send, Output Assign, Vocoder params, Auto Pitch params (0x00–0x13)

---

## JDXI Editor — Current Implementation

### VocalFXEditor (`jdxi_editor/ui/editors/effects/vocal.py`)

```python
self.midi_requests = [
    MidiRequests.PROGRAM_COMMON,
    MidiRequests.PROGRAM_VOCAL_EFFECT,
]
```

### MidiRequests

| Request                 | Address      | Size   | Hex definition                          |
|-------------------------|--------------|--------|-----------------------------------------|
| PROGRAM_COMMON          | 18 00 00 00  | 0x40   | `PROGRAM_COMMON_AREA="00"` + `"00 00 00 00 00 40"` |
| PROGRAM_VOCAL_EFFECT    | 18 00 01 00  | 0x18   | `PROGRAM_VOCAL_EFFECT_AREA="01"` + `"00 00 00 00 00 18"` |

### Hex (`jdxi_editor/midi/sysex/request/hex.py`)

```python
PROGRAM_VOCAL_EFFECT_AREA = "01"  # LMB=0x01 → address 18 00 01 00
```

### create_request part

```python
"00 00 00 00 00 18"  # size 0x18 = 24 bytes
```

---

## Comparison Summary

| Aspect              | Perl              | JDXI Editor       | Status |
|---------------------|-------------------|-------------------|--------|
| Program Common      | 18 00 00 00, 64B  | 18 00 00 00, 64B  | ✓ Match |
| Program Vocal Effect| 18 00 01 00, 24B  | 18 00 01 00, 24B  | ✓ Match |
| Request on show     | Both blocks       | Both blocks       | ✓ Match |
| _dispatch_sysex_to_area | COMMON + VOCAL_EFFECT | COMMON + VOCAL_EFFECT | ✓ Match |

---

## Conclusion

**Vocal Effects `midi_requests` match the Perl version.** No changes needed.

- Address 18 00 01 00 with size 0x18 (24 bytes) is correct for Program Vocal Effect.
- Requesting both PROGRAM_COMMON and PROGRAM_VOCAL_EFFECT is correct, since the editor uses parameters from both areas.
- `showEvent` → `data_request()` sends both requests when the Vocal FX tab is opened.

---

## Note: Main Instrument Ctrl-R

As with the Effects Editor, the main instrument window’s Ctrl-R (`instrument.py` `data_request`) uses `MidiRequests.PROGRAM_TONE_NAME_PARTIAL`, which includes PROGRAM_COMMON but **not** PROGRAM_VOCAL_EFFECT. Vocal Effect data is only requested when the Vocal FX editor tab is opened via its own `showEvent`. This matches the per-editor request pattern used for other editors (Digital, Analog, Drums, Effects).
