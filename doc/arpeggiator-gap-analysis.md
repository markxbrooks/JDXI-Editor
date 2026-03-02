# Arpeggiator Gap Analysis: JDXI-Editor vs Perl vs Roland PDF

Compares the JDXI-Editor (Python) and Perl (`jdxi_manager.pl`) arpeggiator implementations against the Roland MIDI Implementation Guide (Program Zone and Program Controller blocks).

**Reference:** Roland JD-Xi MIDI Implementation, `doc/perl/jdxi_manager.pl`, `doc/perl/JDXidata.pm`

---

## Roland PDF Spec Summary

### Program Zone (per-zone, 4 zones: Digital Synth 1/2, Analog, Drum)

| Offset | Size | Description | Values |
|--------|------|-------------|--------|
| 00 00 - 00 02 | - | (reserve) | - |
| **00 03** | 1 | **Arpeggio Switch** | 0-1: OFF, ON |
| 00 04 - 00 18 | - | (reserve) | - |
| **00 19** | 1 | **Zone Octave Shift** | 61-67: -3 to +3 |
| 00 1A - 00 22 | - | (reserve) | - |
| **Total Size** | **0x23 (35 bytes)** | | |

### Program Controller (global arpeggiator)

| Offset | Size | Description | Values |
|--------|------|-------------|--------|
| 00 00 | 1 | (reserve) | - |
| **00 01** | 1 | **Arpeggio Grid** | 0-8: 04_, 08_, 08L, 08H, 08t, 16_, 16L, 16H, 16t |
| **00 02** | 1 | **Arpeggio Duration** | 0-9: 30, 40, 50, 60, 70, 80, 90, 100, 120, FUL |
| **00 03** | 1 | **Arpeggio Switch** | 0-1: OFF, ON |
| 00 04 | 1 | (reserve) | - |
| **00 05** | 1 | **Arpeggio Style** | 0-127: 1-128 |
| **00 06** | 1 | **Arpeggio Motif** | 0-11: UP/L, UP/H, UP/_, dn/L, dn/H, dn/_, Ud/L, Ud/H, Ud/_, rn/L, rn/_, PHRASE |
| **00 07** | 1 | **Arpeggio Octave Range** | 61-67: -3 to +3 |
| 00 08 | 1 | (reserve) | - |
| **00 09** | 1 | **Arpeggio Accent Rate** | 0-100 |
| **00 0A** | 1 | **Arpeggio Velocity** | 0-127: REAL, 1-127 |
| 00 0B | 1 | (reserve) | - |
| **Total Size** | **0x0C (12 bytes)** | | |

**SysEx Address:** `18 00 40 00` (Program Controller)

---

## Perl Implementation (`jdxi_manager.pl` / `JDXidata.pm`)

### Coverage

| Area | Perl | Address | Size |
|------|------|---------|------|
| **Program Controller** | ✅ Full | `\x18\x00\x40\x00` | 12 bytes |
| **Program Zone** | ❌ Not implemented | - | - |

### Program Controller Parameters (Perl)

| Param | Offset | Perl Var | Perl Labels | Status |
|-------|--------|----------|-------------|--------|
| Grid | 0x01 | `$ARPdata[0x01]` | `@arp_grid`: 1/4, 1/8, 1/8 L, 1/8 H, 1/12, 1/16, 1/16 L, 1/16 H, 1/24 | ✅ Matches Roland |
| Duration | 0x02 | `$ARPdata[0x02]` | `@arp_duration`: 30%, 40%, ..., 120%, Full | ✅ Matches Roland |
| Switch | 0x03 | `$ARPdata[0x03]` | On/Off | ✅ |
| Style | 0x05 | `$ARPdata[0x05]` | `@arp_type`: 001-128 with names | ✅ |
| Motif | 0x06 | `$ARPdata[0x06]` | `@arp_motif`: Up (L), Up (L&H), ..., Phrase | ✅ Matches Roland |
| Octave Range | 0x07 | `$ARPdata[0x07]` | -3 to +3 (transf64) | ✅ |
| Accent | 0x09 | `$ARPdata[0x09]` | 0-100 | ✅ |
| Velocity | 0x0A | `$ARPdata[0x0A]` | 0-127 (0=Real) | ✅ |

### Perl Grid Label Mapping (Roland → Perl)

| Roland | Perl | Index |
|--------|------|-------|
| 04_ | 1/4 | 0 |
| 08_ | 1/8 | 1 |
| 08L | 1/8 L | 2 |
| 08H | 1/8 H | 3 |
| 08t | 1/12 | 4 |
| 16_ | 1/16 | 5 |
| 16L | 1/16 L | 6 |
| 16H | 1/16 H | 7 |
| 16t | 1/24 | 8 |

---

## JDXI-Editor (Python) Implementation

### Coverage

| Area | Python | Address | Size |
|------|--------|---------|------|
| **Program Controller** | ✅ Full | `18 00 40 00` | 12 bytes |
| **Program Zone** | ⚠️ Partial | `ProgramZoneParam` defined | ❌ Not synced in UI |

### Program Controller Parameters (Python)

| Param | Offset | ArpeggioParam | Status |
|-------|--------|---------------|--------|
| Grid | 0x01 | `ARPEGGIO_GRID` | ⚠️ **Bug: ArpeggioGrid enum has 7 values, wrong labels** |
| Duration | 0x02 | `ARPEGGIO_DURATION` | ✅ |
| Switch | 0x03 | `ARPEGGIO_SWITCH` | ✅ |
| Style | 0x05 | `ARPEGGIO_STYLE` | ✅ |
| Motif | 0x06 | `ARPEGGIO_MOTIF` | ⚠️ Combo uses `motif.name` (UP_L) not display_name |
| Octave Range | 0x07 | `ARPEGGIO_OCTAVE_RANGE` | ✅ |
| Accent | 0x09 | `ARPEGGIO_ACCENT_RATE` | ✅ |
| Velocity | 0x0A | `ARPEGGIO_VELOCITY` | ✅ |

### Program Zone Parameters (Python)

| Param | Offset | ProgramZoneParam | Status |
|-------|--------|------------------|--------|
| Arpeggio Switch | 0x03 | `ARPEGGIO_SWITCH` | ✅ Defined, ❌ Not synced in editor |
| Zone Octave Shift | 0x19 | `ZONAL_OCTAVE_SHIFT` | ✅ Defined, ❌ Not synced in editor |

---

## Gaps and Issues

### 🔴 P1: ArpeggioGrid Enum Mismatch (Python)

**File:** `jdxi_editor/midi/data/arpeggio/arpeggio.py`

**Problem:** `ArpeggioGrid` enum has only **7 values** (0-6) with wrong labels:

| Python (current) | Roland (correct) |
|------------------|------------------|
| 1/4, 1/8, 1/8 Triplet, 1/16, 1/16 Triplet, 1/32, 1/32 Triplet | 1/4, 1/8, 1/8 L, 1/8 H, 1/12, 1/16, 1/16 L, 1/16 H, 1/24 |

**Fix:** Replace `ArpeggioGrid` enum with the correct 9-value mapping from `jdxi_editor/midi/data/arpeggio/data.py` (which already has `ARPEGGIO_GRID` correct). The ArpeggioEditor uses `ArpeggioGrid` for combo options; switch to `ARPEGGIO_GRID` from data.py.

### 🟡 P2: Motif Combo Display (Python)

**File:** `jdxi_editor/ui/editors/arpeggio/arpeggio.py` line ~276

**Problem:** `ComboBoxSpec(P.ARPEGGIO_MOTIF, ..., [motif.name for motif in ArpeggioMotif])` uses enum names (UP_L, UP_H) instead of display names (Up (L), Up (L&H)).

**Fix:** Use `[motif.display_name for motif in ArpeggioMotif]` or `ARPEGGIO_MOTIF` from data.py.

### 🟡 P3: Program Zone Not Synced (Python)

**Problem:** Program Zone (per-zone Arpeggio Switch, Zone Octave Shift) is defined in `ProgramZoneParam` but:
- No SysEx request for Program Zone
- No UI to edit per-zone Arpeggio Switch or Zone Octave Shift
- ArpeggioEditor uses `ProgramZoneParam.ARPEGGIO_SWITCH` for one switch but it is not wired to Zone SysEx

**Note:** Perl also does not implement Program Zone. Both are missing this.

### 🟢 Parity: Program Controller

Both Perl and Python implement Program Controller correctly for the core parameters. The Perl address `18004000` matches Python `18 00 40 00`. Size 12 bytes.

---

## Recommended Actions

| Priority | Action | Effort | Status |
|----------|--------|--------|--------|
| P1 | Fix ArpeggioGrid: use 9-value ARPEGGIO_GRID from data.py in ArpeggioEditor combo | Low | ✅ Done |
| P2 | Fix Motif combo: use display_name instead of motif.name | Low | ✅ Done |
| P3 | (Optional) Add Program Zone SysEx + UI for per-zone Arpeggio Switch and Zone Octave Shift | Medium | ✅ Done |

---

## File Reference

| Component | Perl | Python |
|-----------|------|--------|
| Arpeggio data | `JDXidata.pm`: @arp_grid, @arp_duration, @arp_motif, @arp_type | `data/arpeggio/data.py`: ARPEGGIO_GRID, ARP_DURATION, ARPEGGIO_MOTIF, ARPEGGIO_STYLE |
| Arpeggio params | `JDXidata.pm`: %ARP, @ARPdata | `data/parameter/arpeggio.py`: ArpeggioParam |
| Arpeggio UI | `jdxi_manager.pl`: ARP_Frame() | `ui/editors/arpeggio/arpeggio.py`: ArpeggioEditor |
| Zone params | - | `data/parameter/program/zone.py`: ProgramZoneParam |
