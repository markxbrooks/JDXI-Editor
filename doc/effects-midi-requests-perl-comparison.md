# Effects MIDI Requests: Perl vs JDXI Editor Comparison

Compares the Perl version Effects RQ1 (Data Request) configuration with the JDXI Editor `midi_requests` to diagnose why the JD-Xi was not responding.

**Reference:** Perl FX config (addr, rqlen, datalen), `jdxi_editor/midi/sysex/request/`, Roland RQ1 SysEx format.

---

## Perl FX Config Summary

| Effect   | Address (addr)  | Request Size (rqlen) | Data Length (datalen) |
|----------|-----------------|----------------------|------------------------|
| Effect 1 | `\x18\x00\x02\x00` | `\x00\x00\x01\x11` (273) | 145 |
| Effect 2 | `\x18\x00\x04\x00` | `\x00\x00\x01\x11` (273) | 145 |
| Delay    | `\x18\x00\x06\x00` | `\x00\x00\x00\x64` (100) | 100 |
| Reverb   | `\x18\x00\x08\x00` | `\x00\x00\x00\x63` (99)  | 99  |

---

## JDXI Editor midi_requests — Before Fix

| Request           | Address (hex)   | Size (hex)    | Status  |
|-------------------|-----------------|---------------|---------|
| PROGRAM_EFFECT1   | 18 00 02 00     | 00 00 01 11   | ✓ Match |
| PROGRAM_EFFECT2   | 18 00 04 00     | 00 00 01 11   | ✓ Match |
| PROGRAM_DELAY     | 18 00 06 00     | 00 00 00 64   | ✓ Match |
| PROGRAM_REVERB    | 18 00 08 00     | 00 00 00 63   | ✓ Match |

**Address and size match Perl exactly.** The issue was the **Roland RQ1 checksum**.

---

## Root Cause: Incorrect Checksum

The Roland RQ1 checksum must cover all bytes from the **first byte after the command (0x11)** through the last data byte.

### Before Fix

`create_request` computed the checksum over `temp_area + part` only (e.g. `00 02 00 00 00 00 01 11`). It **excluded** the first address byte `0x18`, which is part of the header (`TEMPORARY_PROGRAM_RQ11_HEADER` ends with `18`).

Example for Effect 1:
- Bytes to checksum: `18 00 02 00 00 00 01 11` (8 bytes)
- Old checksum input: `00 02 00 00 00 00 01 11` (missing 0x18)
- Result: wrong checksum, JD-Xi rejects the message

### After Fix

`create_request` now includes the header’s last token (the first address byte) in the checksum input:

```python
checksum_data = f"{header.split()[-1]} {data}"
checksum = roland_checksum(checksum_data)
```

So for Effect 1:
- `checksum_data = "18 00 02 00 00 00 01 11"`
- Checksum is correct; JD-Xi should accept the request.

---

## File Changes

| File | Change |
|------|--------|
| `jdxi_editor/midi/sysex/request/factory.py` | `create_request` now uses `header.split()[-1]` in the checksum input |

---

## Roland RQ1 Format (Reference)

```
F0 41 10 00 00 00 0E  11  aa bb cc dd  ss tt uu vv  sum F7
   [  JD-Xi header  ]  cmd  [ address 4 ] [ size 4 ]  cks EOX
```

- **Command:** 0x11 (RQ1 = Data Request 1)
- **Address:** 4 bytes (aa bb cc dd), e.g. 18 00 02 00 for Effect 1
- **Size:** 4 bytes (ss tt uu vv), e.g. 00 00 01 11 for 273 bytes
- **Checksum:** (128 - (sum of address + size) % 128) % 128

---

## Validation

1. Open Effects Editor with JD-Xi connected.
2. Sliders should populate from the synth.
3. Check logs: no “Invalid checksum” or similar errors.

---

## Related

- `doc/effects-sysex-address-map.md` — Parameter address mapping
- `doc/effects-migration-plan.md` — Effects feature parity plan
