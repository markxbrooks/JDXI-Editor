# JDXI-Editor Features and Usage

This document covers recent changes, patch loading/saving, and SoundFont usage.

---

## 1. Recent Changes (from Changelog)

### Arpeggiator SysEx Sync

- **Bidirectional SysEx**: Arpeggio Editor receives and displays incoming Program Controller SysEx; requests data on show
- **Parameter mapping**: `(TEMPORARY_PROGRAM, CONTROLLER)` → `ArpeggioParam` for correct parsing
- **Value handling**: Fixed ComboBox vs Slider in `_dispatch_sysex_to_area` (ComboBox uses raw MIDI value; Slider uses display value)
- **Patch apply**: `send_json_patch_to_instrument` handles CONTROLLER for Arpeggio patches
- **RQ1 request**: `MidiRequests.PROGRAM_CONTROLLER` for address 18 00 40 00, size 0x0C (12 bytes)

### Effects Editor (Phases 1–6)

- **Delay & Reverb**: Full parameter set with Time/Note mode, Note dropdown, HF Damp
- **Compressor**: Side Chain, Side Sync switches; Side Note as coarse_tune combo
- **Polymorphic UI**: Effect 1 and Effect 2 use QStackedWidget—one page per effect type
- **Layout**: 2-column grid (EFX1|EFX2, Delay|Reverb)
- **Phaser**: Renamed "Center Freq" to "Resonance" (0x21)
- **Polish**: Tooltips for key controls; "Balance [dry->wet]" labeling

### Vocal Effects (Phases 1–3)

- **Addresses**: VOCAL_EFFECT 0x16→0x1C (per JD-Xi guide)
- **SysEx routing**: apply_lmb_offset routes ProgramCommonParam to LMB=COMMON
- **VocalFXParam**: Fixed convert_to_midi/convert_from_midi for Pan, Gender, Octave
- **Data on show**: Requests PROGRAM_COMMON and PROGRAM_VOCAL_EFFECT; receives COMMON and VOCAL_EFFECT SysEx
- **Polymorphic UI**: QStackedWidget for OFF/VOCODER/AUTO-PITCH; 3 tabs — Common, Vocoder & Auto Pitch, Mixer

---

## 2. Patch Loading and Saving

### Supported Formats

| Format | Load | Save | Description |
|--------|------|------|-------------|
| **.jsz** | ✓ | ✓ | Patch bundle (ZIP of JSON files) |
| **.msz** | ✓ | ✓ | Music bundle (patch + MIDI file) |
| **.json** | ✓ | ✓ | Single JSON patch file |
| **.syx** | ✓ | ✓ | Raw Roland SysEx (DT1 messages concatenated) |

### Save Flow

1. **File → Save Patch...** — Open the file dialog
2. Choose format by extension: `.jsz`, `.msz`, `.syx`, or `.json`
3. **.jsz / .msz**: Saves all editor parameters as JSON in a ZIP; `.msz` also includes the loaded MIDI file (if any)
4. **.syx**: Converts current UI values to SysEx DT1 messages and writes binary; compatible with SysEx librarians and other Roland editors

### Load Flow

1. **File → Load Patch...** — Select a file
2. **.jsz / .msz**: Extracts JSON files, sends each to the instrument via SysEx
3. **.json**: Sends single patch to the instrument
4. **.syx**: Reads binary, splits on F0…F7 boundaries, sends each SysEx message to the instrument

### Editors Included in Save

| Editor | Included |
|--------|----------|
| Digital Synth 1 & 2 | Yes (Common + Modify sections) |
| Drum Kit | Yes (Common + Partials) |
| Analog Synth | Yes |
| Effects | Yes (Effect1, Effect2, Delay, Reverb) |
| Vocal FX | Yes |
| Arpeggiator | Yes |
| Pattern Sequencer | No |
| Program Editor | No |
| MIDI File Player | MIDI saved separately in .msz |

### Save Source

The editor **saves from the current UI control values** only. There is no "request current patch from synth" step before save. If a control was never updated from the synth, the saved value may not match the hardware.

For more detail, see [Patch Saving Gap Analysis](patch-saving-gap-analysis.md).

---

## 3. SoundFont Usage

### Overview

JDXI-Editor can use SoundFont (.sf2/.sf3) files for:

1. **FluidSynth playback** — Local software synth for MIDI playback without hardware
2. **Preset list source** — Use SoundFont preset names instead of built-in JD-Xi names (especially for Drums)

### Configuration

Open **MIDI Configuration** (gear icon or via menu) to access:

| Option | Description |
|--------|-------------|
| **Enable FluidSynth for local playback** | Uses FluidSynth for MIDI playback when no hardware is connected |
| **Use SoundFont List** | When enabled, preset names (especially Drums row) come from the configured SoundFont instead of built-in JD-Xi options |
| **Hardware Interface** | Audio output device for FluidSynth (requires `sounddevice`) |
| **SoundFont (SF2/SF3)** | Path to your .sf2 or .sf3 file (e.g. FluidR3_GM.sf2) |

### Use SoundFont List

- **Drums row**: When enabled, the Pattern editor Drums row shows GM percussion names (e.g. "Bass Drum 1", "Acoustic Snare") from the SoundFont instead of JD-Xi built-in names
- **Digital / Analog**: When enabled and a valid SF2 path is set, preset lists can be populated from the SoundFont (bank 0 melodic, bank 128 for drum kits)
- **Fallback**: If the path is invalid or the file cannot be read, built-in JD-Xi presets are used

### Default Path

The default SoundFont path is `~/SoundFonts/FluidR3_GM.sf2` if that file exists. You can browse to select a different .sf2 or .sf3 file.

### Requirements

- **FluidSynth**: `pip install pyfluidsynth` (or `fluidsynth`)
- **SoundFont parsing** (for preset list): `pip install sf2utils`
- **Hardware interface selection**: `pip install sounddevice`

---

## Related Documentation

- [Patch Saving Gap Analysis](patch-saving-gap-analysis.md) — Detailed comparison with Perl editor, format notes
- [MSZ Bundle Format](../jdxi_editor/devel/MSZ_BUNDLE_FORMAT.md) — Music bundle structure
- [CHANGELOG](../CHANGELOG.md) — Full changelog
