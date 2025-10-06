jdxi_editor.midi.data.address.jdxi_addresses
============================================

.. py:module:: jdxi_editor.midi.data.address.jdxi_addresses

.. autoapi-nested-parse::

   sysex utils:
   # Get full address for Temporary Drum Kit (Offset from TEMP_TONE_BASE)
   base = JDXiMemoryAddress.TEMP_TONE_BASE
   drum_offset = (0x10, 0x00, 0x00)
   drum_address = base.offset(drum_offset)

   # Build a DT1 message to write data to it
   data = [0x01, 0x02, 0x03]
   sysex_msg = JDxiSysExBuilder.build_dt1(drum_address, data)



Attributes
----------

.. autoapisummary::

   jdxi_editor.midi.data.address.jdxi_addresses.SYSTEM_OFFSETS
   jdxi_editor.midi.data.address.jdxi_addresses.TEMP_TONE_OFFSETS
   jdxi_editor.midi.data.address.jdxi_addresses.PROGRAM_OFFSETS


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.address.jdxi_addresses.JDXiAddress
   jdxi_editor.midi.data.address.jdxi_addresses.JDxiSysExBuilder


Module Contents
---------------

.. py:class:: JDXiAddress

   Bases: :py:obj:`enum.Enum`


   Base Addresses (4-byte addresses)


   .. py:attribute:: SETUP
      :value: (1, 0, 0, 0)



   .. py:attribute:: SYSTEM
      :value: (2, 0, 0, 0)



   .. py:attribute:: TEMP_PROGRAM
      :value: (24, 0, 0, 0)



   .. py:attribute:: TEMP_TONE_BASE
      :value: (25, 0, 0, 0)



   .. py:attribute:: TEMP_TONE_PART1
      :value: (25, 0, 0, 0)



   .. py:attribute:: TEMP_TONE_PART2
      :value: (25, 32, 0, 0)



   .. py:attribute:: TEMP_TONE_ANALOG
      :value: (25, 64, 0, 0)



   .. py:attribute:: TEMP_TONE_DRUMS
      :value: (25, 96, 0, 0)



   .. py:attribute:: PROGRAM
      :value: (24, 0, 0, 0)



   .. py:method:: offset(offset: Tuple[int, int, int]) -> Tuple[int, int, int, int]


.. py:data:: SYSTEM_OFFSETS

.. py:data:: TEMP_TONE_OFFSETS

.. py:data:: PROGRAM_OFFSETS

.. py:class:: JDxiSysExBuilder

   JDxiSysExBuilder


   .. py:attribute:: MODEL_ID
      :value: [0, 0, 0, 14]



   .. py:method:: build_dt1(address: Tuple[int, int, int, int], data: List[int]) -> List[int]
      :staticmethod:



