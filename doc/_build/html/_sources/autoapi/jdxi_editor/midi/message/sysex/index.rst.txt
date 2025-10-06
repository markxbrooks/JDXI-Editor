jdxi_editor.midi.message.sysex
==============================

.. py:module:: jdxi_editor.midi.message.sysex

.. autoapi-nested-parse::

   Roland JD-Xi System Exclusive (SysEx) Message Module
   ====================================================

   This module provides functionality for constructing, parsing, and handling
   Roland JD-Xi SysEx messages. It includes support for both writing (DT1) and
   reading (RQ1) parameter data, ensuring compliance with Roland's SysEx format.

   Features:
   ---------
   - Constructs valid SysEx messages for Roland JD-Xi.
   - Supports both parameter write (DT1) and read (RQ1) operations.
   - Computes and verifies Roland SysEx checksums.
   - Allows dynamic configuration of MIDI parameters.
   - Provides utilities to convert between byte sequences and structured data.

   Classes:
   --------
   - `RolandSysEx`: Base class for handling Roland SysEx messages.
   - `SysExParameter`: Enum for predefined SysEx parameters and command mappings.
   - `SysExMessage`: Helper class for constructing and sending SysEx messages.

   Usage Example:
   --------------
   ```python
   message = SysExMessage(area=0x19, synth_type=0x01, part=0x00, group=0x00, parameter=0x10, value=0x7F)
   sysex_bytes = message.construct_sysex()
   print(sysex_bytes)  # Outputs a valid SysEx message as a byte sequence
   [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x19, 0x01, 0x00, 0x00, 0x10, 0x7F, 0x57, 0xF7]



Attributes
----------

.. autoapisummary::

   jdxi_editor.midi.message.sysex.JD_XI_HEADER_BYTES


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.message.sysex.SysexParameter
   jdxi_editor.midi.message.sysex.SysExMessage


Module Contents
---------------

.. py:data:: JD_XI_HEADER_BYTES

.. py:class:: SysexParameter

   Bases: :py:obj:`enum.Enum`


   SysEx Parameters for Roland JD-Xi


   .. py:attribute:: DT1_COMMAND_12


   .. py:attribute:: RQ1_COMMAND_11


   .. py:attribute:: PROGRAM_COMMON


   .. py:method:: get_command_name(command_type)
      :classmethod:


      Retrieve the command name given a command type.



.. py:class:: SysExMessage

   Bases: :py:obj:`jdxi_editor.midi.message.midi.MidiMessage`


   Base class for MIDI System Exclusive (SysEx) messages.


   .. py:attribute:: start_of_sysex
      :type:  int
      :value: 240



   .. py:attribute:: manufacturer_id
      :type:  int


   .. py:attribute:: device_id
      :type:  int


   .. py:attribute:: model_id
      :type:  list[int]
      :value: None



   .. py:attribute:: command
      :type:  int


   .. py:attribute:: address
      :type:  list[int]
      :value: None



   .. py:attribute:: data
      :type:  list[int]
      :value: None



   .. py:attribute:: end_of_sysex
      :type:  int
      :value: 247



   .. py:method:: __post_init__()

      Ensure proper initialization of address, model_id, and data fields.



   .. py:method:: calculate_checksum() -> int

      Calculate Roland checksum: (128 - sum(bytes) & 0x7F).



   .. py:method:: to_message_list() -> List[int]

      Convert the SysEx message to a list of integers.



   .. py:method:: from_bytes(data: bytes)
      :classmethod:


      Parse a received SysEx message into an instance.



