jdxi_editor.ui.editors.drum.partial.tva
=======================================

.. py:module:: jdxi_editor.ui.editors.drum.partial.tva

.. autoapi-nested-parse::

   Module: drum_tva
   ==============

   This module defines the `DrumTVASection` class, which provides a PySide6-based
   user interface for editing drum TVA parameters in the Roland JD-Xi synthesizer.
   It extends the `QWidget` base class and integrates MIDI communication for real-time
   parameter adjustments and preset management.

   Key Features:
   -------------
   - Provides a graphical editor for modifying drum TVA parameters, including
     level velocity curve, level velocity sens, env time1 velocity sens, env time4 velocity sens,
     env time1, env time2, env time3, env time4, env level1, env level2, env level3, and env level4.

   Dependencies:
   -------------
   - PySide6 (for UI components and event handling)
   - MIDIHelper (for handling MIDI communication)
   - PresetHandler (for managing synth presets)
   - Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

   Usage:
   ------
   The `DrumTVASection` class can be instantiated as part of a larger PySide6 application.
   It requires a `MIDIHelper` instance for proper communication with the synthesizer.

   Example:
   --------
       midi_helper = MIDIHelper()
       editor = DrumTVASection(midi_helper)
       editor.show()



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.drum.partial.tva.DrumTVASection


Module Contents
---------------

.. py:class:: DrumTVASection(controls: dict[jdxi_editor.midi.data.parameter.drum.partial.AddressParameterDrumPartial, PySide6.QtWidgets.QWidget], create_parameter_combo_box: Callable, create_parameter_slider: Callable, midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Drum TVA Section for the JDXI Editor


   .. py:attribute:: controls


   .. py:attribute:: _create_parameter_slider


   .. py:attribute:: _create_parameter_combo_box


   .. py:attribute:: midi_helper


   .. py:method:: setup_ui()

      setup UI



