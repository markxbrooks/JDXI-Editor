jdxi_editor.midi.data.address.sysex
===================================

.. py:module:: jdxi_editor.midi.data.address.sysex

.. autoapi-nested-parse::

   Collected SysEx constants



Attributes
----------

.. autoapisummary::

   jdxi_editor.midi.data.address.sysex.START_OF_SYSEX
   jdxi_editor.midi.data.address.sysex.END_OF_SYSEX
   jdxi_editor.midi.data.address.sysex.ID_NUMBER
   jdxi_editor.midi.data.address.sysex.DEVICE_ID
   jdxi_editor.midi.data.address.sysex.SUB_ID_1_GENERAL_INFORMATION
   jdxi_editor.midi.data.address.sysex.SUB_ID_2_IDENTITY_REQUEST
   jdxi_editor.midi.data.address.sysex.SUB_ID_2_IDENTITY_REPLY
   jdxi_editor.midi.data.address.sysex.ZERO_BYTE
   jdxi_editor.midi.data.address.sysex.VALUE_ON
   jdxi_editor.midi.data.address.sysex.VALUE_OFF
   jdxi_editor.midi.data.address.sysex.NOTE_ON
   jdxi_editor.midi.data.address.sysex.NOTE_OFF
   jdxi_editor.midi.data.address.sysex.LOW_1_BIT_MASK
   jdxi_editor.midi.data.address.sysex.LOW_2_BITS_MASK
   jdxi_editor.midi.data.address.sysex.LOW_4_BITS_MASK
   jdxi_editor.midi.data.address.sysex.LOW_7_BITS_MASK
   jdxi_editor.midi.data.address.sysex.FULL_BYTE_MASK
   jdxi_editor.midi.data.address.sysex.HIGH_4_BITS_MASK
   jdxi_editor.midi.data.address.sysex.WORD_MASK
   jdxi_editor.midi.data.address.sysex.MAX_EIGHT_BIT_VALUE


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.address.sysex.RolandID
   jdxi_editor.midi.data.address.sysex.ResponseID


Module Contents
---------------

.. py:data:: START_OF_SYSEX
   :value: 240


.. py:data:: END_OF_SYSEX
   :value: 247


.. py:data:: ID_NUMBER
   :value: 126


.. py:data:: DEVICE_ID
   :value: 127


.. py:data:: SUB_ID_1_GENERAL_INFORMATION
   :value: 6


.. py:data:: SUB_ID_2_IDENTITY_REQUEST
   :value: 1


.. py:data:: SUB_ID_2_IDENTITY_REPLY
   :value: 2


.. py:data:: ZERO_BYTE
   :value: 0


.. py:data:: VALUE_ON
   :value: 1


.. py:data:: VALUE_OFF
   :value: 0


.. py:data:: NOTE_ON
   :value: 144


.. py:data:: NOTE_OFF
   :value: 128


.. py:data:: LOW_1_BIT_MASK
   :value: 1


.. py:data:: LOW_2_BITS_MASK
   :value: 3


.. py:data:: LOW_4_BITS_MASK
   :value: 15


.. py:data:: LOW_7_BITS_MASK
   :value: 127


.. py:data:: FULL_BYTE_MASK
   :value: 255


.. py:data:: HIGH_4_BITS_MASK
   :value: 240


.. py:data:: WORD_MASK
   :value: 65535


.. py:data:: MAX_EIGHT_BIT_VALUE
   :value: 255


.. py:class:: RolandID

   Bases: :py:obj:`enum.IntEnum`


   Roland IDs


   .. py:attribute:: ROLAND_ID
      :value: 65



   .. py:attribute:: DEVICE_ID
      :value: 16



.. py:class:: ResponseID

   Bases: :py:obj:`enum.IntEnum`


   Midi responses


   .. py:attribute:: ACK
      :value: 79



   .. py:attribute:: ERR
      :value: 78



