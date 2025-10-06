jdxi_editor.midi.data.vocal_effects.vocal
=========================================

.. py:module:: jdxi_editor.midi.data.vocal_effects.vocal

.. autoapi-nested-parse::

   Vocal Effects



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.vocal_effects.vocal.VocalFxSwitch
   jdxi_editor.midi.data.vocal_effects.vocal.VocalAutoNoteSwitch
   jdxi_editor.midi.data.vocal_effects.vocal.VocalAutoPitchType
   jdxi_editor.midi.data.vocal_effects.vocal.VocalOutputAssign
   jdxi_editor.midi.data.vocal_effects.vocal.VocalAutoPitchKey
   jdxi_editor.midi.data.vocal_effects.vocal.VocalOctaveRange
   jdxi_editor.midi.data.vocal_effects.vocal.VocalAutoPitchNote
   jdxi_editor.midi.data.vocal_effects.vocal.VocoderEnvelope
   jdxi_editor.midi.data.vocal_effects.vocal.VocoderHPF
   jdxi_editor.midi.data.vocal_effects.vocal.VoiceCutoffFilter
   jdxi_editor.midi.data.vocal_effects.vocal.VoiceScale
   jdxi_editor.midi.data.vocal_effects.vocal.VoiceKey


Module Contents
---------------

.. py:class:: VocalFxSwitch

   Bases: :py:obj:`enum.Enum`


   Vocal FX switch values


   .. py:attribute:: OFF
      :value: 0



   .. py:attribute:: ON
      :value: 1



   .. py:property:: display_name
      :type: str


      Get display name for switch value


   .. py:property:: midi_value
      :type: int


      Get MIDI value for switch


.. py:class:: VocalAutoNoteSwitch

   Bases: :py:obj:`enum.Enum`


   Auto Note switch values


   .. py:attribute:: OFF
      :value: 0



   .. py:attribute:: ON
      :value: 1



   .. py:property:: display_name
      :type: str


      Get display name for switch value


   .. py:property:: midi_value
      :type: int


      Get MIDI value for switch


.. py:class:: VocalAutoPitchType

   Bases: :py:obj:`enum.Enum`


   Auto Pitch preset_type values


   .. py:attribute:: SOFT
      :value: 0



   .. py:attribute:: HARD
      :value: 1



   .. py:attribute:: ELECTRIC1
      :value: 2



   .. py:attribute:: ELECTRIC2
      :value: 3



   .. py:property:: display_name
      :type: str


      Get display name for pitch preset_type


   .. py:property:: midi_value
      :type: int


      Get MIDI value for pitch preset_type


.. py:class:: VocalOutputAssign

   Bases: :py:obj:`enum.Enum`


   Output assignment values


   .. py:attribute:: EFX1
      :value: 0



   .. py:attribute:: EFX2
      :value: 1



   .. py:attribute:: DLY
      :value: 2



   .. py:attribute:: REV
      :value: 3



   .. py:attribute:: DIR
      :value: 4



   .. py:property:: display_name
      :type: str


      Get display name for output assignment


   .. py:property:: midi_value
      :type: int


      Get MIDI value for output assignment


.. py:class:: VocalAutoPitchKey

   Bases: :py:obj:`enum.Enum`


   Auto Pitch key values


   .. py:attribute:: C
      :value: 0



   .. py:attribute:: Db
      :value: 1



   .. py:attribute:: D
      :value: 2



   .. py:attribute:: Eb
      :value: 3



   .. py:attribute:: E
      :value: 4



   .. py:attribute:: F
      :value: 5



   .. py:attribute:: Fsharp
      :value: 6



   .. py:attribute:: G
      :value: 7



   .. py:attribute:: Ab
      :value: 8



   .. py:attribute:: A
      :value: 9



   .. py:attribute:: Bb
      :value: 10



   .. py:attribute:: B
      :value: 11



   .. py:attribute:: Cm
      :value: 12



   .. py:attribute:: Csharp_m
      :value: 13



   .. py:attribute:: Dm
      :value: 14



   .. py:attribute:: Dsharp_m
      :value: 15



   .. py:attribute:: Em
      :value: 16



   .. py:attribute:: Fm
      :value: 17



   .. py:attribute:: Fsharp_m
      :value: 18



   .. py:attribute:: Gm
      :value: 19



   .. py:attribute:: Gsharp_m
      :value: 20



   .. py:attribute:: Am
      :value: 21



   .. py:attribute:: Bbm
      :value: 22



   .. py:attribute:: Bm
      :value: 23



   .. py:property:: display_name
      :type: str


      Get display name for key


   .. py:property:: midi_value
      :type: int


      Get MIDI value for key


.. py:class:: VocalOctaveRange

   Bases: :py:obj:`enum.Enum`


   Octave range values


   .. py:attribute:: MINUS_ONE
      :value: 0



   .. py:attribute:: ZERO
      :value: 1



   .. py:attribute:: PLUS_ONE
      :value: 2



   .. py:property:: display_name
      :type: str


      Get display name for octave


   .. py:property:: midi_value
      :type: int


      Get MIDI value for octave


.. py:class:: VocalAutoPitchNote

   Bases: :py:obj:`enum.Enum`


   Auto Pitch note values


   .. py:attribute:: C
      :value: 0



   .. py:attribute:: C_SHARP
      :value: 1



   .. py:attribute:: D
      :value: 2



   .. py:attribute:: D_SHARP
      :value: 3



   .. py:attribute:: E
      :value: 4



   .. py:attribute:: F
      :value: 5



   .. py:attribute:: F_SHARP
      :value: 6



   .. py:attribute:: G
      :value: 7



   .. py:attribute:: G_SHARP
      :value: 8



   .. py:attribute:: A
      :value: 9



   .. py:attribute:: A_SHARP
      :value: 10



   .. py:attribute:: B
      :value: 11



   .. py:property:: display_name
      :type: str


      Get display name for note


   .. py:property:: midi_value
      :type: int


      Get MIDI value for note


.. py:class:: VocoderEnvelope

   Bases: :py:obj:`enum.Enum`


   Vocoder envelope types


   .. py:attribute:: SHARP
      :value: 0



   .. py:attribute:: SOFT
      :value: 1



   .. py:attribute:: LONG
      :value: 2



   .. py:property:: display_name
      :type: str


      Get display name for envelope preset_type


   .. py:property:: midi_value
      :type: int


      Get MIDI value for envelope preset_type


.. py:class:: VocoderHPF

   Bases: :py:obj:`enum.Enum`


   Vocoder HPF frequencies


   .. py:attribute:: BYPASS
      :value: 0



   .. py:attribute:: FREQ_1000
      :value: 1



   .. py:attribute:: FREQ_1250
      :value: 2



   .. py:attribute:: FREQ_1600
      :value: 3



   .. py:attribute:: FREQ_2000
      :value: 4



   .. py:attribute:: FREQ_2500
      :value: 5



   .. py:attribute:: FREQ_3150
      :value: 6



   .. py:attribute:: FREQ_4000
      :value: 7



   .. py:attribute:: FREQ_5000
      :value: 8



   .. py:attribute:: FREQ_6300
      :value: 9



   .. py:attribute:: FREQ_8000
      :value: 10



   .. py:attribute:: FREQ_10000
      :value: 11



   .. py:attribute:: FREQ_12500
      :value: 12



   .. py:attribute:: FREQ_16000
      :value: 13



   .. py:property:: display_name
      :type: str


      Get display name for HPF frequency


   .. py:property:: midi_value
      :type: int


      Get MIDI value for HPF frequency


.. py:class:: VoiceCutoffFilter

   Bases: :py:obj:`enum.Enum`


   Voice cutoff filter types


   .. py:attribute:: THRU
      :value: 0



   .. py:attribute:: LPF
      :value: 1



   .. py:attribute:: HPF
      :value: 2



   .. py:attribute:: BPF
      :value: 3



.. py:class:: VoiceScale

   Bases: :py:obj:`enum.Enum`


   Voice scale types


   .. py:attribute:: CHROMATIC
      :value: 0



   .. py:attribute:: MAJOR
      :value: 1



   .. py:attribute:: MINOR
      :value: 2



   .. py:attribute:: BLUES
      :value: 3



   .. py:attribute:: INDIAN
      :value: 4



.. py:class:: VoiceKey

   Bases: :py:obj:`enum.Enum`


   Voice keys


   .. py:attribute:: C
      :value: 0



   .. py:attribute:: Db
      :value: 1



   .. py:attribute:: D
      :value: 2



   .. py:attribute:: Eb
      :value: 3



   .. py:attribute:: E
      :value: 4



   .. py:attribute:: F
      :value: 5



   .. py:attribute:: Gb
      :value: 6



   .. py:attribute:: G
      :value: 7



   .. py:attribute:: Ab
      :value: 8



   .. py:attribute:: A
      :value: 9



   .. py:attribute:: Bb
      :value: 10



   .. py:attribute:: B
      :value: 11



