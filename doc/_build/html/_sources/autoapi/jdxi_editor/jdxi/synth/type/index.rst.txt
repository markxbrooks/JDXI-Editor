jdxi_editor.jdxi.synth.type
===========================

.. py:module:: jdxi_editor.jdxi.synth.type

.. autoapi-nested-parse::

   Module: synth_type

   This module defines the `SynthType` class, which categorizes JD-Xi synths
   and provides MIDI area codes for different synth sections.

   Classes:
       - SynthType: Defines synth categories and their corresponding MIDI area codes.

   .. method:: - get_area_code(synth_type)

      Returns the MIDI area code for a given synth type.
      



Classes
-------

.. autoapisummary::

   jdxi_editor.jdxi.synth.type.JDXiSynth


Module Contents
---------------

.. py:class:: JDXiSynth

   Synth types and their MIDI area codes


   .. py:attribute:: PROGRAM
      :value: 'PROGRAM'



   .. py:attribute:: ANALOG_SYNTH
      :value: 'ANALOG_SYNTH'



   .. py:attribute:: DIGITAL_SYNTH_1
      :value: 'DIGITAL_SYNTH_1'



   .. py:attribute:: DIGITAL_SYNTH_2
      :value: 'DIGITAL_SYNTH_2'



   .. py:attribute:: DIGITAL_SYNTH_3
      :value: 'DIGITAL_SYNTH_3'



   .. py:attribute:: DRUM_KIT
      :value: 'DRUM_KIT'



   .. py:attribute:: VOCAL_FX
      :value: 'VOCAL_FX'



   .. py:method:: get_area_code(synth_type: str) -> int
      :staticmethod:


      Get MIDI area code for preset preset_type



   .. py:method:: midi_channel_number(synth_type: str) -> int
      :staticmethod:


      Get MIDI area code for preset preset_type



