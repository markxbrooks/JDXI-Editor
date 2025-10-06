jdxi_editor.ui.editors.drum.partial.editor
==========================================

.. py:module:: jdxi_editor.ui.editors.drum.partial.editor

.. autoapi-nested-parse::

   This module defines the `DrumPartialEditor` class for editing drum kit parameters within a graphical user interface (GUI).

   The `DrumPartialEditor` class allows users to modify various parameters related to drum sounds, including pitch, output, TVF (Time Variant Filter), pitch envelope, WMT (Wave Modulation Time), and TVA (Time Variant Amplitude) settings. The class provides a comprehensive layout with controls such as sliders, combo boxes, and spin boxes to adjust the parameters.

   Key functionalities of the module include:
   - Displaying parameter controls for a specific drum partial.
   - Providing detailed access to different parameter groups such as pitch, output, and TVA.
   - Handling MIDI and tone area settings for drum kit editing.
   - Handling dynamic address assignment for each partial based on its name.

   Dependencies:
   - `logging`: For logging initialization and error handling.
   - `PySide6.QtWidgets`: For GUI components such as `QWidget`, `QVBoxLayout`, `QScrollArea`, etc.
   - `jdxi_manager.midi.data.drums`: For drum-related data and operations like retrieving drum waves.
   - `jdxi_manager.midi.data.parameter.drums`: For specific drum parameter definitions and utilities.
   - `jdxi_manager.midi.data.constants.sysex`: For MIDI-related constants like `TEMPORARY_TONE_AREA` and `DRUM_KIT_AREA`.
   - `jdxi_manager.ui.widgets`: For custom UI widgets such as `Slider`, `ComboBox`, and `SpinBox`.

   The `DrumPartialEditor` is designed to work within a larger system for managing drum kit tones, providing an intuitive interface for modifying various sound parameters.



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.drum.partial.editor.DrumPartialEditor


Module Contents
---------------

.. py:class:: DrumPartialEditor(midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper] = None, partial_number: int = 0, partial_name: Optional[str] = None, parent: Optional[PySide6.QtWidgets.QWidget] = None)

   Bases: :py:obj:`jdxi_editor.ui.editors.synth.partial.PartialEditor`


   Editor for address single partial


   .. py:attribute:: midi_helper
      :value: None



   .. py:attribute:: partial_number
      :value: 0



   .. py:attribute:: partial_name
      :value: None



   .. py:attribute:: partial_address_default


   .. py:attribute:: partial_address_map


   .. py:attribute:: preset_helper
      :value: None



   .. py:attribute:: controls
      :type:  Dict[jdxi_editor.midi.data.parameter.drum.partial.AddressParameterDrumPartial, PySide6.QtWidgets.QWidget]


