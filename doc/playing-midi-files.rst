Playing MIDI Files
==================

JDXI-Editor provides two main tools for working with MIDI files: the **Pattern Sequencer** for step-based editing and the **MIDI File Player** for playback and track management.

Overview
=======

**MIDI File Player**
   Load standard MIDI files (.mid, .midi), classify tracks (Detect Drums, Classify Tracks), assign channels to the JD-Xi's four parts (Digital 1, Digital 2, Analog, Drums), and play through the synthesizer or FluidSynth (SoundFont) when no hardware is connected.

**Pattern Sequencer**
   Load MIDI files into a 4×16 step grid, edit notes/velocity/duration per step, and save patterns back to MIDI files. Integrates with the MIDI File Player via "Load into Pattern Editor."

Typical Workflow
================

1. **Load a MIDI file** in the MIDI File Player (File → Open… or drag-and-drop)
2. **Classify tracks** (optional): Use Detect Drums and Classify Tracks to auto-assign channels
3. **Apply changes**: Apply All Track Changes or Apply Presets
4. **Play**: Start playback (JD-Xi or FluidSynth)
5. **Edit in Pattern Editor** (optional): Load into Pattern Editor → edit steps → Save Pattern

SoundFont Playback
==================

When no JD-Xi is connected, enable **Enable FluidSynth for local playback** in MIDI Configuration. The MIDI File Player will use a configured SoundFont (.sf2/.sf3) for software playback. See :doc:`features-and-usage` for SoundFont setup.

Available Tools
===============

* :doc:`Pattern Sequencer <pattern_sequencer>` — 4×16 step grid, MIDI load/save, part muting
* :doc:`MIDI File Player <midi_file_player>` — Track classification, channel assignment, playback
