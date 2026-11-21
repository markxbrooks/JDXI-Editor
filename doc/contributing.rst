Development and Release Checks
==============================

Development environment
-----------------------

The project requires Python 3.10 or newer. From a checkout, create a virtual
environment and install the editable package with development tools:

.. code-block:: console

   python -m venv .venv

   # macOS / Linux
   source .venv/bin/activate

   # Windows PowerShell (run instead of the previous activation command)
   .venv\Scripts\Activate.ps1

   python -m pip install --upgrade pip
   python -m pip install -e ".[dev]"

To build the Sphinx documentation, install ``requirements-docs.txt`` and run:

.. code-block:: console

   python -m pip install -r requirements-docs.txt
   sphinx-build -b html doc doc/_build/html

Automated checks
----------------

Run the default automated test suite from the repository root with:

.. code-block:: console

   python -m pytest

The default pytest configuration excludes tests marked ``slow`` and
``hardware``. Slow tests may depend on local files or real-time playback;
hardware tests require a connected JD-Xi. Run these categories only when the
required setup is available:

.. code-block:: console

   python -m pytest -o addopts= -m slow
   python -m pytest -o addopts= -m hardware

The CI workflow runs the default suite on Linux, macOS, and Windows with
Python 3.11, plus Python 3.10 and 3.12 on Linux. It also builds wheel and
source distributions, checks package metadata and size, and installs the
wheel in a clean environment to verify that the application opens.

Manual hardware release pass
----------------------------

Automated tests cannot establish reliable communication with a physical
instrument. For each platform being claimed, record the OS/version,
architecture, JD-Xi firmware, and MIDI connection method, then check:

* The editor detects the JD-Xi input and output ports.
* Identity and program data requests return data; editing a value sends the
  expected update.
* Digital, Analog, Drum, Effects, and Arpeggiator editors read and write
  representative values.
* Pattern playback and MIDI File Player playback reach the intended parts.
* Recording produces a file that can be reopened or played back.
* Disconnecting or restarting the instrument does not leave the editor in a
  misleading connected state.

Record failures and untested areas in the release notes and
:doc:`known-issues`; do not describe a workflow as hardware-verified based on
FluidSynth playback alone.

Release artifacts
-----------------

The Python package release workflow is triggered by a GitHub release and
checks that the release tag matches ``jdxi_editor/project.py`` before
publishing. Before creating a stable release, verify the tagged source, CI
result, release notes, and platform assets. Install and launch each artifact
from a clean environment. The repository's package CI does not, by itself,
verify every frozen desktop installer.
