# Effects SysEx Address Map

Mapping between Perl `jdxi_manager.pl` addresses and JDXI Editor parameter definitions.

**Format:** Perl uses 4-byte addresses as hex strings (e.g. `18000200`). JDXI Editor uses:
- **Base:** `JDXiSysExAddress(MSB=0x18, UMB=0x00, LMB=section, LSB=0)`
- **Section LMB:** Effect1=0x02, Effect2=0x04, Delay=0x06, Reverb=0x08
- **Param offset:** Added to LSB (and sometimes UMB for 4-byte params)

**Roland SysEx structure:** `F0 41 10 00 00 00 0E 12 [addr4] [data...] F7`

---

## Address Format Conversion

| Perl (hex string) | Bytes (MSB UMB LMB LSB) | JDXI Editor base + param |
|-------------------|------------------------|---------------------------|
| 18000200          | 18 00 02 00            | Effect1 base, param 0x00 |
| 18000400          | 18 00 04 00            | Effect2 base, param 0x00 |
| 18000600          | 18 00 06 00            | Delay base, param 0x00   |
| 18000800          | 18 00 08 00            | Reverb base, param 0x00  |

**JDXI Editor base address:**
```python
JDXiSysExAddress(
    JDXiSysExAddressStartMSB.TEMPORARY_PROGRAM,  # 0x18
    JDXiSysExOffsetSystemUMB.COMMON,             # 0x00
    JDXiSysExOffsetProgramLMB.COMMON,            # 0x00
    0
).add_offset((0, section_lmb, 0))
# section_lmb: EFFECT_1=0x02, EFFECT_2=0x04, DELAY=0x06, REVERB=0x08
```

---

## Effect 1 (LMB=0x02, base 18000200)

| Perl addr | Param offset | Perl label              | JDXI Editor param              | Status   |
|-----------|--------------|-------------------------|---------------------------------|----------|
| 18000200  | 0x00         | Effect Type            | Effect1Param.EFX1_TYPE          | ✓ Match  |
| 18000201  | 0x01         | Effect 1 Level         | Effect1Param.EFX1_LEVEL         | ✓ Match  |
| 18000202  | 0x02         | Delay send level       | Effect1Param.EFX1_DELAY_SEND_LEVEL | ✓ Match |
| 18000203  | 0x03         | Reverb send level      | Effect1Param.EFX1_REVERB_SEND_LEVEL | ✓ Match |
| 18000204  | 0x04         | Output Assign          | Effect1Param.EFX1_OUTPUT_ASSIGN | ✓ Match  |
| 18000211  | 0x11         | Level / Threshold / etc| Effect1Param.EFX1_PARAM_1 (type-specific) | ✓ |
| 18000215  | 0x15         | Drive / Ratio / etc    | Effect1Param.EFX1_PARAM_2       | ✓        |
| 18000219  | 0x19         | Type / Attack / etc    | Effect1Param.EFX1_PARAM_3       | ✓        |
| 1800021D  | 0x1D         | Presence / Release / etc | Effect1Param.EFX1_PARAM_4 / EFX1_PARAM_32 | ✓ |
| 18000221  | 0x21         | Level (Compressor)     | Effect1Param.EFX1_PARAM_5       | ✓        |
| 18000225  | 0x25         | Side Chain On/Off      | Effect1Param.EFX1_PARAM_7       | ⚠ Missing UI |
| 18000229  | 0x29         | Side Level             | Effect1Param.EFX1_PARAM_7_COMPRESSOR_SIDE_LEVEL | ✓ |
| 1800022D  | 0x2D         | Side Note              | Effect1Param.EFX1_PARAM_8_COMPRESSOR_SIDE_NOTE | ✓ (needs note dropdown) |
| 18000231  | 0x31         | Side Time [ms]         | Effect1Param.EFX1_PARAM_9_COMPRESSOR_SIDE_TIME | ✓ |
| 18000235  | 0x35         | Side Release           | Effect1Param.EFX1_PARAM_10_COMPRESSOR_SIDE_RELEASE | ✓ |
| 18000239  | 0x39         | Side Sync On/Off       | Effect1Param.EFX1_PARAM_11      | ⚠ Missing UI |

---

## Effect 2 (LMB=0x04, base 18000400)

| Perl addr | Param offset | Perl label              | JDXI Editor param              | Status   |
|-----------|--------------|-------------------------|---------------------------------|----------|
| 18000400  | 0x00         | Effect Type             | Effect2Param.EFX2_TYPE         | ✓ Match  |
| 18000401  | 0x01         | Effect 2 Level          | Effect2Param.EFX2_LEVEL         | ✓ Match  |
| 18000402  | 0x02         | Delay send level        | Effect2Param.EFX2_DELAY_SEND_LEVEL | ✓ Match |
| 18000403  | 0x03         | Reverb send level       | Effect2Param.EFX2_REVERB_SEND_LEVEL | ✓ Match |
| 18000411  | 0x11         | Rate/Note switch       | Effect2Param.EFX2_PARAM_1_FLANGER/PHASER_RATE_NOTE_SWITCH | ✓ |
| 18000415  | 0x15         | Rate / Sens / etc       | Effect2Param.EFX2_PARAM_2       | ✓        |
| 18000419  | 0x19         | Note / Balance / etc    | Effect2Param.EFX2_PARAM_3       | ✓        |
| 1800041D  | 0x1D         | Depth / Level / etc     | Effect2Param.EFX1_PARAM_4       | ✓        |
| 18000421  | 0x21         | Feedback / Resonance   | Effect2Param.EFX2_PARAM_5      | ✓        |
| 18000425  | 0x25         | Manual                 | Effect2Param.EFX2_PARAM_6       | ✓        |
| 18000429  | 0x29         | Balance / Level        | Effect2Param.EFX2_PARAM_7       | ✓        |
| 1800042D  | 0x2D         | Level (Flanger)        | Effect2Param.EFX2_PARAM_8      | ✓        |

---

## Delay (LMB=0x06, base 18000600)

| Perl addr | Param offset | Perl label        | JDXI Editor param       | Status      |
|-----------|--------------|-------------------|-------------------------|-------------|
| 18000600  | 0x00         | On/Off            | —                       | ❌ Missing  |
| 18000603  | 0x03         | Reverb send level | DelayParam.DELAY_REVERB_SEND_LEVEL (0x06) | ⚠ Addr mismatch |
| 18000604  | 0x04         | Type (SINGLE/PAN) | —                       | ❌ Missing  |
| 18000608  | 0x08         | Time/Note mode    | DelayParam.DELAY_PARAM_1 (0x08) | ⚠ Label wrong |
| 1800060C  | 0x0C         | Time [ms]         | DelayParam.DELAY_PARAM_2 (0x0C) | ⚠ Label wrong |
| 18000610  | 0x10         | Note              | —                       | ❌ Missing  |
| 18000614  | 0x14         | Tap Time [%]      | —                       | ❌ Missing  |
| 18000618  | 0x18         | Feedback [%]      | —                       | ❌ Missing (DELAY_PARAM_24=0x60) |
| 1800061C  | 0x1C         | HF Damp           | —                       | ❌ Missing  |
| 18000620  | 0x20         | Level             | DelayParam.DELAY_LEVEL (0x01)   | ⚠ Addr mismatch |

**Critical:** JDXI Editor Delay param addresses do not align with Perl. `DELAY_LEVEL` at 0x01 vs Perl Level at 0x20; `DELAY_REVERB_SEND_LEVEL` at 0x06 vs Perl at 0x03; `DELAY_PARAM_24` at 0x60 vs Perl Feedback at 0x18. **Verify against JD-Xi Parameter Guide before changing.**

---

## Reverb (LMB=0x08, base 18000800)

| Perl addr | Param offset | Perl label   | JDXI Editor param    | Status      |
|-----------|--------------|--------------|----------------------|-------------|
| 18000800  | 0x00         | On/Off       | —                    | ❌ Missing  |
| 18000803  | 0x03         | Type        | ReverbParam.REVERB_LEVEL (0x03) | ⚠ Addr/meaning mismatch |
| 18000807  | 0x07         | Time        | ReverbParam.REVERB_PARAM_1 (0x07) | ✓ Match |
| 1800080B  | 0x0B         | HF Damp     | ReverbParam.REVERB_PARAM_2 (0x0B) | ✓ Match |
| 1800080F  | 0x0F         | Level       | ReverbParam.REVERB_PARAM_24 (0x5F) | ⚠ Addr mismatch |

**Note:** Perl has Reverb Level at 0x0F; JDXI Editor `REVERB_LEVEL` is at 0x03. `REVERB_PARAM_24` at 0x5F does not match Perl 0x0F. **Verify against JD-Xi Parameter Guide.**

---

## 4-Byte (Signed) Parameters

Many effect params use 4-byte signed values. Perl uses `+32768` offset (display 0–127 maps to SysEx 32768–32895). JDXI Editor uses `convert_to_midi` with `Midi.value.min.SIGNED_SIXTEEN_BIT` (32768) for these params.

---

## References

- `doc/perl/jdxi_manager.pl` (FX_DEL_Frame, FX_REV_Frame, FX1_*, FX2_*)
- `doc/perl/JDXidata.pm` (lookup tables)
- `jdxi_editor/midi/data/parameter/effects/effects.py`
- `jdxi_editor/midi/data/address/address.py` (JDXiSysExOffsetProgramLMB)
- Roland JD-Xi Parameter Guide (recommended for final validation)
