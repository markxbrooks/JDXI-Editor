Playing MIDI Files
==================

JD-Xi Editor includes a MIDI File Player and a Pattern Editor. The player
loads Standard MIDI Files (``.mid`` or ``.midi``), provides track and channel
controls, and can send playback to a JD-Xi or use FluidSynth with a SoundFont.
The Pattern Editor loads a MIDI file into a step grid for editing and saving.

Playback choices
----------------

**JD-Xi hardware**
   Connect the instrument, select its MIDI output in **MIDI Configuration**,
   and assign tracks to the intended channels. The default JD-Xi mapping is
   channel 1 to Digital 1, channel 2 to Digital 2, channel 3 to Analog, and
   channel 10 to Drums.

**FluidSynth**
   Enable **Enable FluidSynth for local playback**, select an SF2/SF3 file,
   choose an audio output, and start FluidSynth in **MIDI Configuration**.
   This is software playback and does not validate JD-Xi hardware
   communication. The Audio Monitor listens to an audio input, not to
   FluidSynth's output.

Basic workflow
--------------

1. Open **MIDI File Player** and load a ``.mid`` or ``.midi`` file through the
   File menu or drag-and-drop.
2. For a general MIDI file, use **Fit to the JD-Xi** › **Assign tracks to
   parts…** to put its tracks on the JD-Xi's parts and choose their sounds;
   confirm the results before playback.
3. Select the intended output and play the file. For hardware, listen to the
   JD-Xi; for FluidSynth, check the configured audio output.
4. To edit steps, use **Load into Pattern Editor**. Save the resulting pattern
   as a MIDI file from the Pattern Editor.

Channel assignment conventions
------------------------------

The default routing uses MIDI channels 1, 2, 3, and 10 for the JD-Xi's four
parts. **Assign tracks to parts…** and **Starting sounds** are starting
points, not a substitute for checking the track headers.
When multiple tracks share a channel, MIDI channel-level messages and note
state can affect more than one track.

Supported input is Standard MIDI File Type 0 and Type 1. A one-bar playback
and a recording capture passed in the hardware suite. See
:doc:`known-issues` for that result and the other release-candidate limits.
