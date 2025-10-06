jdxi_editor.midi.data.digital.oscillator
========================================

.. py:module:: jdxi_editor.midi.data.digital.oscillator

.. autoapi-nested-parse::

   Digital Oscillator



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.digital.oscillator.DigitalOscPcmWaveGain
   jdxi_editor.midi.data.digital.oscillator.DigitalOscWave
   jdxi_editor.midi.data.digital.oscillator.DigitalWaveform


Module Contents
---------------

.. py:class:: DigitalOscPcmWaveGain

   Bases: :py:obj:`enum.IntEnum`


   Wave gain values in dB


   .. py:attribute:: DB_MINUS_6
      :value: 0



   .. py:attribute:: DB_0
      :value: 1



   .. py:attribute:: DB_PLUS_6
      :value: 2



   .. py:attribute:: DB_PLUS_12
      :value: 3



.. py:class:: DigitalOscWave

   Bases: :py:obj:`enum.IntEnum`


   Oscillator waveform types


   .. py:attribute:: SAW
      :value: 0



   .. py:attribute:: SQUARE
      :value: 1



   .. py:attribute:: PW_SQUARE
      :value: 2



   .. py:attribute:: TRIANGLE
      :value: 3



   .. py:attribute:: SINE
      :value: 4



   .. py:attribute:: NOISE
      :value: 5



   .. py:attribute:: SUPER_SAW
      :value: 6



   .. py:attribute:: PCM
      :value: 7



   .. py:property:: display_name
      :type: str


      Get display name for the waveform


   .. py:property:: description
      :type: str


      Get full description of the waveform


.. py:class:: DigitalWaveform

   Bases: :py:obj:`enum.Enum`


   Waveform types available on the JD-Xi


   .. py:attribute:: SAW
      :value: 0



   .. py:attribute:: SQUARE
      :value: 1



   .. py:attribute:: PW_SQUARE
      :value: 2



   .. py:attribute:: TRIANGLE
      :value: 3



   .. py:attribute:: SINE
      :value: 4



   .. py:attribute:: NOISE
      :value: 5



   .. py:attribute:: SUPER_SAW
      :value: 6



   .. py:attribute:: PCM
      :value: 7



   .. py:property:: display_name
      :type: str


      Get display name for waveform


   .. py:property:: midi_value
      :type: int


      Get MIDI value for waveform


   .. py:method:: from_midi_value(value: int) -> jdxi_editor.midi.wave.form.Waveform
      :classmethod:


      Create Waveform from MIDI value



