# JDXI-Editor: Project Critique and Rewrite Recommendation

*November 2026, version 0.9.7 (`main` @ df800a1a)*

This document has two parts:

1. A critique of the project as it is: architecture, MIDI correctness, code health, tests and packaging, with a prioritised list of fixes.
2. What I would choose to write a suite from scratch: a desktop app, a mobile app (iOS and Android) and a plugin (VST3 and others), for professionalism and performance.

Part 1 draws on repository measurements and on bugs found and fixed in recent sessions (SysEx requests, patch save/load, the MIDI player).

---

## Part 1: The project today

### At a glance

| | |
|---|---|
| Application code | 722 Python files, ~105,000 lines (`ui/` 70.6k, `midi/` 28.6k, `devel/` 4.2k) |
| Own libraries | `picomidi` (MIDI and playback), `decologr` (logging), `picoui` (widgets, kept in this repo) |
| GUI / MIDI | PySide6 (Qt 6), python-rtmidi, mido, FluidSynth |
| Tests | 433 test functions in 60 files; 13 fail in a default run; no CI job runs them |
| History | 2,053 commits since January 2025 |

### What is good

- **Breadth.** It covers the Digital, Analog, Drum, Effects, Vocal FX, Program and Arpeggio editors, plus a pattern sequencer, a MIDI file player with track tools, a playlist, SoundFont playback and a MIDI monitor. Few hardware editors cover this much of a synth's MIDI implementation.
- **Domain depth.** Roland address arithmetic, nibbled parameters, the RQ1/DT1 request cycle and the `.msz` bundle format are all modelled. The newer modules carry docstrings with examples. These include the request queue, synth memory, echo guard, patch bundle and playback engine.
- **Tests exist and are fast.** Most tests run headless (`QT_QPA_PLATFORM=offscreen`) without hardware. They found real regressions during the recent work.
- **The playback engine is well designed.** It is a pure, Qt-free `PlaybackEngine` with absolute-tick scheduling, controller chase and held-note tracking. A thin Qt transport drives it from its own thread. The rest of the code should follow this pattern.
- **Release tooling exists.** There are PyInstaller and Nuitka builds, macOS signing and notarisation, an Inno Setup installer for Windows, and Sphinx docs published to Pages.

### 1. Architecture

**1.1 The MIDI layer depends on the UI layer.** 15 modules under `midi/` import from `jdxi_editor.ui`, and 12 import PySide6. The I/O helper, input handler and controller are among them. As a result:
- the MIDI and SysEx code can't be reused without Qt, which rules it out for a plugin or mobile app;
- tests of the MIDI logic must start a `QApplication`;
- a recent fix (`patch_values.py` importing `ui.widgets.envelope.parameter`) had to add another such import, because the units a parameter is shown in live in the UI layer.

*Fix:* move parameter metadata (ranges, units, display conversion) into `midi/data`. The rule is that the UI may import the MIDI layer, never the other way round. An import-linter contract in CI can enforce it.

**1.2 One parameter, several units.** One parameter value can be in any of four units, depending on where it is read:

| Read from | Unit |
|---|---|
| Wire and file | raw MIDI |
| Slider | display value (signed for bipolar parameters) |
| ADSR / pitch envelope | ms (different ranges) or a sustain fraction |
| Combo box | its index |

Each widget converts in its own way, and the parameter tables have errors: Digital `OSC_PITCH_COARSE`/`FINE` and `AMP_VELOCITY` are given in display units with no offset, and `AMP_LEVEL_KEYFOLLOW` and `LFO_SHAPE` share an offset. This one design flaw caused most of the save/load bugs:
- values drifted on every save and load;
- the pitch envelope was written as 127;
- controls didn't update from the synth.

*Fix:* every parameter is held as **raw MIDI in one model**. Conversion happens in exactly two functions per parameter: raw → display, and display → raw. Both are generated from one table (see 1.4). Widgets bind to the model, never to SysEx.

**1.3 God classes.**

| File | Lines |
|---|---|
| `ui/windows/jdxi/instrument.py` | 2,416 |
| `ui/editors/midi_player/editor.py` | 2,013 |
| `ui/editors/pattern/pattern.py` | 1,919 |
| `ui/editors/digital/editor.py` | 1,437 |

The MIDI player editor alone handles:
- file I/O;
- program-change marker editing;
- loop points and transport sync;
- WAV export;
- track classification;
- channel mutes.

The track viewer both builds widgets and edits the MIDI file. *Fix:* separate models and services from widgets, starting with the player (a `MidiDocument` model with undo/redo) and the main window.

**1.4 Data written as code.** `ui/programs/programs.py` (3,861 lines) and `ui/preset/tone/digital/list.py` (3,648 lines) are data. The parameter tables are hand-written Python enums with offsets, ranges and display ranges. *Fix:* keep one machine-readable spec of the JD-Xi MIDI implementation (YAML or JSON), and generate the parameter classes and the presets from it. A spec can be checked automatically, for example for overlapping offsets, sections overrunning their size, or display ranges that don't match the raw range. That would have caught the Digital table bugs.

**1.5 Global state and side channels.** The MIDI helper is effectively a singleton, and state is attached to it ad hoc, for example `request_queue_for(helper)` and `synth_memory_for(helper)`. That is pragmatic, but tests interfere with each other through it. The code checks objects with `hasattr` 425 times rather than relying on declared interfaces. *Fix:* build a `Device` object holding the port, queue, memory and echo guard once, and pass it to the editors that need it.

### 2. MIDI correctness and timing

Most of these were found in recent sessions, and the specific bugs are fixed. The weaknesses that allowed them remain:

- **Requests weren't checked against the spec.** Malformed RQ1s (wrong address width) made Arpeggio and Effects reads time out. *Lesson:* round-trip tests (encode → bytes → decode) for every request the editor sends, and golden fixtures recorded from a real JD-Xi.
- **Feedback loops.** Values received from the synth used to be echoed back as writes. A thread-local echo guard now blocks this. The cleaner design is a model that tracks where each change came from (device or user) and only forwards user changes.
- **Request traffic.** A program change used to send duplicate, unpaced RQ1 bursts. The new `SysExRequestQueue` serialises them and waits for each reply. It should be the only path to the device.
- **Timing in Python.** Playback runs a high-resolution timer in a `QThread`. That is adequate for a hardware synth, but the GIL means GC pauses and UI work can add jitter. Python can't host audio-thread work, which rules out sample-accurate output and plugins (see Part 2). There are also 13 `time.sleep` calls outside `devel/`, which are blocking waits.
- **Mute and velocity logic was only tested at the engine level.** The UI wiring was wrong: each track's mute button toggled twice per click. Tests that click real widgets (now added) are worth having for every editor.

### 3. Code health

| Signal | Count | Comment |
|---|---|---|
| `print(...)` | 610 | Use `decologr`/`logging` at debug level. The prints flood stdout during tests. |
| `except:` / `except Exception:` | 365 | Many hide real errors, e.g. a bad parameter becomes a silent no-op. Catch narrowly; log and re-raise at boundaries. |
| `hasattr(...)` | 425 | Duck typing as a substitute for interfaces (see 1.5). |
| `mypy` | `strict = True` in `mypy.ini` | Not run in CI. Either enforce it on `midi/` first or remove it. |

Other issues:
- Docstrings often contradict the code. For example, "`track: int MIDI channel (1-16)`" was written for a track index. Docstrings that only repeat the method name ("`get_muted_tracks` … `:return: None`") add noise.
- Dead code is still present: `midi/utils/play_buffered.py` (unused, and its track numbers start at 1), `paintEventOld`, the track viewer's hidden channel-mute row, and the `clear_old` methods.
- `jdxi_editor/devel/` holds 27 one-off scripts (monitors, probes, `sheep.py`) inside the shipped package.

### 4. Tests

- **No CI job runs the tests.** The two workflows publish to PyPI and build docs. A green `main` currently means nothing.
- 13 tests fail in a default run and are effectively ignored:
  - `test_sheep_simple` ×4, `test_long_playback`, `test_realtime_playback`, `test_segment_statistics`, `test_buffer_tempo_fix` and `test_track_duration` depend on local MIDI files, real-time waits or the old buffered player;
  - `test_sysex_parser_ir` ×4 are genuine failures.
- Hardware, timing and data-file tests sit alongside unit tests. *Fix:* use markers (`@pytest.mark.hardware`, `slow`, `needs_file`), keep the default run green and require it in CI on macOS, Windows and Linux.
- The newest tests (raw-value bundles, request queue, mutes) show the pattern to follow: no hardware, real byte fixtures, real widgets.

### 5. Packaging and repository

These are real defects: a `pip install` of this project would not work as published.

- **The entry point doesn't exist.** `[project.scripts] jdxi_manager = "jdxi_manager.main:main"`, but the package is `jdxi_editor`.
- **The wheel would be empty.** `[tool.hatch.build.targets.wheel] packages = ["jdxi-editor"]` names a directory that doesn't exist (hyphen, not underscore).
- **The metadata disagrees with itself.**
  - The distribution is called `jdxi_manager` and the repository URL points to `JDXI-Manager`, while the homepage is `JDXI-Editor`.
  - `README.md` and `README.rst` both exist.
  - black targets `py38` while the project requires Python 3.10 or later.
- **Two build configurations.** `setup.py` is the py2app configuration for the macOS app (used by `building/apple/build_macos.py`), not a duplicate package definition. It should say so, or be renamed, so it isn't mistaken for one.
- **Undeclared dependencies.**
  - `picoui` is imported but isn't a declared dependency. It works only because a copy sits at the repository root.
  - `picomidi` is missing from `requirements.txt`.
- **`requirements.txt` is a frozen developer environment, not the app's dependencies.** It includes `biotraj`, `mmtf-python`, `SQLAlchemy`, `pandas`, `scipy`, `scikit-image`, `music21`, `pyo` and `pyglm`, plus `style==1.1.0` and `update==0.0.1`. Those last two are trivial placeholder packages that should not be installed by anyone. Use `pyproject.toml` with `uv.lock` (already present) as the single source.
- **Things in git that shouldn't be:**
  - `JD-Xi Editor.app/` (a built binary);
  - Roland's manuals (`JD-Xi_ParameterGuide_e01_W.pdf`, `JD-Xi_MIDI_Imple_e01_W.rtf` and `.html`). Redistributing these may conflict with Roland's copyright, so link to Roland's site instead.
  - (`build/`, `dist/`, `venv/` and egg-info sit in the working tree but are already ignored.)
- There are three build systems: `main.spec` / `JD-Xi-Editor.spec` (PyInstaller), Nuitka scripts and `building/buildsys`. Keep one.

### 6. Prioritised fixes (if you continue in Python)

| # | Fix | Effort | Value | Status |
|---|---|---|---|---|
| 1 | CI that runs the tests on 3 OSes; mark or fix the 13 failures | S | Very high | **Done.** `.github/workflows/tests.yml`; the parser bugs and missing imports are fixed; the real-time `sheep.mid` tests are marked `slow`. |
| 2 | Fix `pyproject.toml` (entry point, wheel packages, name, dependencies); replace the frozen `requirements.txt` | S | High | **Done**, except the wheel is 105 MB (images about 3.5 MB each), just over PyPI's default 100 MB limit. |
| 3 | Remove binaries and Roland PDFs from git; complete `.gitignore` | S | High (legal and size) | **Done** (untracked; still in history). |
| 4 | Machine-readable JD-Xi spec + generated parameter tables + spec checks | M | Very high: removes a whole class of bugs | **Checks done** (`tests/test_parameter_tables.py`; 21 table errors fixed). Spec and generator not started. |
| 5 | One raw-MIDI parameter model; widgets bind to it; remove per-widget units | L | Very high | |
| 6 | Cut the `midi/` → `ui/` dependency; enforce it in CI | M | High: enables reuse | **Started:** 15 → 11 modules; `tests/test_layering.py` stops new ones. |
| 7 | `Device` object (port, request queue, memory, echo guard) in place of the singleton plus attributes | M | Medium | **Done:** `JDXiDevice` (`helper.device`) owns the queue, memory and echo guard. The helper is still a singleton, because editors built without a helper rely on it. |
| 8 | Split the main window and the MIDI player; `MidiDocument` with undo | L | Medium | |
| 9 | Replace `print` with logging; narrow `except`s; delete dead code and `devel/` | M | Medium | `play_buffered.py` removed. |

---

## Part 2: Starting again — desktop, mobile and plugin

### The deciding constraint: the plugin

Desktop and mobile can be built with many stacks. A plugin (VST3, AU, CLAP, AUv3 on iOS) can't:

- it runs inside someone else's process and event loop;
- several copies can be loaded at once;
- its audio and MIDI callbacks must be real-time safe (no allocation, locks or GC on the audio thread).

That rules out Python, and it rules out Qt in practice. Qt expects to own the application's event loop (`QApplication`), which conflicts with the host and with other plugins using Qt. Its LGPL terms are also awkward for the static linking iOS requires. Whatever the plugin uses should also run the other two targets, so that one codebase covers all three.

### Recommendation: C++20 + JUCE, with a separate core library

| Layer | Choice | Why |
|---|---|---|
| Language | **C++20** | The language of the audio-plugin ecosystem. Deterministic memory and timing, and no GC on the audio thread. |
| Framework | **JUCE 8** | One codebase builds standalone desktop apps (macOS, Windows, Linux), iOS and Android apps, and plugins (VST3, AU, AUv3, standalone; CLAP via the `clap-juce-extensions` wrapper). It includes MIDI I/O, MIDI files, timers, audio, the GUI, preset state and an OpenGL / Metal / Direct2D renderer. |
| MIDI I/O | **JUCE `MidiInput`/`MidiOutput`**, not RtMidi | RtMidi is fine on desktop but doesn't serve iOS and Android well. JUCE wraps CoreMIDI (macOS and iOS), WinMM / Windows MIDI Services, ALSA and Android's `android.media.midi` behind one API. For C++ outside JUCE, **libremidi** is the modern successor to RtMidi. |
| GUI | **JUCE components** for knobs, envelopes and keyboards; optionally the **JUCE 8 WebView UI** for browser and librarian screens | JUCE's vector components are standard in commercial plugins and render the same in all three targets. A WebView suits list-heavy screens (patch library, playlist) and is used by many current plugins. Keep real-time widgets (meters, envelope drag) native. |
| Core | **A plain C++ library (`jdxi-core`) with no JUCE dependency**, generated from the JD-Xi spec | Parameter model (raw MIDI plus display conversion), SysEx encode/decode, Roland address arithmetic, request scheduler, device memory mirror, `.msz` reader/writer. Pure and unit-testable, so the apps stay thin. |
| Build | **CMake + CPM or vcpkg**, GitHub Actions matrix, **pluginval** in CI | pluginval is the standard tool for checking a plugin's behaviour in a host. |
| Tests | **Catch2** or GoogleTest; golden SysEx fixtures recorded from the hardware | The same fixtures run on every platform. |

#### What each target looks like

- **Desktop:** a JUCE standalone app with the full editor, librarian, MIDI file player (JUCE `MidiFile` plus a high-priority timer thread; the current `PlaybackEngine` design carries over directly) and pattern sequencer. It can be signed and notarised for macOS, packaged as MSIX or with Inno Setup for Windows, and as AppImage or Flatpak for Linux.
- **Mobile (iOS and Android):** the same core and largely the same components, with layouts for touch and small screens.
  - On iOS, ship both a standalone app and an **AUv3**, so it runs inside AUM, Cubasis or Logic for iPad.
  - On Android, JUCE uses the platform MIDI API, and the JD-Xi connects over USB OTG.
  - Check two things on real devices early: the JD-Xi's class-compliant USB-MIDI behaviour, and SysEx throughput.
- **Plugin (VST3, AU, CLAP):** the JD-Xi editor inside a DAW, giving parameter automation and total recall. The patch is saved in the DAW project and sent to the synth when the project loads. Two traps to design for from the start:
  1. **SysEx through the host is unreliable.** Hosts and the VST3 format pass SysEx out of a plugin poorly. AU and CLAP do better. The robust approach is for the plugin to open the JD-Xi's MIDI port itself, which JUCE allows on desktop, and to use host MIDI output only for notes and CCs.
  2. **Exclusive ports.** On Windows with the WinMM driver, only one process can open a MIDI port at a time, so the DAW and the plugin can fight over the JD-Xi. Windows MIDI Services (multi-client) removes this. Detect the conflict and tell the user.

#### Licensing

JUCE is dual-licensed: AGPLv3, or a commercial licence that includes a free tier below a revenue threshold. Check the current terms before choosing.

AGPLv3 matches an open-source editor. A closed-source or paid app needs a commercial licence. Plugins must also meet Steinberg's VST3 licence terms (now MIT-licensed for the SDK, but check the trademark guidelines). CLAP is MIT.

### Alternatives considered

| Stack | Desktop | Mobile | Plugin | Verdict |
|---|---|---|---|---|
| **C++ / JUCE** | ✅ | ✅ (iOS and Android, AUv3) | ✅ VST3, AU, AUv3, CLAP | **Recommended.** One codebase, industry standard, proven in commercial products. |
| C++ / Qt (QML) | ✅ excellent | ⚠️ works, less native; LGPL difficult on iOS | ❌ in practice | The best path if you never ship a plugin. |
| Rust: `nih-plug` + `midir` + egui / iced / vizia / Slint | ✅ | ⚠️ immature for mobile audio and MIDI | ✅ VST3 and CLAP (no AU or AUv3 in nih-plug) | Strong for safety, but GUI and mobile are behind JUCE. Worth revisiting in 2–3 years. |
| Native shells (SwiftUI / Jetpack Compose) + a shared C++ or Rust core | Swift on macOS only | ✅ best mobile UX | Via the C++ core | The best mobile result, but three or four UIs to maintain. Only worth it with a team. |
| Python / PySide6 (today) | ✅ fast to develop | ❌ | ❌ | Fine for a desktop-only editor, a dead end for the other two targets. |
| Flutter / .NET MAUI / Avalonia | ✅ | ✅ | ❌ | MIDI support relies on community packages, and none can produce a plugin. |

### Shipping all three in stages

1. **Write the JD-Xi spec first** (YAML), with checks, as the source of truth. It is useful in both Python and C++.
2. **Build `jdxi-core` in C++** from the spec. Expose it to Python through **nanobind** or pybind11, so the current PySide6 app adopts it piece by piece: the SysEx codec, then the parameter model, then the request queue. The desktop app keeps shipping while the core is replaced underneath it, and any behaviour difference shows up in the existing tests.
3. **Ship the JUCE plugin and the iOS AUv3** on the same core. These are the targets Python can't reach, and they add the most value.
4. **Rebuild the desktop app in JUCE** last, once the core and its components are proven, and retire the Python app when it reaches feature parity.

This keeps the domain knowledge built up over 2,000 commits. That knowledge is now the project's main asset, and it becomes something every target can use.
