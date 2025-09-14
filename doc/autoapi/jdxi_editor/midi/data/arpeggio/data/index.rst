jdxi_editor.midi.data.arpeggio.data
===================================

.. py:module:: jdxi_editor.midi.data.arpeggio.data


Attributes
----------

.. autoapisummary::

   jdxi_editor.midi.data.arpeggio.data.ARPEGGIO_GRID
   jdxi_editor.midi.data.arpeggio.data.ARP_DURATION
   jdxi_editor.midi.data.arpeggio.data.ARPEGGIO_MOTIF
   jdxi_editor.midi.data.arpeggio.data.ARPEGGIO_MOTIF_NAME_LIST
   jdxi_editor.midi.data.arpeggio.data.ARPEGGIO_STYLE
   jdxi_editor.midi.data.arpeggio.data.PATTERNS
   jdxi_editor.midi.data.arpeggio.data.DURATIONS
   jdxi_editor.midi.data.arpeggio.data.OCTAVE_RANGES


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.arpeggio.data.ArpeggioStyle


Module Contents
---------------

.. py:data:: ARPEGGIO_GRID
   :value: ['1/4', '1/8', '1/8 L', '1/8 H', '1/12', '1/16', '1/16 L', '1/16 H', '1/24']


.. py:data:: ARP_DURATION
   :value: ['30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%', '120%', 'Full']


.. py:data:: ARPEGGIO_MOTIF
   :value: ['Up  (L)', 'Up  (L&H)', 'Up  (_)', 'Down  (L)', 'Down  (L&H)', 'Down  (_)', 'Up/Down  (L)',...


.. py:data:: ARPEGGIO_MOTIF_NAME_LIST
   :value: ['UP/L', 'UP/H', 'UP/_', 'dn/L', 'dn/H', 'dn/_', 'Ud/L', 'Ud/H', 'Ud/_', 'rn/L', 'rn/_', 'PHRASE']


.. py:data:: ARPEGGIO_STYLE
   :value: ['001: Basic 1', '002: Basic 2', '003: Basic 3', '004: Basic 4', '005: Basic 5', '006: Basic 6',...


.. py:class:: ArpeggioStyle

   Bases: :py:obj:`enum.Enum`


   Generic enumeration.

   Derive from this class to define new enumerations.


   .. py:attribute:: BASIC_1
      :value: 0



   .. py:attribute:: names


   .. py:property:: display_name
      :type: str


      Get display name for grid value


   .. py:property:: midi_value
      :type: int


      Get MIDI value for grid


.. py:data:: PATTERNS
   :value: ['UP', 'DOWN', 'UP/DOWN', 'RANDOM', 'NOTE ORDER', 'CHORD', 'USER']


.. py:data:: DURATIONS
   :value: ['1/4', '1/8', '1/8 Triplet', '1/16', '1/16 Triplet', '1/32', '1/32 Triplet']


.. py:data:: OCTAVE_RANGES

