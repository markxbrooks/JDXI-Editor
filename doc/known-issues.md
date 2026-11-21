# Known issues

1.0.0rc2 is a candidate. The app stays Beta. This page restates the caveats already in [CHANGELOG.md](../CHANGELOG.md).

## Hardware

A connected JD-Xi has not had a stable pass. These are still unverified:

- Identity
- Program read and write
- Digital
- Analog
- Drums
- Effects
- Arpeggiator
- Pattern
- Playback to the instrument
- Recording

SoundFont playback and the Audio Monitor run without a JD-Xi. The monitor listens to an audio input. It does not hear the SoundFont. A playlist cheat preset is sent on the Analog part.

## Install

- **PySide6** is pinned to `>=6.8.1.1,<6.10`. 6.12 crashes the main window when a queued slot receives outgoing MIDI. 6.10 and 6.11 have not been tried.
- **Apple Silicon `pip install`** cannot build PyAudio. PyPI has no macOS arm64 wheel, and the source build fails against the newest SDK. A frozen `.dmg` or `.pkg` bundles PyAudio. A checkout follows [deps/wheels/README.md](../deps/wheels/README.md).
- **The candidate `.deb`** is versioned `1.0.0rc1`, which dpkg orders after `1.0.0`. apt will not upgrade that package to the finished release. Reinstall.
- **1.0.0rc1 and 1.0.0rc2** were tagged without downloadable files.

## Patches

Load Patch transmits the file to the JD-Xi. Save Patch writes a file on disk. Neither is a backup of the instrument's user memory. The formats (`.jsz`, `.msz`, `.json`, `.syx`) are described in [features-and-usage.md](features-and-usage.md).
