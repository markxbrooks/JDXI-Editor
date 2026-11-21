Release Candidate Status and Known Issues
=========================================

JD-Xi Editor |release| is a release candidate. The package metadata still
classifies the project as Beta.

Hardware verification
---------------------

``python -m pytest -m hardware`` passed on a connected JD-Xi. That run covered:

* Device identity.
* Temporary program, digital, analog, drum, effect, and arpeggio reads.
* One temporary digital byte, written and then restored.
* A one-bar playback to the instrument.
* A recording capture from the JD-Xi audio input.

Nothing in that run was skipped. The same result is in
``doc/known-issues.md``.

SoundFont playback can run without a JD-Xi when FluidSynth is configured. It
does not verify hardware parameter reads/writes, and it does not provide a
JD-Xi sound model. The Audio Monitor listens to an audio input; it does not
monitor FluidSynth output. A playlist cheat preset is sent on the Analog
part.

Installation compatibility
--------------------------

* Python package metadata requires Python 3.10 or newer. The current CI matrix
  tests Python 3.10, 3.11, and 3.12 on Linux, plus Python 3.11 on macOS and
  Windows. Later versions and other operating systems are not covered by that
  matrix.
* PySide6 is constrained to ``>=6.8.1.1,<6.10``. Version 6.12 is known to
  crash in the main window's queued outgoing-MIDI path. Versions 6.10 and
  6.11 have not been verified.
* Release candidate tags may not have downloadable files attached. Check the
  release page for actual assets before choosing that installation method.

Patch and data handling
-----------------------

**Save Patch** writes the current editor UI values to a file. It does not
first request a complete state from the instrument and is not a backup of the
JD-Xi's user memory. **Load Patch** sends file contents to the instrument.
Keep copies of important patch files and verify their contents before loading.

The editor supports these patch extensions:

* ``.jsz`` — a ZIP bundle of JSON patch files.
* ``.msz`` — a music bundle containing patch JSON and, when present, a MIDI
  file.
* ``.json`` — a single JSON patch file.
* ``.syx`` — concatenated Roland SysEx data.

The Pattern Editor and MIDI File Player have separate MIDI file load/save
workflows; saving a pattern does not create a patch backup.

Before a stable release
-----------------------

The hardware suite above has passed on one connected JD-Xi. A stable release
still needs that pass on each platform the release claims to support, an
issue list for anything that fails, and the intended release artifacts
attached and install-tested. See :doc:`contributing` for the automated and
manual checks described by this repository.
