# Changelog

All notable changes to JDXI-Editor are documented in this file.

## [Unreleased]

### Arpeggiator SysEx Sync

- **PARAMETER_ADDRESS_NAME_MAP**: Added `(TEMPORARY_PROGRAM, CONTROLLER)` → `ArpeggioParam` for correct Program Controller parsing
- **Phase 4**: Fixed ComboBox vs Slider value handling in `_dispatch_sysex_to_area` (ComboBox uses raw MIDI value; Slider uses display value)
- **helper.py**: Added CONTROLLER handling for `send_json_patch_to_instrument` (Arpeggio patch apply)
- **ArpeggioParam.get_by_name**: Added for param resolution in SysEx dispatcher
- **MidiRequests.PROGRAM_CONTROLLER**: RQ1 request for address 18 00 40 00, size 0x0C (12 bytes)
- **ArpeggioEditor**: `midi_requests`, `showEvent` → `data_request`, `midi_sysex_json` → `_dispatch_sysex_to_area`
- **Bidirectional SysEx**: Arpeggio Editor now receives and displays incoming Program Controller SysEx; requests data on show

### Effects Editor (Phases 1–6)

- **Data layer**: Added Delay/Reverb parameters (On/Off, Type, HF Damp, Time/Note mode), Compressor Side Chain/Side Sync, coarse_tune for Side Note
- **Delay & Reverb UI**: Full parameter set with Time/Note mode, Note dropdown, HF Damp
- **Compressor**: Side Chain, Side Sync switches; Side Note as coarse_tune combo
- **Polymorphic sections**: Effect 1 and Effect 2 use QStackedWidget—one page per effect type; no more show/hide
- **Layout**: 2-column grid (EFX1|EFX2, Delay|Reverb) via SimpleEditorHelper layout_mode="grid"
- **Phaser**: Renamed "Center Freq" to "Resonance" (0x21)
- **Polish**: Tooltips for key controls; "Balance [dry->wet]" labeling
- **Cleanup**: Removed efx1_param_labels, efx2_param_labels; fixed Phaser docstrings

### Vocal Effects (Phase 1)

- **Program Common addresses**: VOCAL_EFFECT 0x16→0x1C (per JD-Xi guide); VOCAL_EFFECT_NUMBER→0x1B (placeholder, undocumented)
- **SysEx routing**: apply_lmb_offset routes ProgramCommonParam to LMB=COMMON
- **VocalFXParam**: Fixed convert_to_midi/convert_from_midi for Pan, Gender, Octave; convert_from_display delegates to convert_to_midi
- **VocalEffectsData**: Tooltips for all vocal effect controls; "Balance [dry→wet]" label

### Vocal Effects (Phase 2)

- **data_request on show**: showEvent requests PROGRAM_COMMON and PROGRAM_VOCAL_EFFECT; MidiRequests.PROGRAM_VOCAL_EFFECT added
- **SysEx receive**: _dispatch_sysex_to_area updates controls from COMMON and VOCAL_EFFECT; JDXiMapSynthTone 0x01→VOCAL_EFFECT
- **VocalFXParam.get_by_name**: Added for param resolution in dispatcher

### Vocal Effects (Phase 3)

- **Polymorphic UI**: QStackedWidget for OFF/VOCODER/AUTO-PITCH; Vocal Effect combo switches stack page
- **Tab structure**: 3 tabs — Common, Vocoder & Auto Pitch, Mixer (replaces 4-tab layout)
- **Effect Part**: VOCAL_EFFECT_PART (Part 1/Part 2) in Common; removed VOCODER_SWITCH from Common
