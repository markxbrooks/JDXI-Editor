Installation
============

Choose an installation method from the project's `GitHub releases
<https://github.com/markxbrooks/JDXI-Editor/releases>`_. Release assets vary
by version and platform; use the files attached to the release you intend to
install rather than copying a versioned filename from an older guide.

.. warning::

   JD-Xi Editor |release| is a release candidate. ``python -m pytest -m hardware``
   has passed on a connected JD-Xi. See :doc:`known-issues` for that result,
   installation limitations, and patch handling caveats.

Requirements
------------

The Python package metadata requires Python 3.10 or newer. CI currently runs
the test suite on Python 3.10, 3.11, and 3.12 on Linux, and on Python 3.11 on
macOS and Windows. This is the tested CI matrix, not a guarantee for every
later Python version or distribution.

The application depends on Qt (PySide6), RtMidi, PyAudio, FluidSynth bindings,
and other packages. The supported PySide6 range is ``>=6.8.1.1,<6.10``; 6.10
and 6.11 have not been verified, and 6.12 is known to crash when the main
window handles outgoing MIDI in a queued slot.

Install a release build
-----------------------

Download an installer or archive attached to the desired release and follow
the platform's normal installation steps. Not every release provides an
installer for every platform. If a release has no suitable asset, use the
Python package or source instructions below.

Install from PyPI
-----------------

Use a virtual environment so the editor's dependencies remain separate from
other Python applications.

.. code-block:: console

   python -m venv .venv

   # macOS / Linux
   source .venv/bin/activate

   # Windows PowerShell (run instead of the previous activation command)
   .venv\Scripts\Activate.ps1

   python -m pip install --upgrade pip
   python -m pip install JDXI-Editor
   jdxi-editor

On macOS, PyAudio does not currently have a PyPI wheel for Apple Silicon, so
pip may try and fail to build it from source. Prefer a frozen macOS release
asset when available. The source-build workaround is documented in
``deps/wheels/README.md`` in the repository.

On Linux, PyAudio may need PortAudio development headers before installation.
For Debian or Ubuntu, install them with ``sudo apt install portaudio19-dev``.
Other distributions may use a differently named PortAudio development
package.

Install from source
-------------------

.. code-block:: console

   git clone https://github.com/markxbrooks/JDXI-Editor.git
   cd JDXI-Editor
   python -m venv .venv

   # Activate the environment using the command for your shell/platform.
   # macOS / Linux:
   source .venv/bin/activate
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1

   python -m pip install --upgrade pip
   python -m pip install -e .
   python -m jdxi_editor.main

The repository's ``requirements.txt`` installs the editable package with
optional SoundFont and plot extras. It is not required for a basic source
install. See :doc:`contributing` for development dependencies and checks.

Optional features
-----------------

* **SoundFont preset lists:** install ``sf2utils`` (included in the
  ``soundfont`` extra) to read preset names from an SF2/SF3 file.
* **FluidSynth playback:** the package includes ``pyfluidsynth`` and
  ``sounddevice``. Configure a SoundFont and audio output in **MIDI
  Configuration**. Native FluidSynth availability can vary by platform.
* **Audio plots:** install the ``plots`` extra for optional Matplotlib-based
  plots.

The exact features that work without a JD-Xi are described in
:doc:`known-issues` and :doc:`playing-midi-files`.
