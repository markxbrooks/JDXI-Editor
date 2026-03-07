# Changelog

All notable changes to JDXI-Editor are documented in this file.

# [0.9.6] — 2026-03

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

### Pattern Editor — MIDI Load/Save (Phases 1–4)

- **Phase 1 — Button selectability**: `_update_button_states_for_beats_per_measure` after load; `ensure_measure_count` for measures; `_wire_button_clicks` on all measures
- **Phase 2 — Data consistency**: `sync_measure_to_ui` after load and on edit; `PatternMeasure.steps` kept in sync with button state for copy/paste
- **Phase 3 — MIDI state alignment**: PPQ synced from loaded file; `_calculate_note_on_time` and save use correct `ticks_per_beat`; `save_pattern` preserves loaded file PPQ
- **Phase 4 — Save UX**: Save dialog pre-fills with loaded file path when loading from MidiFileEditor or Load; `_pattern_file_path` set from `midi_file.filename` when available
- **Tooltips on load**: Active notes show note names (e.g. C4, CLAP) in tooltips after MIDI file load
- **Drum name conversion**: `MidiNoteConverter.note_name_to_midi` handles drum names (CLAP, BD1, etc.) with JD-Xi fallback when `drum_options` empty
- **SequencerButton**: Fixed `note_duration`/`duration_ms` when `duration_ms` is None; added `duration_ms` property for pattern/manager compatibility

---

🎹 **SoundFonts & Pattern Editor Refinement Release**

This release introduces major improvements to the **SoundFont playback system**, continued development of the **Pattern Editor**, and extensive internal UI and codebase refinements.

## Added

### SoundFont Integration
- Added **SoundFont (.sf2 / .sf3) support**
- Ability to **load and browse SoundFont instruments**
- Use SoundFonts as a **virtual instrument backend**
- Enables MIDI playback and sequencing **without requiring a physical JD-Xi**
- Integration with **FluidSynth for audio playback**
- SoundFont preset list extraction and instrument selection

### Pattern Editor
- Expanded **Pattern Sequencer / Pattern Editor**
- **MIDI load/save**: Load from MidiFileEditor or file; edit steps; save back to same file with correct PPQ
- Improved step editing workflow and pattern playback timing
- **Part muting** for the four parts; **USB File Recording** widget
- Tooltips show note names (C4, CLAP, etc.) on loaded and edited steps
- Continued development of **grid-based sequencing tools**
- Foundations for future advanced sequencing features

### UI Enhancements
- Added **parameter plot widgets** for visual feedback
- Improved splash screen
- New instrument image handling for presets and parts
- Automatic instrument image loading
- Visual distinction between synth parts and drum kits

---

## Changed

### UI Improvements
- Improved spacing, margins, and layout consistency
- Updated section grouping and visual organization
- Switched application font to **Segoe UI**
- More consistent control panel styling

### Editor Components
- Refined slider and switch widget behavior
- Improvements to Program Editor sliders
- Improvements to Drum Editor layout and controls
- Updated UI margins and spacing across several windows

### MIDI Player
- Improved **MIDI channel detection**
- Automatic drum channel assignment to **Channel 10**
- Detection of:
  - bass instruments
  - guitars
  - keyboards
  - strings
- Automatic assignment to synth parts (channels 1–3)

---

## Refactored

### Core Architecture
Major internal refactoring was performed to improve maintainability.

- Expanded **ControlsRegistry** system for tracking UI controls
- Cleaner separation between:
  - UI layout
  - widget construction
  - MIDI / SysEx logic
- Adoption of **table-driven and data-model based patterns**
- Reduced duplication across synth editor components

### Codebase Improvements
- Improved handling of:
  - sliders
  - switches
  - parameter widgets
- Additional type hints and docstrings
- Continued restructuring of UI code in `picoui`
- Improved internal module organization

---

## Fixed

- Various UI inconsistencies across editor panels
- Improved preset loading reliability
- Reduced errors when switching programs rapidly
- Improved UI synchronization with JD-Xi state
- Fixes related to Program Editor slider behavior
- General stability improvements

---

# [0.9.5] — 2026-02
🎛️ **Editor and MIDI System Improvements**

## Added
- Improved **Arpeggiator SysEx synchronization**
- Effects editor enhancements
- Vocal effects editing improvements
- Improved patch loading and saving

## Supported Patch Formats
- `.jsz`
- `.msz`
- `.json`
- `.syx`

## Improvements
- MIDI debugging tools
- Parameter visualization
- Editor UI improvements

---

# [0.9.4] — 2026-02
🎹 **Major Code & UI Refinement Release**

## Major Code Improvements
- Substantial internal refactoring for improved maintainability and extensibility
- Cleaner separation between UI layout, widget construction, and MIDI logic
- Table-driven and data-model-based approaches adopted in several core areas
- Reduced duplication and more consistent editor patterns across synth sections

## UI & Layout Enhancements
- Improved spacing, alignment, and visual balance across the application
- Improved splash screen
- New Plot widgets for clearer visual feedback and parameter visualization
- More consistent use of reusable section and control widgets
- Overall UI feels more polished, legible, and "instrument-like"

## New Application Font
- Switched to **Segoe UI** for improved readability and a more modern, native look across platforms

## Instrument Images & Visual Identity
- Added instrument images for presets and parts
- Automatic image loading based on detected instrument type
- Graceful fallback when a specific image is unavailable
- Clear visual distinction between synth parts and drum kits

## Pattern Editor
- Improved workflow and usability
- Better visual structure and control grouping
- Continued groundwork for future sequencing enhancements

## MIDI File Player
- Drum detection and assignment to MIDI Channel 10
- Bass, Guitar/Keys & strings channel detection, assignment to Channels 1–3

## Preset & Program Handling
- Improved preset loading reliability
- More robust program loading and switching
- Fewer edge-case failures when changing parts or programs
- Better synchronization between UI state and JD-Xi internal state

## Fixed
- Numerous bug fixes across editors and supporting code
- Improved error handling and logging
- Reduced UI inconsistencies during rapid parameter changes

---

# [0.9.3] — 2026-01
🎹 **Major Code & UI Refinement Release**

## Major Code Improvements
- Substantial internal refactoring for improved maintainability and extensibility
- Cleaner separation between UI layout, widget construction, and MIDI logic
- Table-driven and data-model-based approaches adopted in several core areas
- Reduced duplication and more consistent editor patterns across synth sections

## UI & Layout Enhancements
- Improved spacing, alignment, and visual balance across the application
- Improved splash screen
- New Plot widgets for clearer visual feedback and parameter visualization
- More consistent use of reusable section and control widgets

## New Application Font
- Switched to **Segoe UI** for improved readability and a more modern, native look across platforms

## Instrument Images & Visual Identity
- Added instrument images for presets and parts
- Automatic image loading based on detected instrument type
- Graceful fallback when a specific image is unavailable
- Clear visual distinction between synth parts and drum kits

## Pattern Editor
- Improved workflow and usability
- Better visual structure and control grouping
- Continued groundwork for future sequencing enhancements

## MIDI File Player
- Drum detection and assignment to MIDI Channel 10
- Bass, Guitar/Keys & strings channel detection, assignment to Channels 1–3

## Preset & Program Handling
- Improved preset loading reliability
- More robust program loading and switching
- Fewer edge-case failures when changing parts or programs
- Better synchronization between UI state and JD-Xi internal state

## Fixed
- Numerous bug fixes across editors and supporting code
- Improved error handling and logging
- Reduced UI inconsistencies during rapid parameter changes

---

# [0.9.2] — 2026-01
🎹 **Major Feature Update + Expanded MIDI Support**

## New Builds
- macOS build available — packaged installer, no manual Python setup required
- Linux build available — .deb packaged installer and AppImage, built on Ubuntu 24.04
- Windows installer available (built via PyInstaller + Inno Setup)

## Better Playlist Editing
- Debugged the editing of existing Playlist Items
- Improved database backend code

## MIDI File Player Improvements
- Added "Detect Drum tracks" button to detect drums and save them as MIDI Channel 10
- Added "Classify Tracks" button to classify tracks as Bass, Piano/Guitars or Strings, and save as MIDI Channels 1, 2 or 3
- Drag and drop of MIDI tracks to sort and group tracks

## Improved Styling
- Icons for every tab
- Reusable widgets added for each page, giving a more harmonised appearance

## Improved Pattern Sequencer
- Can add bars and copy from previous bars
- More work planned for the sequencer

## MIDI File Support
- Load and play MIDI files directly in the editor
- Built-in Playlist Editor & Database
- Manage Playlists and Tracks per Playlist
- Select, play, and record tracks from the list
- Edit MIDI channel assignments
- Delete or reorder tracks
- Save modified MIDI files with automatic naming

## Digital Synth Editing
- Full editing support for all four digital parts, including partials

## Drum Editing — Vastly Improved
- Redesigned Drum Editor with clearer layout and control flow
- Improved parameter organization across drum partials
- More consistent mapping between kit parameters and MIDI behavior
- Better usability when editing multiple drum sounds

## Envelope Enhancements
- Added ADSR-style envelopes for Pitch, WMT, TVA, TVF
- Includes visual envelope displays for intuitive editing

## General Improvements
- New Splash screen
- User Programs Librarian & Database
- Select programs from a searchable list
- Integrated cheat-code workflow
- Enhanced playback slider and MIDI handling
- Cleaner, more reliable build system

---

# [0.9.1] — 2026-01
🎹 **Major Feature Update + Expanded MIDI Support**

## New Builds
- macOS build available — packaged installer, no manual Python setup required
- Linux build available — .deb packaged installer and AppImage, built on Ubuntu 24.04
- Windows installer available (built via PyInstaller + Inno Setup)

## MIDI File Support
- Load and play MIDI files directly in the editor
- Built-in Playlist Editor & Database
- Manage Playlists and Tracks per Playlist
- Select, play, and record tracks from the list
- Edit MIDI channel assignments
- Delete or reorder tracks
- Save modified MIDI files with automatic naming

## Digital Synth Editing
- Full editing support for all four digital parts, including partials

## Drum Editing — Vastly Improved
- Redesigned Drum Editor with clearer layout and control flow
- Improved parameter organization across drum partials
- More consistent mapping between kit parameters and MIDI behavior
- Better usability when editing multiple drum sounds

## Envelope Enhancements
- Added ADSR-style envelopes for Pitch, WMT, TVA, TVF
- Includes visual envelope displays for intuitive editing

## General Improvements
- New Splash screen
- User Programs Librarian & Database
- Select programs from a searchable list
- Integrated cheat-code workflow
- Enhanced playback slider and MIDI handling
- Cleaner, more reliable build system

---

# [0.9] — 2025-12
🎹 **Major Feature Update + Expanded MIDI Support**

## New Builds
- macOS build available — packaged installer, no manual Python setup required
- Linux build available — .deb packaged installer and AppImage, built on Ubuntu 24.04
- Windows installer available (built via PyInstaller + Inno Setup)

## MIDI File Support
- Load and play MIDI files directly in the editor
- Built-in Playlist Editor & Database
- Manage Playlists and Tracks per Playlist
- Select, play, and record tracks from the list
- Edit MIDI channel assignments
- Delete or reorder tracks
- Save modified MIDI files with automatic naming

## Digital Synth Editing
- Full editing support for all four digital parts, including partials

## Drum Editing — Vastly Improved
- Redesigned Drum Editor with clearer layout and control flow
- Improved parameter organization across drum partials
- More consistent mapping between kit parameters and MIDI behavior
- Better usability when editing multiple drum sounds

## Envelope Enhancements
- Added ADSR-style envelopes for Pitch, WMT, TVA, TVF
- Includes visual envelope displays for intuitive editing

## General Improvements
- User Programs Librarian & Database
- Select programs from a searchable list
- Integrated cheat-code workflow
- Enhanced playback slider and MIDI handling
- Cleaner, more reliable build system

---

# [0.8] — 2025-09
🎹 **New Windows Build + Major Feature Updates**

## New Builds
- **Windows build available** — packaged installer, no need to set up Python manually
- macOS and Linux builds also available

## MIDI File Support
- Load and play MIDI files directly in the editor
- Edit channel numbers
- Save modified MIDI files for playback

## Digital Synth Editing
- All 4 digital parts now fully editable, including partials

## General Improvements
- More stable UI across platforms
- Improved playback slider and MIDI handling
- Cleaner build system with PyInstaller + Inno Setup for Windows

## Notes
- Some features like the full Pattern Sequencer and PW display were still in progress

---

# [0.6.0] — 2025-05 (Beta)
🎹 **First Public Beta for macOS Sequoia**

## What's New
- Universal binary for macOS Sequoia (Intel & M1/M2/M3)
- Fully redesigned editor UI with improved layout
- Real-time MIDI feedback and enhanced control mapping
- Modular synth editors for Digital, Analog, and Drum sections

## Known Limitation
- Patch saving not yet implemented for drums

---

# [0.4.0] — 2025-05 (Beta)
🎹 **First Public Beta for macOS Sequoia**

## What's New
- Universal binary for macOS Sequoia (Intel & M1/M2/M3)
- Fully redesigned editor UI with improved layout
- Real-time MIDI feedback and enhanced control mapping
- Modular synth editors for Digital, Analog, and Drum sections

## Known Limitation
- Patch saving not yet implemented

---

# Core Features

JDXI-Editor provides a software editing environment for the **Roland JD-Xi synthesizer**, allowing deeper control than the hardware interface alone.

### Synth Editing
- Digital Synth Parts 1 & 2
- Three partials per digital synth
- Analog Synth Editor
- Drum Part Editor

### Effects
- Reverb
- Delay
- Vocoder
- Arpeggiator

### MIDI Tools
- MIDI debugger
- MIDI file player
- MIDI playlist support
- Pattern sequencing tools

### Interface
- JD-Xi style LCD display
- On-screen keyboard
- Preset browser with search
- Envelope visualizations (ADSR, pitch)

---

# Changelog

All notable changes to **JDXI-Editor** will be documented in this file.

The format loosely follows **Keep a Changelog**, and the project adheres to **semantic-ish versioning** while still in the 0.x development phase.

---

# Project

**JDXI-Editor** is a cross-platform MIDI editor built using:

- **Python**
- **Qt / PySide**
- **RtMidi**
- **Mido**

It aims to implement as much of the **Roland JD-Xi MIDI implementation** as possible, providing a modern graphical interface for sound editing, sequencing, and MIDI experimentation.

---

# Links

Repository  
https://github.com/markxbrooks/JDXI-Editor

Documentation  
https://markxbrooks.github.io/JDXI-Editor/
