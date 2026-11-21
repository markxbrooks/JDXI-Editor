MIDI File Player
================

The MIDI File Player loads Standard MIDI Files and plays them through the
selected MIDI output. That output can be a connected JD-Xi or FluidSynth when
software playback is configured. The player also provides track
classification, channel assignment, and a path into the Pattern Editor.

Load and route a file
---------------------

1. Open a ``.mid`` or ``.midi`` file from the File menu, or drag it into the
   player.
2. Check each track's channel in its header. **Detect Drums** and **Classify
   Tracks** can help propose assignments; assignments can be changed in the
   track list.
3. **Apply Presets** inserts JD-Xi presets for the selected channels. Confirm
   those choices on the instrument before playback.
4. Select the intended MIDI output and start playback.

The default JD-Xi part mapping is channel 1 (Digital 1), channel 2 (Digital
2), channel 3 (Analog), and channel 10 (Drums). Automatic classification is
heuristic, so inspect channels and track names before sending a file to the
instrument.

Use FluidSynth
--------------

In **MIDI Configuration**, enable **Enable FluidSynth for local playback**,
select a SoundFont (SF2/SF3), select an audio output, and use **Start** or
**Test Note** to confirm sound. **Use SoundFont List** additionally uses
SoundFont preset names in supported preset lists; it is separate from simply
playing through FluidSynth. See :doc:`installation` for optional package
dependencies and :doc:`known-issues` for the distinction between software
playback and hardware verification.

Pattern Editor integration
--------------------------

Use **Load into Pattern Editor** to transfer the loaded MIDI file for step
editing. Save the edited pattern from the Pattern Editor as a MIDI file.
Pattern export does not save a JD-Xi patch or a copy of the instrument's
memory.

For the complete workflow and routing notes, see :doc:`playing-midi-files`.
