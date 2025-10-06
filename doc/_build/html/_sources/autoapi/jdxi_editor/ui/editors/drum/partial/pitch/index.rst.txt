jdxi_editor.ui.editors.drum.partial.pitch
=========================================

.. py:module:: jdxi_editor.ui.editors.drum.partial.pitch

.. autoapi-nested-parse::

   Module: drum_pitch
   ================

   This module defines the `DrumPitchSection` class, which provides a PySide6-based
   user interface for editing drum pitch parameters in the Roland JD-Xi synthesizer.
   It extends the `QWidget` base class and integrates MIDI communication for real-time
   parameter adjustments and preset management.

   Key Features:
   -------------
   - Provides a graphical editor for modifying drum pitch parameters, including
     partial level, partial coarse tune, partial fine tune, partial random pitch depth,
     partial pan, partial random pan depth, partial alternate pan depth, and partial env mode.

   Dependencies:
   -------------
   - PySide6 (for UI components and event handling)
   - MIDIHelper (for handling MIDI communication)
   - PresetHandler (for managing synth presets)
   - Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

   Usage:
   ------
   The `DrumPitchSection` class can be instantiated as part of a larger PySide6 application.
   It requires a `MIDIHelper` instance for proper communication with the synthesizer.

   Example:
   --------
       midi_helper = MIDIHelper()
       editor = DrumPitchSection(midi_helper)
       editor.show()



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.drum.partial.pitch.DrumPitchSection


Module Contents
---------------

.. py:class:: DrumPitchSection(controls: dict[jdxi_editor.midi.data.parameter.drum.partial.AddressParameterDrumPartial, PySide6.QtWidgets.QWidget], create_parameter_combo_box: Callable, create_parameter_slider: Callable, midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Drum Pitch Section for the JDXI Editor


   .. py:attribute:: controls


   .. py:attribute:: _create_parameter_slider


   .. py:attribute:: _create_parameter_combo_box


   .. py:attribute:: midi_helper


   .. py:method:: setup_ui() -> None

      setup UI



