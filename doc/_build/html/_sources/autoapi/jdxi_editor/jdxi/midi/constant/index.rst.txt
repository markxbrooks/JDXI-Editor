jdxi_editor.jdxi.midi.constant
==============================

.. py:module:: jdxi_editor.jdxi.midi.constant

.. autoapi-nested-parse::

   Midi and JD-Xi Constant definitions



Classes
-------

.. autoapisummary::

   jdxi_editor.jdxi.midi.constant.MidiConstant
   jdxi_editor.jdxi.midi.constant.JDXiConstant


Module Contents
---------------

.. py:class:: MidiConstant

   Miscellaneous MIDI constants for JD-Xi communication.


   .. py:attribute:: MIDI_CHANNELS_NUMBER
      :value: 16



   .. py:attribute:: MIDI_NOTES_NUMBER
      :value: 128



   .. py:attribute:: CONTROL_CHANGE_BANK_SELECT_MSB
      :value: 85



   .. py:attribute:: CONTROL_CHANGE_BANK_SELECT_LSB_BANK_E_AND_F
      :value: 0



   .. py:attribute:: CONTROL_CHANGE_BANK_SELECT_LSB_BANK_G_AND_H
      :value: 1



   .. py:attribute:: CONTROL_CHANGE_BANK_SELECT_LSB_BANK_A_AND_B
      :value: 64



   .. py:attribute:: CONTROL_CHANGE_BANK_SELECT_LSB_BANK_C_AND_D
      :value: 65



   .. py:attribute:: PROGRAM_CHANGE_BANK_A_AND_C_AND_E_AND_G
      :value: 0



   .. py:attribute:: PROGRAM_CHANGE_BANK_B_AND_D_AND_F_AND_H
      :value: 64



   .. py:attribute:: TEMPO_DEFAULT_120_BPM
      :value: 120



   .. py:attribute:: TEMPO_CONVERT_SEC_TO_USEC
      :value: 1000000



   .. py:attribute:: TEMPO_100_BPM_USEC
      :value: 600000



   .. py:attribute:: TEMPO_120_BPM_USEC
      :value: 500000



   .. py:attribute:: TEMPO_150_BPM_USEC
      :value: 400000



   .. py:attribute:: TEMPO_162_BPM_USEC
      :value: 370370



   .. py:attribute:: CONTROL_CHANGE_NRPN_MSB
      :value: 99



   .. py:attribute:: CONTROL_CHANGE_NRPN_LSB
      :value: 98



   .. py:attribute:: SONG_STOP
      :value: 252



   .. py:attribute:: SONG_START
      :value: 250



   .. py:attribute:: START_OF_SYSEX
      :value: 240



   .. py:attribute:: END_OF_SYSEX
      :value: 247



   .. py:attribute:: ZERO_BYTE
      :value: 0



   .. py:attribute:: VALUE_ON
      :value: 1



   .. py:attribute:: VALUE_OFF
      :value: 0



   .. py:attribute:: VALUE_MAX_FOUR_BIT
      :value: 15



   .. py:attribute:: VALUE_MAX_SEVEN_BIT
      :value: 127



   .. py:attribute:: VALUE_MAX_EIGHT_BIT
      :value: 255



   .. py:attribute:: VALUE_MAX_FOURTEEN_BIT
      :value: 16383



   .. py:attribute:: VALUE_MAX_SIGNED_SIXTEEN_BIT
      :value: 32767



   .. py:attribute:: VALUE_MIN_SIGNED_SIXTEEN_BIT
      :value: 32768



   .. py:attribute:: VALUE_MAX_UNSIGNED_SIXTEEN_BIT
      :value: 65535



   .. py:attribute:: VALUE_MAX_THIRTY_TWO_BIT
      :value: 4294967295



   .. py:attribute:: NOTE_OFF
      :value: 128



   .. py:attribute:: NOTE_ON
      :value: 144



   .. py:attribute:: POLY_AFTERTOUCH
      :value: 160



   .. py:attribute:: CONTROL_CHANGE
      :value: 176



   .. py:attribute:: CONTROL_CHANGE_MAX
      :value: 191



   .. py:attribute:: PROGRAM_CHANGE
      :value: 192



   .. py:attribute:: PROGRAM_CHANGE_MAX
      :value: 207



   .. py:attribute:: CHANNEL_AFTERTOUCH
      :value: 208



   .. py:attribute:: PITCH_BEND
      :value: 224



   .. py:attribute:: BANK_SELECT_MSB
      :value: 0



   .. py:attribute:: BANK_SELECT_LSB
      :value: 32



   .. py:attribute:: MIDI_CHANNEL_MASK
      :value: 15



   .. py:attribute:: PITCH_BEND_RANGE
      :value: 16383



   .. py:attribute:: PITCH_BEND_CENTER
      :value: 8192



   .. py:attribute:: CHANNEL_BINARY_TO_DISPLAY
      :value: 1



   .. py:attribute:: CHANNEL_DISPLAY_TO_BINARY
      :value: -1



.. py:class:: JDXiConstant

   JD-Xi-specific MIDI and SysEx constants.


   .. py:attribute:: TIMER_INTERVAL
      :value: 10



   .. py:attribute:: FILTER_PLOT_DEPTH
      :value: 1.0



   .. py:attribute:: CHECKED
      :value: 2



   .. py:attribute:: CENTER_OCTAVE_VALUE
      :value: 64



   .. py:attribute:: ID_NUMBER
      :value: 126



   .. py:attribute:: DEVICE_ID
      :value: 127



   .. py:attribute:: SUB_ID_1_GENERAL_INFORMATION
      :value: 6



   .. py:attribute:: SUB_ID_2_IDENTITY_REQUEST
      :value: 1



   .. py:attribute:: SUB_ID_2_IDENTITY_REPLY
      :value: 2



   .. py:attribute:: SYSEX_LENGTH_ONE_BYTE_DATA
      :value: 15



   .. py:attribute:: SYSEX_LENGTH_FOUR_BYTE_DATA
      :value: 18



   .. py:attribute:: ROLAND_ID
      :value: [65, 16, 0]



   .. py:attribute:: JD_XI_MODEL_ID
      :value: 14



