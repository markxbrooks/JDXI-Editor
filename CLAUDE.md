# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this is

JDXi-Editor is a PySide6 desktop editor and MIDI manager for the **Roland JD-Xi** synthesizer. It edits the Digital 1/2, Analog, Drum, Effects, Vocal FX and Arpeggio parameters over SysEx, and adds a pattern sequencer, a MIDI file player with track classification, FluidSynth SoundFont playback, an audio monitor, playlists, and rack skins. It is published on PyPI as `JDXI-Editor`; the console scripts are `jdxi-editor` / `jdxi_manager` → `jdxi_editor.main:main`.

- Version: `__version__` in [jdxi_editor/project.py](jdxi_editor/project.py). Hatch reads it from there; it is the only place to bump.
- Python 3.10 to 3.12. **PySide6 is pinned `<6.10`** because 6.12 segfaults when the main window opens. See the comment in [pyproject.toml](pyproject.toml).
- Status and caveats are in [doc/known-issues.md](doc/known-issues.md) and [CHANGELOG.md](CHANGELOG.md).

## Commands

```bash
pip install -e ".[dev]"            # dev extra: pytest, mypy, black, isort, flake8, soundfile, librosa
python run_editor.py               # run from a checkout (or: jdxi-editor)

python -m pytest                   # default: skips tests marked slow and hardware
python -m pytest tests/test_jdxi_sysex.py::test_name   # one test
python -m pytest -m slow           # needs local files (e.g. tests/sheep.mid, not in git) / real time
python -m pytest -m hardware       # needs a connected JD-Xi (tests/test_jdxi_hardware.py)

black . && isort .                 # line length 88, isort profile "black"
python -m build                    # sdist + wheel (hatch_build.py scales images in resources/)
python -m building.buildsys        # desktop packages; --dmg / --app / --pkg on macOS. See doc/building.md
```

- Tests build real Qt widgets. Headless runs need `QT_QPA_PLATFORM=offscreen` (CI sets it). On PowerShell: `$env:QT_QPA_PLATFORM='offscreen'; python -m pytest`.
- [tests/conftest.py](tests/conftest.py) clears `JDXI_EDITOR_MIDI_CONTROLLERS` so tests use the built-in controller maps, not `~/.jdxi_editor/midi_controllers.json`.
- CI ([.github/workflows/tests.yml](.github/workflows/tests.yml)) runs on Linux/macOS/Windows with 3.11, plus 3.10 and 3.12 on Linux. It also builds the wheel, installs it into a clean venv, and runs [scripts/check_installed.py](scripts/check_installed.py). On Linux, `MidiIOHelper` needs `/dev/snd/seq`.
- `mypy.ini` sets `strict = True`, but the codebase is not strict-clean. Don't treat mypy output as a gate.

## Repository layout

| Path | Purpose |
|---|---|
| `jdxi_editor/` | The application package |
| `picoui/` | Shared Qt UI helpers, **vendored into the wheel**. PyPI's picoui lacks modules the editor imports, so edit the repo copy |
| `decologr/` | Local copy of the logging library (`from decologr import Decologr as log`). It is also a PyPI dependency |
| `picomidi` | **External** PyPI dependency (`>=0.3.0`): MIDI constants, `AddressParameter`, the playback engine and scheduler. `picomidi.local.bak/` is an untracked local backup and is not used |
| `tests/` | pytest suite (~120 files), with fixtures, `.msz`/JSON/MIDI samples |
| `scripts/` | Stand-alone analysis tools (MIDI part classification, similarity, SysEx parsing, screenshots) |
| `building/` | Platform build system (`python -m building.buildsys`), PyInstaller/py2app specs, Windows scripts |
| `resources/` | Images, fonts, presets. Resolve paths through `jdxi_editor.resources.resource_path` so they work in frozen bundles |
| `doc/` | Sphinx docs (`*.rst`, published to GitHub Pages by `docs.yml`) and many design notes, gap analyses and critiques (`*.md`) |
| `jdxi_editor/devel/` | Ad-hoc dev and diagnostic scripts, excluded from the wheel |

## Architecture

### Startup
[jdxi_editor/main.py](jdxi_editor/main.py) sets up logging, the `QApplication`, translations and the splash screen, then builds `JDXiInstrument`. [run_editor.py](run_editor.py) is a thin wrapper that sets `HOMEBREW_PREFIX` on macOS so pyfluidsynth can find libfluidsynth.

### Main window
- [ui/windows/jdxi/ui.py](jdxi_editor/ui/windows/jdxi/ui.py): `JDXiWindow(QMainWindow)` builds the layout, menus, status bar and MIDI indicators.
- [ui/windows/jdxi/instrument.py](jdxi_editor/ui/windows/jdxi/instrument.py): `JDXiInstrument(JDXiWindow)` (~2.7k lines) is the controller. It auto-connects to the JD-Xi ports, holds `editor_registry` (a map of `EditorConfig` entries: title, editor class, synth type, MIDI channel, icon), opens editors lazily (`get_existing_editor`, `register_editor`), and routes incoming SysEx to them.

### MIDI I/O: `jdxi_editor/midi/io/`
- `MidiIOHelper` ([helper.py](jdxi_editor/midi/io/helper.py)) is a **process-wide singleton** (`__new__` plus an init guard) that combines `MidiInHandler` and `MidiOutHandler`, both `QObject`s built on python-rtmidi and mido. Treat it as shared global state: constructing it again returns the same object.
- Incoming messages arrive as Qt signals on `MidiInHandler`: `midi_sysex_json` (parsed SysEx as a JSON string), `midi_program_changed`, `midi_control_changed`, `update_tone_name`, `update_program_name` and `midi_message_incoming`. Outgoing messages are mirrored on `midi_message_outgoing`.
- Send methods: `send_midi_message`, `send_raw_message`, `send_program_change`, `send_bank_select_and_program_change`, `send_control_change`, `send_nrpn` / `send_rpn`, and `send_identity_request`.
- Patch files: `load_patch` / `save_patch_as_syx` handle `.msz` (a zip of JSON sections; see `jdxi_editor/devel/MSZ_BUNDLE_FORMAT.md`) and `.syx`.
- No ports is a normal state: the editor opens without a JD-Xi.

### Parameter and address model
- A JD-Xi address is 4 bytes, `JDXiSysExAddress(msb, umb, lmb, lsb)`, defined in [midi/data/address/address.py](jdxi_editor/midi/data/address/address.py). Area and part offsets are IntEnums such as `JDXiSysExOffsetTemporaryToneUMB` (DIGITAL_SYNTH_1/2, ANALOG_SYNTH, DRUM_KIT) and `JDXiSysExOffsetSuperNATURALLMB` (COMMON, MODIFY, PARTIAL_1..3). Combine them with `address.add_offset(...)`.
- Parameters are **enum-like classes of `ParameterSpec` tuples** that subclass picomidi's `AddressParameter`. Each spec holds the address offset, the raw min/max, the display min/max, a description and a display name. They live in `midi/data/parameter/` (for example `DigitalCommonParam`, `DigitalPartialParam`, `AnalogParam`, `DrumPartialParam`, `Effect1Param`, `ArpeggioParam`, `VocalFXParam` and `ProgramCommonParam`). To add a parameter, add a `ParameterSpec` to the right class, using the offset from the Roland MIDI implementation.
- `JDXiSysExComposer` ([midi/sysex/composer.py](jdxi_editor/midi/sysex/composer.py)) composes `(address, param, value)` into DT1 SysEx. The parsers in `midi/sysex/parser/` decode replies into dicts keyed by `SysExSection` (`TEMPORARY_AREA`, `SYNTH_TONE`, and parameter names). Requests (RQ1) are in `midi/sysex/request/`.
- `JDXi` ([core/jdxi.py](jdxi_editor/core/jdxi.py)) is a composition facade: `JDXi.Synth`, `JDXi.UI` (dimensions, theme, style) and `JDXi.Midi` (constants).

### Editors: `jdxi_editor/ui/editors/`
- The base classes are in `ui/editors/synth/`. `SynthBase` ([base.py](jdxi_editor/ui/editors/synth/base.py)) builds controls from specs (`_create_parameter_slider/combo_box/switch`), keeps a `ControlRegistry`, and sends changes through `send_midi_parameter`. That method resolves the address from self or a parent, then calls composer → `midi_helper.send_midi_message`. `SynthEditor` ([editor.py](jdxi_editor/ui/editors/synth/editor.py)) adds preset loading, instrument images and `dispatch_sysex_to_area`, which ignores SysEx for other areas and routes COMMON, MODIFY or partial data to `_update_common_controls`, `_update_modify_controls` or `_update_controls`. Subclasses must implement `_update_controls`.
- UI layout is **spec-driven**: sections declare `SliderSpec(param, label)`, `ComboBoxSpec` and `SwitchSpec` lists (from [ui/widgets/spec.py](jdxi_editor/ui/widgets/spec.py)), and the base builds the widgets. Shared section building blocks (amp, filter, LFO, oscillator, wave) are in `ui/editors/base/`.
- Per-synth editors live in `digital/` (common, partial, tone_modify), `analog/`, `drum/`, `effects/`, `arpeggio/` and `program/`. The non-synth tools are `pattern/` (sequencer), `midi_player/`, `playlist/`, `preset/` and `io/`.
- Reusable widgets are in `ui/widgets/` (slider, switch, combo_box, adsr, rack, transport, digital LCD and others). Styling and themes are in `ui/style/`, and user TOML skins are loaded by `ui/style/user_skins.py`.

### Other subsystems
- `midi/playback/`: transport and state on top of picomidi's `PlaybackEngine`. Per-track volume, transpose and channel maps need picomidi ≥ 0.3.0.
- `midi/file`, `midi/track`, `midi/pattern`, `midi/recording`: MIDI file loading, classification and USB recording.
- `audio/`: the audio monitor (oscilloscope, meters, spectrum) through sounddevice. It listens to an audio input, not to the SoundFont.
- `core/db/`: SQLAlchemy 2.0 persistence for programs, favourites and playlists.
- `jdxi_editor/bundle_imports.py`: imported first in `main.py` so frozen builds pick up fluidsynth, sounddevice and lilypond.

## Conventions and gotchas

- Logging: use `from decologr import Decologr as log` and call `log.message(...)`, `log.error(...)`, `log.parameter(...)` or `log.header_message(...)`, passing `scope=self.__class__.__name__`. Don't use `print`.
- Settings are stored with `QSettings("mabsoft", ...)`. User files live in `~/.jdxi_editor/` (`skins/`, `midi_controllers.json`).
- Several source files are very large (`instrument.py`, `synth/editor.py`, `synth/base.py`). Read the relevant method rather than the whole file.
- `doc/*.md` holds detailed gap analyses and SysEx address maps for effects, vocal FX, arpeggio and NRPN. Check them before changing those areas.
- Don't commit the large local logs or build outputs at the repo root (`rc3_pytest*.log`, `build/`, `dist/`).
- Commit messages usually use a bracketed tag, such as `[docs] ...` or `[release] vX.Y.Z`.
