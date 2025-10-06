jdxi_editor.jdxi.preset.manager
===============================

.. py:module:: jdxi_editor.jdxi.preset.manager


Classes
-------

.. autoapisummary::

   jdxi_editor.jdxi.preset.manager.JDXiPresetManager


Module Contents
---------------

.. py:class:: JDXiPresetManager

   .. py:attribute:: _instance
      :value: None


      Singleton class to manage presets.


   .. py:attribute:: current_preset_number
      :value: 1



   .. py:attribute:: current_preset_index
      :value: 0



   .. py:attribute:: current_preset_name
      :value: 'Init Tone'



   .. py:attribute:: current_preset_names


   .. py:attribute:: preset_channel_map


   .. py:attribute:: preset_synth_map


   .. py:method:: get_preset_name_by_type_and_index(synth_type: jdxi_editor.jdxi.synth.type.JDXiSynth, preset_index: int) -> str

      Get the name of the currently selected preset

      :param synth_type: JDXISynth The type of synth
      :param preset_index: int The index of the preset
      :return: str The name of the preset



   .. py:method:: get_presets_for_synth(synth: jdxi_editor.jdxi.synth.type.JDXiSynth) -> jdxi_editor.jdxi.preset.lists.JDXiPresetToneList

      Get the available presets for the given synth type.

      :param synth: JDXISynth The type of synth
      :return: JDXIPresets The available presets



   .. py:method:: get_presets_for_channel(channel: jdxi_editor.midi.channel.channel.MidiChannel) -> jdxi_editor.jdxi.preset.lists.JDXiPresetToneList

      Get the available presets for the given channel.

      :param channel: MidiChannel The MIDI channel
      :return: JDXIPresets The available presets



   .. py:method:: set_current_preset_name(preset_name: str)

      Set the current global tone name.

      :param preset_name: str The name of the preset



   .. py:method:: set_preset_name_by_type(preset_type: str, preset_name: str)

      Set the preset name for a specific tone type.

      :param preset_type: str The type of preset
      :param preset_name: str The name of the preset



   .. py:method:: get_preset_name_by_type(tone_type: jdxi_editor.jdxi.synth.type.JDXiSynth) -> str

      Get the tone name for a specific tone type.

      :param tone_type: JDXISynth The type of tone
      :return: str The name of the tone



   .. py:method:: reset_all_presets()

      Reset all tone names to 'Init Tone'.



   .. py:method:: _update_display()

      Update the display.



