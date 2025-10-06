jdxi_editor.midi.data.arpeggio.arpeggio
=======================================

.. py:module:: jdxi_editor.midi.data.arpeggio.arpeggio

.. autoapi-nested-parse::

   Arpeggiator Configuration Module

   This module defines the settings, data structures, and parameter ranges for an arpeggiator.
   It provides enumerations, default values, and data classes to represent various arpeggiator
   configurations, including grid timing, note duration, motif patterns, and styles.

   ### Contents:
   - **Arpeggio Settings**:
     - `arp_grid`: Available grid timing values (e.g., 1/4, 1/8, etc.).
     - `arp_duration`: Note duration options as percentages.
     - `arp_motif`: Various motif patterns for the arpeggiator.
     - `arp_style`: A collection of predefined arpeggiator styles.

   - **Arpeggio Parameter Ranges and Defaults**:
     - `Arpeggio`: Defines valid parameter ranges and default values.
     - `ArpeggioPatch`: A dataclass representing a complete arpeggio configuration.

   - **Enumerations**:
     - `ArpeggioGrid`: Grid timing options.
     - `ArpeggioDuration`: Possible note durations.
     - `ArpeggioMotif`: Arpeggiator motif patterns.
     - `ArpeggioParameters`: Parameter identifiers used in arpeggiator control.

   ### Usage:
   This module can be used to configure an arpeggiator in a MIDI editor or synthesizer
   application. The `ArpeggioPatch` class allows structured representation and validation of
   arpeggiator settings, ensuring proper configuration.



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.arpeggio.arpeggio.ArpeggioPatch
   jdxi_editor.midi.data.arpeggio.arpeggio.ArpeggioMotif
   jdxi_editor.midi.data.arpeggio.arpeggio.ArpeggioGrid
   jdxi_editor.midi.data.arpeggio.arpeggio.ArpeggioDuration
   jdxi_editor.midi.data.arpeggio.arpeggio.ArpeggioOctaveRange
   jdxi_editor.midi.data.arpeggio.arpeggio.ArpeggioSwitch


Module Contents
---------------

.. py:class:: ArpeggioPatch

   Complete arpeggiator patch data


   .. py:attribute:: switch
      :type:  bool
      :value: False



   .. py:attribute:: style
      :type:  int
      :value: 0



   .. py:attribute:: octave
      :type:  int
      :value: 0



   .. py:attribute:: grid
      :type:  int
      :value: 1



   .. py:attribute:: duration
      :type:  int
      :value: 50



   .. py:attribute:: motif
      :type:  int
      :value: 0



   .. py:attribute:: key
      :type:  int
      :value: 0



   .. py:attribute:: patterns
      :type:  List[int]
      :value: None



   .. py:attribute:: rhythms
      :type:  List[int]
      :value: None



   .. py:attribute:: notes
      :type:  List[int]
      :value: None



   .. py:method:: __post_init__()

      Initialize pattern data



.. py:class:: ArpeggioMotif

   Bases: :py:obj:`enum.Enum`


   Arpeggio motif values


   .. py:attribute:: UP_L
      :value: 0



   .. py:attribute:: UP_H
      :value: 1



   .. py:attribute:: UP_NORM
      :value: 2



   .. py:attribute:: DOWN_L
      :value: 3



   .. py:attribute:: DOWN_H
      :value: 4



   .. py:attribute:: DOWN_NORM
      :value: 5



   .. py:attribute:: UP_DOWN_L
      :value: 6



   .. py:attribute:: UP_DOWN_H
      :value: 7



   .. py:attribute:: UP_DOWN_NORM
      :value: 8



   .. py:attribute:: RANDOM_L
      :value: 9



   .. py:attribute:: RANDOM_NORM
      :value: 10



   .. py:attribute:: PHRASE
      :value: 11



   .. py:property:: display_name
      :type: str


      Get display name for grid value


   .. py:property:: midi_value
      :type: int


      Get MIDI value for grid


.. py:class:: ArpeggioGrid

   Bases: :py:obj:`enum.Enum`


   Arpeggiator grid values


   .. py:attribute:: QUARTER
      :value: 0



   .. py:attribute:: EIGHTH
      :value: 1



   .. py:attribute:: EIGHTH_T
      :value: 2



   .. py:attribute:: SIXTEENTH
      :value: 3



   .. py:attribute:: SIXTEENTH_T
      :value: 4



   .. py:attribute:: THIRTY_TWO
      :value: 5



   .. py:attribute:: THIRTY_TWO_T
      :value: 6



   .. py:property:: display_name
      :type: str


      Get display name for grid value


   .. py:property:: midi_value
      :type: int


      Get MIDI value for grid


.. py:class:: ArpeggioDuration

   Bases: :py:obj:`enum.Enum`


   Arpeggiator duration values


   .. py:attribute:: D30
      :value: 0



   .. py:attribute:: D40
      :value: 1



   .. py:attribute:: D50
      :value: 2



   .. py:attribute:: D60
      :value: 3



   .. py:attribute:: D70
      :value: 4



   .. py:attribute:: D80
      :value: 5



   .. py:attribute:: D90
      :value: 6



   .. py:attribute:: D100
      :value: 7



   .. py:attribute:: D120
      :value: 8



   .. py:attribute:: FUL
      :value: 9



   .. py:property:: display_name
      :type: str


      Get display name for duration value


   .. py:property:: midi_value
      :type: int


      Get MIDI value for duration


.. py:class:: ArpeggioOctaveRange

   Bases: :py:obj:`enum.Enum`


   Arpeggio octave range values


   .. py:attribute:: OCT_MINUS_3
      :value: -3



   .. py:attribute:: OCT_MINUS_2
      :value: -2



   .. py:attribute:: OCT_MINUS_1
      :value: -1



   .. py:attribute:: OCT_ZERO
      :value: 0



   .. py:attribute:: OCT_PLUS_1
      :value: 1



   .. py:attribute:: OCT_PLUS_2
      :value: 2



   .. py:attribute:: OCT_PLUS_3
      :value: 3



   .. py:property:: display_name
      :type: str


      Get display name for octave range


   .. py:property:: midi_value
      :type: int


      Get MIDI value for octave range (centered at 64)


.. py:class:: ArpeggioSwitch

   Bases: :py:obj:`enum.Enum`


   Arpeggiator switch values


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


