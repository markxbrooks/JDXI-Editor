MIDI File Player
================

The MIDI File Player loads Standard MIDI Files and plays them through the
selected MIDI output. That output can be a connected JD-Xi or FluidSynth when
software playback is configured. The player also fits a file to the JD-Xi's
parts, and provides a path into the Pattern Editor.

Load and route a file
---------------------

1. Open a ``.mid`` or ``.midi`` file from the File menu, or drag it into the
   player.
2. The **Fit to the JD-Xi** group says what of the file the JD-Xi plays. For a
   general MIDI file, use **Assign tracks to parts…** (below).
3. **Starting sounds** gives the parts a sound to start from, also written into
   the file: Digital 1 Picked Bass, Digital 2 Piano, Analog JP8 Strings.
4. Select the intended MIDI output and start playback.

The JD-Xi plays four parts, each on its own channel: channel 1 (Digital 1),
channel 2 (Digital 2), channel 3 (Analog), and channel 10 (Drums). Notes on any
other channel are not heard.

Fit to the JD-Xi
----------------

**Assign tracks to parts…** proposes a part for each track that plays notes, in
a table you can change before **Apply**: the drum tracks to Drums; for each
melodic part the one track recognised best for it (the bass to Digital 1, keys
or guitars to Digital 2, strings to Analog); the other tracks are not played.
**None played** sets every track to "Not played", **Proposal** and **As now**
switch between the proposal and the parts the tracks are on. The proposal is
heuristic, so check it before sending a file to the instrument.

**Sounds of the parts**, under the table, picks for each part the JD-Xi preset
closest to the General MIDI instrument of its main track. On Apply it takes the
place of the file's program changes on that part and is sent to the JD-Xi. Each
can be changed, or left **Unchanged**.

Channels and the event filter
-----------------------------

Each channel has a mute (**M**) and a solo (**S**) button. With any channel
soloed, only the soloed ones play; the mutes come back when the solos go off.
A track without a name shows, in grey, the instrument it plays.

In the event filter, **GM** (on by default) blocks the file's program changes
that do not choose a JD-Xi sound: General MIDI ones would change the parts'
sounds. **PC** blocks all program changes, **CC** all control changes.

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
