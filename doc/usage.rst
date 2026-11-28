Connect and Use the Editor
==========================

Connect a JD-Xi
---------------

1. Connect the JD-Xi's USB COMPUTER port to the computer and turn the
   instrument on.
2. Start JD-Xi Editor and open **MIDI Configuration** from the application
   menu.
3. Choose the JD-Xi MIDI input and output ports. Input receives MIDI from the
   instrument; output sends parameter changes and notes to it. The JD-Xi's
   ports are listed first, marked ★; **Find the JD-Xi** chooses them.
4. **Test connection** asks the instrument who it is. The line at the top of
   the dialog says whether the JD-Xi replied, another instrument replied, or
   nothing replied. It runs by itself when the dialog opens with ports open.
5. Leave **Request data from the JD-Xi** enabled for hardware use, then close
   the dialog with **OK**. If the device was connected after the dialog
   opened, choose **Refresh Ports** and select its ports.
6. Open the editor you want to use and request/read the current data before
   editing. Change one parameter and confirm that the instrument responds.

If the editor shows no JD-Xi ports, close other MIDI applications that may
have opened the device, reconnect the USB cable, then refresh the port list.
See :doc:`troubleshooting` if it remains unavailable.

Use FluidSynth without a JD-Xi
------------------------------

Open **MIDI Configuration**, enable **Enable FluidSynth for local playback**,
select a SoundFont file (SF2/SF3), choose an audio output, and use **Start** or
**Test Note** to check audio. FluidSynth is for local MIDI playback; it does
not emulate the JD-Xi parameter editor or receive a hardware response. The
Audio Monitor listens to an audio input and does not monitor FluidSynth's
output.

Edit and save a sound
--------------------

1. Connect the JD-Xi and select its MIDI ports as described above.
2. Open the relevant Digital, Analog, Drum, Effects, Vocal Effects, or
   Arpeggiator editor.
3. Read/request the current hardware data before editing when you need the
   editor values to reflect the instrument.
4. Make a small change and listen on the JD-Xi.
5. Use **Save Patch** to export the editor's current values to a file. Treat
   that file as a snapshot of the UI values, and keep a separate copy of any
   important patch files.

Patch formats and limitations are listed in :doc:`known-issues`.

Work with MIDI files
--------------------

Open **MIDI File Player**, load a Standard MIDI File, assign tracks to the
desired channels, and start playback. With a JD-Xi selected, output is sent to
the instrument. With FluidSynth enabled and configured, playback can use the
SoundFont. Tracks assigned to channels 1, 2, 3, and 10 correspond to Digital
1, Digital 2, Analog, and Drums in the default JD-Xi mapping. These are
channel conventions; check the track assignments before playback.

Use **Load into Pattern Editor** to transfer a file into the step editor. The
Pattern Editor can save its edited pattern as a MIDI file. For details and
the hardware-suite result, see :doc:`playing-midi-files` and
:doc:`known-issues`.
