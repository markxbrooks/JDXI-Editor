jdxi_editor.ui.editors.effects.common
=====================================

.. py:module:: jdxi_editor.ui.editors.effects.common

.. autoapi-nested-parse::

   Module: effects_editor

   This module defines the `EffectsEditor` class, which provides a PySide6-based user interface
   for editing effects parameters on the Roland JD-Xi synthesizer. It extends `SynthEditor` and
   allows users to modify various effects settings, including Effect 1, Effect 2, Delay, and Reverb.

   Classes:
       - EffectsEditor: A QWidget subclass for managing and editing JD-Xi effect parameters.

   Dependencies:
       - os
       - logging
       - PySide6.QtWidgets (QWidget, QVBoxLayout, etc.)
       - PySide6.QtCore (Qt)
       - PySide6.QtGui (QPixmap)
       - jdxi_manager modules for MIDI and parameter handling

   Features:
       - Displays effects parameters with interactive controls.
       - Supports updating instrument images dynamically.
       - Sends MIDI messages to update effect settings in real-time.
       - Organizes effect parameters into categorized tabs.

                                   AddressParameterEffect1.EFX1_PARAM_17,
                                   AddressParameterEffect1.EFX1_PARAM_18,
                                   AddressParameterEffect1.EFX1_PARAM_19,
                                   AddressParameterEffect1.EFX1_PARAM_20,
                                   AddressParameterEffect1.EFX1_PARAM_21,
                                   AddressParameterEffect1.EFX1_PARAM_22,
                                   AddressParameterEffect1.EFX1_PARAM_23,
                                   AddressParameterEffect1.EFX1_PARAM_24,
                                   AddressParameterEffect1.EFX1_PARAM_25,
                                   AddressParameterEffect1.EFX1_PARAM_26,
                                   AddressParameterEffect1.EFX1_PARAM_27,
                                   AddressParameterEffect1.EFX1_PARAM_28,
                                   AddressParameterEffect1.EFX1_PARAM_29,
                                   AddressParameterEffect1.EFX1_PARAM_30,
                                   AddressParameterEffect1.EFX1_PARAM_31,

                                   AddressParameterEffect1.EFX2_PARAM_17,
                                   AddressParameterEffect1.EFX2_PARAM_18,
                                   AddressParameterEffect1.EFX2_PARAM_19,
                                   AddressParameterEffect1.EFX2_PARAM_20,
                                   AddressParameterEffect1.EFX2_PARAM_21,
                                   AddressParameterEffect1.EFX2_PARAM_22,
                                   AddressParameterEffect1.EFX2_PARAM_23,
                                   AddressParameterEffect1.EFX2_PARAM_24,
                                   AddressParameterEffect1.EFX2_PARAM_25,
                                   AddressParameterEffect1.EFX2_PARAM_26,
                                   AddressParameterEffect1.EFX2_PARAM_27,
                                   AddressParameterEffect1.EFX2_PARAM_28,
                                   AddressParameterEffect1.EFX2_PARAM_29,
                                   AddressParameterEffect1.EFX2_PARAM_30,
                                   AddressParameterEffect1.EFX2_PARAM_31,



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.effects.common.EffectsCommonEditor


Module Contents
---------------

.. py:class:: EffectsCommonEditor(midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper, preset_helper: jdxi_editor.jdxi.preset.helper.JDXiPresetHelper = None, parent=None)

   Bases: :py:obj:`jdxi_editor.ui.editors.synth.simple.BasicEditor`


   Effects Editor Window


   .. py:attribute:: tab_widget
      :value: None



   .. py:attribute:: midi_helper


   .. py:attribute:: preset_helper
      :value: None



   .. py:attribute:: EFX1_PARAMETERS


   .. py:attribute:: EFX2_PARAMETERS


   .. py:attribute:: efx1_param_labels


   .. py:attribute:: efx2_param_labels


   .. py:attribute:: midi_requests
      :value: ['F0 41 10 00 00 00 0E 12 18 00 02 00 01 7F 32 32 01 00 40 00 40 00 40 00 40 00 00 00 00 08 00...



   .. py:attribute:: delay_params
      :value: None



   .. py:attribute:: efx2_additional_params


   .. py:attribute:: default_image
      :value: 'effects.png'



   .. py:attribute:: instrument_icon_folder
      :value: 'effects'



   .. py:attribute:: title_label


   .. py:attribute:: image_label


   .. py:attribute:: controls
      :type:  Dict[Union[jdxi_editor.midi.data.parameter.effects.effects.AddressParameterReverb, jdxi_editor.midi.data.parameter.effects.common.AddressParameterEffectCommon, jdxi_editor.midi.data.parameter.effects.effects.AddressParameterEffect1, jdxi_editor.midi.data.parameter.effects.effects.AddressParameterEffect2], PySide6.QtWidgets.QWidget]


   .. py:attribute:: tabs


   .. py:attribute:: address


   .. py:attribute:: sysex_composer


   .. py:method:: update_flanger_rate_note_controls() -> None

      Update Flanger rate/note controls based on rate note switch.



   .. py:method:: update_phaser_rate_note_controls() -> None

      Update Flanger rate/note controls based on rate note switch.



   .. py:method:: _update_efx1_labels(effect_type: int)

      Update Effect 1 parameter labels based on selected effect type.

      :param effect_type: int
      :return:



   .. py:method:: _update_efx2_labels(effect_type: int)

      Update Effect 2 parameter labels based on selected effect type.

      :param effect_type: int



   .. py:method:: _create_effect1_section()

      Create Effect 1 section



   .. py:method:: _create_effect2_section()

      Create Effect 2 section



   .. py:method:: _create_delay_tab()

      Create Delay tab with parameters



   .. py:method:: _create_reverb_section()

      Create Reverb section



   .. py:method:: _on_parameter_changed(param: jdxi_editor.midi.data.parameter.synth.AddressParameter, value: int, address: jdxi_editor.midi.data.address.address.RolandSysExAddress = None)

      Handle parameter value changes from UI controls.



   .. py:method:: send_midi_parameter(param: jdxi_editor.midi.data.parameter.synth.AddressParameter, value: int) -> bool

      Send MIDI parameter with error handling

      :param param: AddressParameter
      :param value: int value
      :return: bool True on success, False otherwise



