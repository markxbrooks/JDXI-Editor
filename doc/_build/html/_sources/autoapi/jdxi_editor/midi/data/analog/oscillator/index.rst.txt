jdxi_editor.midi.data.analog.oscillator
=======================================

.. py:module:: jdxi_editor.midi.data.analog.oscillator


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.analog.oscillator.AnalogOscWave
   jdxi_editor.midi.data.analog.oscillator.AnalogSubOscType


Module Contents
---------------

.. py:class:: AnalogOscWave

   Bases: :py:obj:`enum.Enum`


   Analog oscillator waveform types


   .. py:attribute:: SAW
      :value: 0



   .. py:attribute:: TRIANGLE
      :value: 1



   .. py:attribute:: PULSE
      :value: 2



   .. py:property:: display_name
      :type: str


      Get display name for waveform


   .. py:property:: midi_value
      :type: int


      Get MIDI value for waveform


.. py:class:: AnalogSubOscType

   Bases: :py:obj:`enum.Enum`


   Analog sub oscillator types


   .. py:attribute:: OFF
      :value: 0



   .. py:attribute:: OCT_DOWN_1
      :value: 1



   .. py:attribute:: OCT_DOWN_2
      :value: 2



   .. py:property:: display_name
      :type: str


      Get display name for sub oscillator preset_type


   .. py:property:: midi_value
      :type: int


      Get MIDI value for sub oscillator preset_type


