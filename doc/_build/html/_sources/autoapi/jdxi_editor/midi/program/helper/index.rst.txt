jdxi_editor.midi.program.helper
===============================

.. py:module:: jdxi_editor.midi.program.helper

.. autoapi-nested-parse::

   Module: program_handler
   ======================

   This module defines the `PresetHandler` class, which extends `PresetLoader` to manage
   preset selection and navigation for a MIDI-enabled synthesizer.

   Classes:
   --------
   - `PresetHandler`: Handles preset loading, switching, and signaling for UI updates.

   Dependencies:
   -------------
   - `PySide6.QtCore` (Signal, QObject) for event-driven UI interaction.
   - `jdxi_manager.midi.data.presets.type.PresetType` for managing preset types.
   - `jdxi_manager.midi.preset.loader.PresetLoader` as the base class for preset loading.

   Functionality:
   --------------
   - Loads presets via MIDI.
   - Emits signals when a preset changes (`preset_changed`).
   - Supports navigation through available presets (`next_tone`, `previous_tone`).
   - Retrieves current preset details (`get_current_preset`).

   Usage:
   ------
   This class is typically used within a larger MIDI control application to handle
   preset changes and communicate them to the UI and MIDI engine.



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.program.helper.JDXiProgramHelper


Module Contents
---------------

.. py:class:: JDXiProgramHelper(midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper], channel: int)

   Bases: :py:obj:`PySide6.QtCore.QObject`


   Preset Loading Class


   .. py:attribute:: program_changed


   .. py:attribute:: _instance
      :value: None



   .. py:method:: next_program()

      Increase the tone index and load the new program



   .. py:method:: previous_program()

      Decrease the tone index and load the new program.



   .. py:method:: get_current_program() -> tuple[str, int]

      Get current program bank and number

      :return: tuple[str, int]



   .. py:method:: load_program(bank_letter: str, program_number: int) -> None

      Load Program

      :param bank_letter: str
      :param program_number: int
      :return: None



   .. py:method:: data_request() -> None

      Request the current value of the NRPN parameter from the device.



