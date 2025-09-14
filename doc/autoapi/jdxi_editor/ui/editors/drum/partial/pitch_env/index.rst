jdxi_editor.ui.editors.drum.partial.pitch_env
=============================================

.. py:module:: jdxi_editor.ui.editors.drum.partial.pitch_env

.. autoapi-nested-parse::

   Module: drum_pitch_env
   ================

   This module defines the `DrumPitchEnvSection` class, which provides a PySide6-based
   user interface for editing drum pitch envelope parameters in the Roland JD-Xi synthesizer.
   It extends the `QWidget` base class and integrates MIDI communication for real-time
   parameter adjustments and preset management.

   Key Features:
   -------------
   - Provides a graphical editor for modifying drum pitch envelope parameters, including
     from PySide6.QtWidgets import QGroupBox, QFormLayout, QWidget, QVBoxLayout, QScrollArea
     pitch env depth, pitch env velocity sens, pitch env time1 velocity sens, pitch env time4 velocity sens,
     pitch env time1, pitch env time2, pitch env time3, pitch env time4, pitch env level0, pitch env level1,
     pitch env level2, pitch env level3, and pitch env level4.

   Dependencies:
   -------------
   - PySide6 (for UI components and event handling)
   - MIDIHelper (for handling MIDI communication)
   - PresetHandler (for managing synth presets)
   - Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

   Usage:
   ------
   The `DrumPitchEnvSection` class can be instantiated as part of a larger PySide6 application.
   It requires a `MIDIHelper` instance for proper communication with the synthesizer.

   Example:
   --------
       midi_helper = MIDIHelper()
       editor = DrumPitchEnvSection(midi_helper)
       editor.show()



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.drum.partial.pitch_env.DrumPitchEnvSection


Module Contents
---------------

.. py:class:: DrumPitchEnvSection(controls: dict[jdxi_editor.midi.data.parameter.drum.partial.AddressParameterDrumPartial, PySide6.QtWidgets.QWidget], create_parameter_combo_box: Callable, create_parameter_slider: Callable, midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Drum Pitch Env Section for the JDXI Editor


   .. py:attribute:: controls


   .. py:attribute:: _create_parameter_slider


   .. py:attribute:: _create_parameter_combo_box


   .. py:attribute:: midi_helper


   .. py:method:: setup_ui() -> None

      setup UI



