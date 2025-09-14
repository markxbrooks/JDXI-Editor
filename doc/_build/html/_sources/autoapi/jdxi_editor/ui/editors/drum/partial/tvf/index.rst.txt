jdxi_editor.ui.editors.drum.partial.tvf
=======================================

.. py:module:: jdxi_editor.ui.editors.drum.partial.tvf

.. autoapi-nested-parse::

   Module: drum_tvf
   ==============

   This module defines the `DrumTVFSection` class, which provides a PySide6-based
   user interface for editing drum TVF parameters in the Roland JD-Xi synthesizer.
   It extends the `QWidget` base class and integrates MIDI communication for real-time
   parameter adjustments and preset management.

   Key Features:
   -------------
   - Provides a graphical editor for modifying drum TVF parameters, including
     filter type, cutoff frequency, cutoff velocity curve, env depth, env velocity curve type,
     env velocity sens, env time1 velocity sens, env time4 velocity sens, env time1, env time2,
     env time3, env time4, env level0, env level1, env level2, env level3, and env level4.

   Dependencies:
   -------------
   - PySide6 (for UI components and event handling)
   - MIDIHelper (for handling MIDI communication)
   - PresetHandler (for managing synth presets)
   - Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

   Usage:
   ------
   The `DrumTVFSection` class can be instantiated as part of a larger PySide6 application.
   It requires a `MIDIHelper` instance for proper communication with the synthesizer.

   Example:
   --------
       midi_helper = MidiIOHelper()
       editor = DrumTVFSection(midi_helper)
       editor.show()



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.drum.partial.tvf.DrumTVFSection


Module Contents
---------------

.. py:class:: DrumTVFSection(controls: dict[jdxi_editor.midi.data.parameter.drum.partial.AddressParameterDrumPartial, PySide6.QtWidgets.QWidget], create_parameter_combo_box: Callable, create_parameter_slider: Callable, midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Drum TVF Section for the JDXI Editor


   .. py:attribute:: controls


   .. py:attribute:: midi_helper


   .. py:attribute:: _create_parameter_slider


   .. py:attribute:: _create_parameter_combo_box


   .. py:method:: setup_ui()

      setup UI



