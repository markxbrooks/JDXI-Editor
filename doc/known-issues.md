# Known issues

1.0.0 is the first stable release. The app stays Beta. This page restates the caveats already in [CHANGELOG.md](../CHANGELOG.md).

## Hardware

`python -m pytest -m hardware` passed on a connected JD-Xi: identity, temporary program, digital, analog, drum, effect, and arpeggio reads, one restored temporary digital byte, a one-bar playback, and a recording capture from the JD-Xi audio input. Nothing in that run was skipped.

SoundFont playback and the Audio Monitor run without a JD-Xi. The monitor listens to an audio input. It does not hear the SoundFont. A playlist cheat preset is sent on the Analog part.

## Install

- **PySide6** is pinned to `>=6.8.1.1,<6.10`. 6.12 crashes the main window when a queued slot receives outgoing MIDI. 6.10 and 6.11 have not been tried.
- **The candidate `.deb`** is versioned `1.0.0rc1`, which dpkg orders after `1.0.0`. apt will not upgrade that package to the finished release. Reinstall.
- **1.0.0rc1 and 1.0.0rc2** were tagged without downloadable files.

## Patches

Load Patch transmits the file to the JD-Xi. Save Patch writes a file on disk. Neither is a backup of the instrument's user memory. The formats (`.jsz`, `.msz`, `.json`, `.syx`) are described in [features-and-usage.md](features-and-usage.md).
