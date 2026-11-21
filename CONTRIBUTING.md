# Contributing

Issues and changes are welcome. The user-facing install path is [README.md](README.md). Caveats for the current candidate are in [doc/known-issues.md](doc/known-issues.md).

## Tests

From a checkout, with the `dev` extra installed:

```bash
python -m pytest
```

That command skips tests marked `slow`, and it also skips a `hardware` marker. Nothing in the suite uses `hardware` yet. The marker is reserved for a connected JD-Xi. `tests/sheep.mid` is a local file and is not in the repository; the tests that read it are marked `slow` and skip when it is absent. Run the slow set with:

```bash
python -m pytest -m slow
```

CI sets `QT_QPA_PLATFORM=offscreen` so Qt can construct widgets without a display. A missing system MIDI service is reported as no ports. As of 1.0.0rc2 the editor opens in that case instead of exiting from `_rtmidi`.

## picoui

`picoui` is copied into the wheel. The newest release on PyPI, 0.1.3, lacks `picoui.helpers`, `specs.widgets`, `widget.helper`, and the other modules the editor imports. The comment is in [pyproject.toml](pyproject.toml), next to `only-include`.

## Builds

Package commands, the Linux build, and the notes that used to live at the bottom of the README are in [doc/building.md](doc/building.md).
