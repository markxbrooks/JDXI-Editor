jdxi_editor.jdxi.preset.helper
==============================

.. py:module:: jdxi_editor.jdxi.preset.helper

.. autoapi-nested-parse::

   Module: preset_helper
   ======================

   This module defines the `PresetHandler` class, which extends `PresetHelper` to manage
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

   jdxi_editor.jdxi.preset.helper.JDXiPresetHelper


Module Contents
---------------

.. py:class:: JDXiPresetHelper(midi_helper, presets, channel=1, preset_type=JDXiSynth.DIGITAL_SYNTH_1)

   Bases: :py:obj:`PySide6.QtCore.QObject`


   Preset Loading Class


   .. py:attribute:: update_display


   .. py:attribute:: preset_changed


   .. py:attribute:: presets


   .. py:attribute:: channel
      :value: 1



   .. py:attribute:: type
      :value: 'DIGITAL_SYNTH_1'



   .. py:attribute:: preset_number
      :value: 1



   .. py:attribute:: current_preset_zero_indexed
      :value: 0



   .. py:attribute:: midi_requests


   .. py:attribute:: midi_helper


   .. py:attribute:: _initialized
      :value: True



   .. py:method:: get_current_preset()

      Get the current preset details.



   .. py:method:: get_available_presets()

      Get the available presets.



   .. py:method:: load_preset_by_program_change(preset_index, synth_type=JDXiSynth.DIGITAL_SYNTH_1)

      Load a preset using program change.



   .. py:method:: load_preset(preset_data: jdxi_editor.jdxi.preset.button.JDXiPresetButtonData)

      Load the preset based on the provided data

      :param preset_data: JDXIPresetData
      :return: None



   .. py:method:: data_request() -> None

      Request the current value of the NRPN parameter from the device.



   .. py:method:: send_program_change(channel: int, msb: int, lsb: int, pc: int) -> None

      Send a Bank Select and Program Change message

      :param channel: int
      :param msb: int
      :param lsb: int
      :param pc: int
      :return: None



