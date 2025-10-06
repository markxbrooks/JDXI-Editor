jdxi_editor.ui.editors.drum.partial.output
==========================================

.. py:module:: jdxi_editor.ui.editors.drum.partial.output

.. autoapi-nested-parse::

   Module: drum_output
   ================

   This module defines the `DrumOutputSection` class, which provides a PySide6-based
   user interface for editing drum output parameters in the Roland JD-Xi synthesizer.
   It extends the `QWidget` base class and integrates MIDI communication for real-time
   parameter adjustments and preset management.

   Key Features:
   -------------
   - Provides a graphical editor for modifying drum output parameters, including
     from PySide6.QtWidgets import QGroupBox, QFormLayout, QWidget, QVBoxLayout, QScrollArea
     partial output level, partial chorus send level, partial reverb send level, and partial output assign.

   Dependencies:
   -------------
   - PySide6 (for UI components and event handling)
   - MIDIHelper (for handling MIDI communication)
   - PresetHandler (for managing synth presets)
   - Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

   Usage:
   ------
   The `DrumOutputSection` class can be instantiated as part of a larger PySide6 application.
   It requires a `MIDIHelper` instance for proper communication with the synthesizer.

   Example:
   --------
       midi_helper = MIDIHelper()
       editor = DrumOutputSection(midi_helper)
       editor.show()



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.drum.partial.output.DrumOutputSection


Module Contents
---------------

.. py:class:: DrumOutputSection(controls: dict[jdxi_editor.midi.data.parameter.drum.partial.AddressParameterDrumPartial, PySide6.QtWidgets.QWidget], create_parameter_combo_box: Callable, create_parameter_slider: Callable, midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Drum Output Section for the JDXI Editor


   .. py:attribute:: controls


   .. py:attribute:: _create_parameter_slider


   .. py:attribute:: _create_parameter_combo_box


   .. py:attribute:: midi_helper


   .. py:method:: setup_ui() -> None

      setup UI



