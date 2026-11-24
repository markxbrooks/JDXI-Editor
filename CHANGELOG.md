# Changelog

All notable changes to JDXI-Editor are documented in this file.

# [Unreleased]

### Fixed

- **SoundFont playback survives a change of audio output.** PortAudio reads
  the audio hardware once, when it starts, and never looks again, so a
  session that outlives a change to it -- AirPods connecting, headphones
  unplugged -- asked for devices by positions that had moved or gone and got
  `paInternalError` (-9986), the default output included. Playback stopped
  following the route, and every later attempt to start the SoundFont failed
  until the application was restarted. The output now rereads the devices
  once and retries. Because that closes every stream in the process, the
  Audio Monitor and the USB recorder register theirs, and a reread is
  refused while either is listening.
- **Recording refuses a device with no inputs.** Choosing an output left
  `WavRecordingThread` opening it anyway, which on some platforms writes a
  file of zeroes. It now names the device and says there is nothing to
  record.

# [1.0.1] — 2026-11-23

A packaging release: 1.0.0 with the two fixes below. No new features, and no
change to the application's own code. The app stays **Beta**; what is known
to be wrong with it is collected in [doc/known-issues.md](doc/known-issues.md).

### Fixed

- **The Audio Monitor hears the input in the packaged Mac app.** macOS does
  not refuse an app that opens an audio input without declaring why it wants
  one: it hands it silence. PortAudio opened the stream, the monitor said
  "Listening", and no samples ever arrived. Running from a checkout was
  unaffected, because there the permission belongs to the terminal. Both
  Info.plists now carry `NSMicrophoneUsageDescription`.
- **The Linux package asks for the libraries it needs.** The `.deb` declared
  no dependencies at all. The PyInstaller bundle carries Python, Qt and
  PortAudio, but not the system libraries those load at runtime: without
  `libasound2` the bundled PortAudio cannot load, so `import sounddevice`
  fails and the Audio Monitor reports that sounddevice is not installed;
  without the Qt libraries the application does not start. The renamed
  64-bit `time_t` packages are given as alternatives, so the package stays
  installable on Debian 12 and 13 alike.

# [1.0.0] — 2026-11-22

The first stable release. 1.0.0rc2 with the fix below, and no new features.
The app stays **Beta**: what is known to be wrong with it is collected in
[doc/known-issues.md](doc/known-issues.md).

### Fixed

- **The right-hand rack ear is painted again.** The strip along the bottom of
  the instrument keeps room at each end for the cheeks a rack skin paints
  there, and lays the wheels and the keys out between them. The keys were
  sized to the window's full width instead, so the strip's contents asked for
  more room than the strip could be given: Qt handed it its minimum anyway,
  the surplus hung over the right edge of the window, and the cheek at that
  end was painted where nothing showed it. The left one starts at the window's
  edge whatever happens, so the pair went lopsided rather than missing. Only
  skins whose cheeks are wider than the 28 px of slack in the instrument's
  design width were affected: JD-Xi Rackmount, Juno-106, Mini Moog, MS-20,
  ARP 2600, Brushed Metal (70s) and Ivory & Walnut.

# [1.0.0rc2] — 2026-11-19

The same caveats are collected in [doc/known-issues.md](doc/known-issues.md).

Replaces 1.0.0rc1, which never reached PyPI: its tag predated the fix below,
and the release checks failed. No new features.

`python -m pytest -m hardware` has since passed on a connected JD-Xi:
identity, temporary program, digital, analog, drum, effect, and arpeggio
reads, one restored temporary digital byte, a one-bar playback, and a
recording capture. The same result is in
[doc/known-issues.md](doc/known-issues.md). The app stays **Beta**.

### Changed

- **USB recording uses sounddevice.** PyAudio is no longer a dependency.
  sounddevice's wheels include PortAudio, so an Apple Silicon `pip install`
  does not compile PyAudio.
- **SoundFont output on macOS follows the headphone jack.** The built-in
  output opens as the system default, so CoreAudio uses the jack when
  headphones are plugged in. A separate device (AirPods, USB, a multi-output
  device) stays on the index that was selected. Plugging or unplugging the
  jack while playback is following the system route reopens the stream.

### Fixed

- **The editor starts without a MIDI backend.** python-rtmidi raises when it
  cannot reach the platform's MIDI service (on Linux, whenever `/dev/snd/seq`
  is absent: containers, minimal installs, CI runners). The editor now treats
  that as "no ports" and opens, instead of exiting with a traceback from
  `_rtmidi`.

### Tests

- `librosa` is declared in the `dev` extra: the refine, audio-evidence,
  arpeggio and likelihood tests import it and failed without it.
- The tests that read the local `tests/sheep.mid` are marked `slow` and skip
  when it is absent, as the other sheep tests already did.
- The pattern loop test allows a CI runner's scheduling jitter on each beat
  (+-0.1 s) while still failing a dropped or doubled beat, and holds the
  median gap to the tempo.

# [1.0.0rc1] — 2026-11-19

The first candidate for 1.0. Everything a user can see is listed under 0.9.9
below; this tag adds no features. It exists so installation and JD-Xi hardware
can be exercised before 1.0. On the machine this tag was cut from, the MIDI
inputs were empty, so identity, a program read and write, digital, analog,
drums, effects, a pattern, and playback to a JD-Xi had not been run. That
pass is recorded under 1.0.0rc2. The app stays **Beta**.

### Fixed

- **picomidi**: Required `>=0.3.0`. The MIDI player's transport imports
  `picomidi.playback.scheduler` and calls the engine's per-track volume,
  transpose, and channel map, none of which exist in picomidi 0.2.0. The floor
  said `>=0.2.0`, so a fresh install resolved to 0.2.0 and the **main window
  did not import at all**. Only the released 0.9.9 was unaffected.
- **Update check**: A pre-release is now ordered before its own release, so
  `1.0.0rc1 < 1.0.0rc2 < 1.0.0`. The version was read as numbers only, which
  made 1.0.0rc1 and 1.0.0 indistinguishable: a candidate's testers would never
  have been offered the finished build.
- **Windows installer**: Stamped with the project's version. `jdxi_editor.iss`
  carried a hard-coded `0.9.6`, so every installer since has been mislabelled.
- **Documentation**: The Sphinx build reads the version from
  `jdxi_editor/project.py`. It claimed `1.0.0` while the app was on 0.9.9.
- **Offscreen startup**: The MIDI configuration dialog is skipped when there
  is no display. `__init__` opens it whenever a JD-Xi was not auto-connected,
  and `exec()` had nobody to answer it, so the test suite and
  `scripts/check_installed.py` hung instead of finishing.

### Known issues

- **The `.deb` version** is `1.0.0rc1`, which dpkg orders *after* `1.0.0`, so
  `apt` will not upgrade a candidate to the finished release. Reinstall rather
  than upgrade.

# [0.9.9] — 2026-11

The notes below are everything a user can see since 0.9.8. This build stays **Beta**. 1.0.0rc1 and 1.0.0rc2 now exist. The hardware pass they were cut to allow has been run: `python -m pytest -m hardware` passed on a connected JD-Xi, and the result is under 1.0.0rc2 and in [doc/known-issues.md](doc/known-issues.md).

### Rack skins

- **JDXiSkin menu**: The window wears a rack skin. Built-ins include Glossy Black, JD-Xi Red, JD-Xi White, JD-Xi Rack, TR-808, TB-303, TR-909, TR-1000, Jupiter-8, Juno-106, Mini Moog, MC-101, MS-20, SH-101 (grey, red, blue), ARP 2600, Brushed Metal, and Ivory Walnut.
- **User skins**: A TOML file in `~/.jdxi_editor/skins/` appears in the same menu. `doc/skins/tr1000_user.toml` is an example. The Skin Editor starts a file from any built-in skin. A skin can ask the Audio Monitor for bar meters, needles, or a vintage VU, and can draw MIDI lanes as punched cards.

### Audio

- **Audio Monitor**: Oscilloscope, stereo bar meters, and a spectrum, from an **input** device. It does not hear SoundFont playback. Needles are drawn only when the active skin asks for them.
- **SoundFont output**: FluidSynth renders samples and sounddevice plays them. MIDI Configuration has an **Audio output** menu. "(Default)" is the system output (the speakers, when those are the Mac's default). Changing the menu while FluidSynth is running reopens that device, and the status names the output PortAudio opened. A short note from `TimGM6mb.sf2` opened the system default (`Mark's AirPods #5`, index 1), `MacBook Pro Speakers` (index 4), and `Multi-Output Device` (index 9). No USB interface was connected. The monitor's input path was left alone.

### Playback, playlists, and install

- **Playlists**: Add, remove, and reorder files, with artwork and playback progress.
- **MIDI tools**: Phrase finding, track classification, trimming, and remap, beside the existing player.
- **Update check**: Once a day, against GitHub Releases, for a build that matches this install.
- **PySide6**: Required `>=6.8.1.1,<6.10`. 6.12 crashes the main window when a queued slot receives outgoing MIDI. 6.10 and 6.11 are untested.
- **picomidi**: Required `>=0.3.0`. The MIDI player's transport uses `picomidi.playback.scheduler` and the engine's per-track volume, transpose, and channel map, none of which are in picomidi 0.2.0; against 0.2.0 the main window does not import at all.
- **Frozen builds**: FluidSynth, sounddevice (and its PortAudio binaries), and music21's LilyPond support are declared for PyInstaller and py2app. SoundFont playback needs a FluidSynth install. PortAudio comes with sounddevice.

# [0.9.8] — 2026-11

### Refreshed UI (UI_CRITIQUE)

- **AppEditorStyle**: Shared restrained editor chrome (grey idle borders, soft sliders; accent only for focus/active) used app-wide via `Theme.apply_editor_style`
- **MidiPlayerStyle / PatternEditorStyle**: Subclass the shared chrome; muted timeline colours, two-line track headers, bar/beat ruler
- **Identity tokens**: Metallic red `#A71920`, illuminated accent `#E04435`, LCD orange `#FF6A00` in `AppEditorStyle` and `JDXiUIStyle`
- **Signature LCD**: `DigitalDisplay` / `DigitalTitle` JD-Xi-style panel; optional `BANK msb/lsb · PC n` line wired from tone selection
- **Tabs**: Underline selection (metallic red / Analog cyan) instead of full red box borders; main editor and section `TAB_TITLE` aligned
- **Preset workspace**: Top-aligned Digital/Analog/Drum preset + instrument image row; frameless instrument overview (no heavy inset card)
- **Selection / MIDI wire**: Slim `MidiWireInfo` (channel, bank, program); `MidiSelectionInfoBar` syncs LCD detail on preset change
- **Drum partial SysEx**: Pass `address` + `send_midi_parameter` into Pitch Env, Partial, Output, TVF, and TVA sections (fixes failed sends such as `PITCH_ENV_TIME_4_VELOCITY_SENS`); harden QWidget parent address lookup

# [0.9.7] — 2026-06

Interim release between Effects/Vocal/Pattern work (0.9.6) and the UI refresh (0.9.8).

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
