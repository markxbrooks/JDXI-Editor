# Effects Editor Gap Analysis

Checklist of missing parameters and features vs. Perl `jdxi_manager.pl`. Use to track Phase 1+ implementation.

**Source:** `doc/perl/jdxi_manager.pl`, `doc/perl/JDXidata.pm`  
**Address reference:** `doc/effects-sysex-address-map.md`

---

## Effect 1

| Parameter              | Perl addr | JDXI Editor status | EffectsData / enum needed |
|------------------------|-----------|--------------------|---------------------------|
| Type                   | 0x00      | ✓ Present          | —                         |
| Level                  | 0x01      | ✓ Present          | —                         |
| Delay send             | 0x02      | ✓ Present          | —                         |
| Reverb send            | 0x03      | ✓ Present          | —                         |
| Output Assign          | 0x04      | ✓ Present          | —                         |
| **Distortion/Fuzz**    |           |                    |                           |
| Type (0–5)             | 0x19      | ✓ Present          | —                         |
| Drive                  | 0x15      | ✓ Present          | —                         |
| Presence               | 0x1D      | ✓ Present          | —                         |
| Level                  | 0x11      | ✓ Present          | —                         |
| **Compressor**         |           |                    |                           |
| Ratio                  | 0x15      | ✓ Present          | `compression_ratios` ✓    |
| Threshold              | 0x11      | ✓ Present          | —                         |
| Attack                 | 0x19      | ✓ Present          | `compression_attack_times` ✓ |
| Release                | 0x1D      | ✓ Present          | `compression_release_times` ✓ |
| Level                  | 0x21      | ✓ Present          | —                         |
| Side Chain On/Off      | 0x25      | ✅ Phase 3         | —                         |
| Side Sync On/Off       | 0x39      | ✅ Phase 3         | —                         |
| Side Level             | 0x29      | ✓ Present          | —                         |
| Side Note              | 0x2D      | ✅ Phase 3         | `coarse_tune` combo       |
| Side Time [ms]         | 0x31      | ✓ Present          | —                         |
| Side Release           | 0x35      | ✓ Present          | —                         |
| **Bit Crusher**        |           |                    |                           |
| Rate                   | 0x15      | ✓ Present          | —                         |
| Bit                    | 0x19      | ✓ Present          | —                         |
| Filter                 | 0x1D      | ✓ Present          | —                         |
| Level                  | 0x11      | ✓ Present          | —                         |

---

## Effect 2

| Parameter              | Perl addr | JDXI Editor status | EffectsData / enum needed |
|------------------------|-----------|--------------------|---------------------------|
| Type                   | 0x00      | ✓ Present          | —                         |
| Level                  | 0x01      | ✓ Present          | —                         |
| Delay send             | 0x02      | ✓ Present          | —                         |
| Reverb send            | 0x03      | ✓ Present          | —                         |
| **Flanger**            |           |                    |                           |
| Rate/Note switch       | 0x11      | ✓ Present          | `rate_note_states` ✓      |
| Note                   | 0x19      | ✓ Present          | `flanger_notes` ✓         |
| Rate                   | 0x15      | ✓ Present          | —                         |
| Depth                  | 0x1D      | ✓ Present          | —                         |
| Feedback               | 0x21      | ✓ Present          | —                         |
| Manual                 | 0x25      | ✓ Present          | —                         |
| Balance                | 0x29      | ✓ Present          | —                         |
| Level                  | 0x2D      | ✓ Present          | —                         |
| **Phaser**             |           |                    |                           |
| Rate/Note switch       | 0x11      | ✓ Present          | —                         |
| Note                   | 0x19      | ✓ Present          | —                         |
| Rate                   | 0x15      | ✓ Present          | —                         |
| Depth                  | 0x1D      | ✓ Present          | —                         |
| Resonance (0x21)       | 0x21      | ✓ (as Center Freq)  | Verify label              |
| Manual                 | 0x25      | ✓ Present          | —                         |
| Level                  | 0x29/0x0D | ✓ Present          | —                         |
| **Ring Mod**           |           |                    |                           |
| Frequency              | 0x11      | ✓ Present          | —                         |
| Sens                   | 0x15      | ✓ Present          | —                         |
| Balance                | 0x19      | ✓ Present          | —                         |
| Level                  | 0x1D      | ✓ Present          | —                         |
| **Slicer**             |           |                    |                           |
| Timing Pattern         | 0x11      | ✓ Present          | —                         |
| Rate [Note]            | 0x15      | ✓ Present          | `flanger_notes` ✓         |
| Attack                 | 0x19      | ✓ Present          | —                         |
| Trigger Level          | 0x1D      | ✓ Present          | —                         |
| Level                  | 0x21      | ✓ Present          | —                         |

---

## Delay

| Parameter              | Perl addr | JDXI Editor status | EffectsData / enum needed |
|------------------------|-----------|--------------------|---------------------------|
| On/Off                 | 0x00      | ✅ Phase 2         | —                         |
| Type (SINGLE/PAN)      | 0x04      | ✅ Phase 2         | `delay_types`             |
| Time/Note mode         | 0x08      | ✅ Phase 2         | `delay_time_note_modes`   |
| Reverb send level      | 0x03      | ✅ Phase 2         | —                         |
| Time [ms]              | 0x0C      | ✅ Phase 2         | —                         |
| Note                   | 0x10      | ✅ Phase 2         | `delay_notes`             |
| Tap Time [%]           | 0x14      | ✅ Phase 2         | —                         |
| Feedback [%]           | 0x18      | ✅ Phase 2         | —                         |
| HF Damp                | 0x1C      | ✅ Phase 2         | `hf_damp`                 |
| Level                  | 0x01      | ✅ Phase 2         | —                         |

---

## Reverb

| Parameter              | Perl addr | JDXI Editor status | EffectsData / enum needed |
|------------------------|-----------|--------------------|---------------------------|
| On/Off                 | 0x00      | ✅ Phase 2          | —                         |
| Type                   | 0x03      | ✅ Phase 2          | `rev_type`                |
| Time                   | 0x07      | ✅ Phase 2          | —                         |
| HF Damp                | 0x0B      | ✅ Phase 2          | `hf_damp`                 |
| Level                  | 0x01      | ✅ Phase 2          | —                         |

---

## EffectsData Extensions Needed

| Table        | Perl source   | Status      |
|--------------|---------------|-------------|
| `rev_type`   | @rev_type     | ✅ Added (Phase 1) |
| `hf_damp`    | @hf_damp      | ✅ Added (Phase 1) |
| `delay_types`| ['SINGLE','PAN'] | ✅ Added (Phase 1) |
| `delay_time_note_modes` | ['Time','Note'] | ✅ Added (Phase 1) |
| `coarse_tune`| @coarse_tune  | ✅ Added (Phase 1) |
| `flanger_notes` | @dly_notes  | ✓ Present (22 entries) |
| `delay_notes` | alias to flanger_notes | ✅ Added (Phase 1) |

---

## Architecture / UX Gaps

| Feature                    | Perl                         | JDXI Editor              |
|----------------------------|------------------------------|---------------------------|
| Polymorphic effect UI      | Dynamic frame per type       | Show/hide controls       |
| Effect type change trigger | Rebuilds frame               | Updates labels/visibility |
| Layout                     | 2-column (EFX1\|EFX2, DLY\|REV) | Tabbed |

---

## Phase 0 Validation Notes

- **Delay addresses:** JDXI Editor `DELAY_LEVEL` (0x01), `DELAY_REVERB_SEND_LEVEL` (0x06), `DELAY_PARAM_24` (0x60) do not match Perl. Confirm with JD-Xi Parameter Guide before changing.
- **Reverb addresses:** `REVERB_LEVEL` (0x03) may overlap with Type in Perl. `REVERB_PARAM_24` (0x5F) vs Perl Level (0x0F). Verify.
- **4-byte params:** Both use +32768 offset for signed display. Conversion logic appears correct.
