Introduction
============

JD-Xi Editor is an independent desktop companion for the Roland JD-Xi. It
provides editors for synthesizer parts, drums, effects, vocal effects, and
arpeggiator settings, alongside tools for MIDI-file playback and step-based
pattern editing.

Hardware editing uses MIDI to request and send parameter data. Connect a
JD-Xi and select its input and output ports to use those workflows. FluidSynth
can provide local MIDI-file playback with a SoundFont, but it is not a JD-Xi
emulator and does not validate hardware communication.

The package metadata requires Python 3.10 or newer. See
:doc:`installation` for the CI-tested Python and platform matrix, and
:doc:`known-issues` for the current release-candidate status and limitations.

.. note::

   This is an unofficial project and is not affiliated with, endorsed by, or
   sponsored by Roland Corporation. Roland and JD-Xi are trademarks of Roland
   Corporation.

Next steps
----------

* :doc:`getting-started` for a short setup path.
* :doc:`installation` for release, PyPI, and source installation.
* :doc:`usage` for MIDI configuration and basic workflows.
* :doc:`playing-midi-files` for MIDI playback and Pattern Editor workflows.
* :doc:`known-issues` before relying on release-candidate hardware behavior.
