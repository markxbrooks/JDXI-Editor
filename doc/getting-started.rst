Getting Started
===============

JD-Xi Editor is a desktop companion for editing JD-Xi sounds and working with
MIDI files. A connected instrument is required for sending and reading JD-Xi
parameters. Some MIDI-file playback is also available through FluidSynth and a
SoundFont without the hardware; see :doc:`known-issues` for current
limitations.

1. :doc:`installation` — install a release build, the Python package, or the
   source checkout.
2. Connect and power on the JD-Xi if you want to edit or audition sounds on the
   instrument.
3. Open **MIDI Configuration** and select the JD-Xi input and output ports.
   Keep **Request data from the JD-Xi** enabled for hardware use.
4. Open an editor, use its **Read** or refresh action to request the current
   values, then edit a parameter and confirm the instrument responds.
5. Save patches to files you control. **Save Patch** is a file export, not a
   backup of the JD-Xi's user memory.

For detailed connection steps, see :doc:`usage`. For file playback, see
:doc:`playing-midi-files`. For known caveats before trying the release
candidate, read :doc:`known-issues`.

.. toctree::
   :maxdepth: 1

   installation
   usage
   playing-midi-files
   known-issues
   troubleshooting
