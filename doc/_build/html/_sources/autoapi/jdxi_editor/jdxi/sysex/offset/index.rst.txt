jdxi_editor.jdxi.sysex.offset
=============================

.. py:module:: jdxi_editor.jdxi.sysex.offset

.. autoapi-nested-parse::

   JD-Xi SysEx Offsets
   ==================
   This module defines the offsets for various JD-Xi SysEx messages, including control change,
   program change, pitch bend, and identity messages. Each offset is represented as an `IntEnum`
   to provide a clear and structured way to access the byte positions within the SysEx messages.



Classes
-------

.. autoapisummary::

   jdxi_editor.jdxi.sysex.offset.JDXIControlChangeOffset
   jdxi_editor.jdxi.sysex.offset.JDXIProgramChangeOffset
   jdxi_editor.jdxi.sysex.offset.JDXIPitchBendOffset
   jdxi_editor.jdxi.sysex.offset.JDXiSysExOffset
   jdxi_editor.jdxi.sysex.offset.JDXIIdentityOffset


Module Contents
---------------

.. py:class:: JDXIControlChangeOffset

   Bases: :py:obj:`enum.IntEnum`


   JDXIControlChangeOffset
   Represents the offsets for JD-Xi Control Change messages.
   Byte   |    Description
   --------------------------------------------------------
   Status |    0xB0 to 0xBF — Control Change on MIDI channels 1–16
   Data 1 |    Control Number (0–127)
   Data 2 |    Control Value (0–127)


   .. py:attribute:: STATUS_BYTE
      :value: 0



   .. py:attribute:: CONTROL
      :value: 1



   .. py:attribute:: VALUE
      :value: 2



   .. py:attribute:: END
      :value: -1



.. py:class:: JDXIProgramChangeOffset

   Bases: :py:obj:`enum.IntEnum`


   JDXIProgramChangeOffset
   Represents the offsets for JD-Xi Program Change messages.

   Byte   |    Description
   --------------------------------------------------------
   Status |    0xC0 to 0xCF — Program Change on MIDI channels 1–16
   Data 1 |    Program Number (0–127)


   .. py:attribute:: STATUS_BYTE
      :value: 0



   .. py:attribute:: PROGRAM_NUMBER
      :value: 1



   .. py:attribute:: END
      :value: -1



.. py:class:: JDXIPitchBendOffset

   Bases: :py:obj:`enum.IntEnum`


   JDXIPitchBendOffset
   Represents the offsets for JD-Xi Pitch Bend messages.

   Byte   |    Description
   --------------------------------------------------------
   Status |    0xE0 to 0xEF — Pitch Bend on MIDI channels 1–16
   Data 1 |    Pitch Bend Value (14-bit, split into two bytes)


   .. py:attribute:: STATUS_BYTE
      :value: 0



   .. py:attribute:: PITCH_BEND_VALUE
      :value: 1



   .. py:attribute:: END
      :value: -1



.. py:class:: JDXiSysExOffset

   Bases: :py:obj:`enum.IntEnum`


   JDXiSysExOffset

   Represents the offsets for JD-Xi SysEx messages.
   Byte        |       Description
   --------------------------------------------------------
   SYSEX_START |       Start of SysEx message (0xF0)
   ROLAND_ID   |       Roland ID (0x41)
   DEVICE_ID   |       Device ID (0x10)
   MODEL_ID_1  |       First byte of Model ID (0x00)
   MODEL_ID_2  |       Second byte of Model ID (0x0E)
   MODEL_ID_3  |       Third byte of Model ID (0x00)
   MODEL_ID_4  |       Fourth byte of Model ID (0x00)
   COMMAND_ID  |       Command ID (0x00 for Identity Request, 0x01 for Identity Reply)
   ADDRESS_MSB |       Most Significant Byte of Address
   ADDRESS_UMB |       Upper Middle Byte of Address
   ADDRESS_LMB |       Lower Middle Byte of Address
   ADDRESS_LSB |       Least Significant Byte of Address
   TONE_NAME_START |   Start of Tone Name (12 bytes)
   TONE_NAME_END |     End of Tone Name (24 bytes)
   VALUE |     Value (3 bytes, varies by command)
   CHECKSUM |  Checksum byte (calculated from the message)
   SYSEX_END | End of SysEx message (0xF7)



   .. py:attribute:: SYSEX_START
      :value: 0



   .. py:attribute:: ROLAND_ID
      :value: 1



   .. py:attribute:: DEVICE_ID
      :value: 2



   .. py:attribute:: MODEL_ID_1
      :value: 3



   .. py:attribute:: MODEL_ID_2
      :value: 4



   .. py:attribute:: MODEL_ID_3
      :value: 5



   .. py:attribute:: MODEL_ID_4
      :value: 6



   .. py:attribute:: COMMAND_ID
      :value: 7



   .. py:attribute:: ADDRESS_MSB
      :value: 8



   .. py:attribute:: ADDRESS_UMB
      :value: 9



   .. py:attribute:: ADDRESS_LMB
      :value: 10



   .. py:attribute:: ADDRESS_LSB
      :value: 11



   .. py:attribute:: TONE_NAME_START
      :value: 12



   .. py:attribute:: TONE_NAME_END
      :value: 24



   .. py:attribute:: VALUE
      :value: -3



   .. py:attribute:: CHECKSUM
      :value: -2



   .. py:attribute:: SYSEX_END
      :value: -1



.. py:class:: JDXIIdentityOffset

   Bases: :py:obj:`enum.IntEnum`


   JDXIIdentityOffset
   Represents the offsets for JD-Xi Identity SysEx messages.
   Pos | Byte        | Description
   --------------------------------------------------------
   0 | SYSEX_START |   Start of SysEx message (0xF0)
   1 | ID_NUMBER   |   ID Number (0x7E for non-realtime, 0x7F for realtime)
   2 | DEVICE_ID   |   Device ID (0x7F for all devices)
   3 | SUB_ID_1    |   Sub ID 1 (0x06 for General Information)
   4 | SUB_ID_2    |   Sub ID 2 (0x01 for Identity Request, 0x02 for Identity Reply)
   5 | ROLAND_ID   |   Roland Manufacturer ID (0x41, 0x10, 0x00)
   6-9 | DEVICE_ID_1-4 |       Device ID (0x0E for JD-Xi)
   10-13 | REVISION_1-4 |      Revision bytes x 4
   14 | SYSEX_END   |  End of SysEx message (0xF7)


   .. py:attribute:: SYSEX_START
      :value: 0



   .. py:attribute:: ID_NUMBER
      :value: 1



   .. py:attribute:: DEVICE_ID
      :value: 2



   .. py:attribute:: SUB_ID_1_GENERAL_INFORMATION
      :value: 3



   .. py:attribute:: SUB_ID_2_IDENTITY_REPLY
      :value: 4



   .. py:attribute:: ROLAND_ID
      :value: 5



   .. py:attribute:: DEVICE_FAMILY_CODE_1
      :value: 6



   .. py:attribute:: DEVICE_FAMILY_CODE_2
      :value: 7



   .. py:attribute:: DEVICE_FAMILY_NUMBER_CODE_1
      :value: 8



   .. py:attribute:: DEVICE_FAMILY_NUMBER_CODE_2
      :value: 9



   .. py:attribute:: SOFTWARE_REVISION_1
      :value: 10



   .. py:attribute:: SOFTWARE_REVISION_2
      :value: 11



   .. py:attribute:: SOFTWARE_REVISION_3
      :value: 12



   .. py:attribute:: SOFTWARE_REVISION_4
      :value: 13



   .. py:attribute:: SYSEX_END
      :value: -1



   .. py:attribute:: __len__
      :value: 14



   .. py:method:: expected_length()
      :classmethod:



