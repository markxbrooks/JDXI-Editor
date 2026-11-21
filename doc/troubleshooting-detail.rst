Troubleshooting
===============

No JD-Xi MIDI ports appear
--------------------------

* Confirm the instrument is powered on and connected through its USB COMPUTER
  port.
* In **MIDI Configuration**, press **Refresh Ports** after connecting the
  instrument.
* Close other applications that may have opened the JD-Xi's MIDI ports, then
  restart JD-Xi Editor and check again.
* On Linux, confirm that the user has access to the ALSA sequencer and that
  the system's MIDI services and permissions are configured. Group names and
  setup steps vary by distribution; do not assume a particular ``audio`` group
  is required.

The editor does not read or write hardware values
-------------------------------------------------

Verify that **MIDI Output** points to the JD-Xi and that **Request data from
the JD-Xi** is enabled. The checkbox controls automatic data requests when
editors open, on program changes, and on refresh. An explicit **Read** action
still sends a request. Try one editor and one parameter first. See
:doc:`known-issues` for the current unverified hardware areas in this release
candidate.

No audio from FluidSynth
------------------------

* Confirm **Enable FluidSynth for local playback** is on.
* Choose an existing SF2/SF3 file and an available **Audio output** device in
  **MIDI Configuration**.
* Use **Start** and **Test Note** in that dialog. Check the operating system's
  output device and volume if the test note is silent.
* FluidSynth audio is separate from the MIDI Output port. The Audio Monitor
  listens to an audio input and does not show FluidSynth's output.

Python installation fails
--------------------------

* Use Python 3.10 or newer and install in a fresh virtual environment.
* Keep PySide6 within the declared ``>=6.8.1.1,<6.10`` range. Version 6.12 is
  known to crash in a queued MIDI-output path; 6.10 and 6.11 have not been
  verified.
* On Debian/Ubuntu, install ``portaudio19-dev`` before pip installation if
  PyAudio cannot build. Other Linux distributions use their own package name.
* On Apple Silicon, prefer a frozen macOS release build when available:
  PyAudio has no macOS arm64 wheel on PyPI and its source build may fail with
  the newest SDK. See :doc:`installation` for the source-workaround reference.

Patch appears different after loading
-------------------------------------

Patch load sends the selected file's data to the instrument. Patch save writes
the editor's current UI values; it does not first request a complete state
from the JD-Xi and it does not create an instrument-memory backup. Read the
hardware state before editing when possible, and keep independent copies of
important files. See :doc:`known-issues` for format details and limitations.

Report a problem
----------------

Open an issue at the `GitHub issue tracker
<https://github.com/markxbrooks/JDXI-Editor/issues>`_. Include:

* JD-Xi Editor version and installation method.
* Operating system version, architecture, and Python version if applicable.
* JD-Xi firmware version and whether it was connected.
* MIDI input/output selections and the steps that reproduce the problem.
* Relevant error text or logs. Remove personal paths or other private data
  before attaching logs.
