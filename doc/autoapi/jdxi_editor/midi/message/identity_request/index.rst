jdxi_editor.midi.message.identity_request
=========================================

.. py:module:: jdxi_editor.midi.message.identity_request

.. autoapi-nested-parse::

   MIDI Identity Request Message Module

   This module defines the `IdentityRequestMessage` class, which represents a MIDI Identity Request message.
   MIDI Identity Request messages are used to query a device for its identity, typically to retrieve information such as its model or manufacturer.

   Classes:
       - IdentityRequestMessage: Represents a MIDI Identity Request message used to query a device's identity.

   Features:
       - Inherits from the base `Message` class, utilizing SysEx message structure.
       - Includes device identification information, such as device ID and fixed SysEx parameters.
       - Provides a method for converting the message into a list of bytes for sending via MIDI.

   Constants Used:
       - START_OF_SYSEX: The start byte for a SysEx message.
       - ID_NUMBER, DEVICE, SUB_ID_1, SUB_ID_2: Fixed SysEx identifiers for the identity request.
       - END_OF_SYSEX: The end byte for a SysEx message.

   Usage Example:
       >>> identity_msg = IdentityRequestMessage()
       >>> identity_msg.to_message_list()
       [0xF0, 0x7E, 0x00, 0x01, 0x02, 0xF7]



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.message.identity_request.IdentityRequestMessage


Module Contents
---------------

.. py:class:: IdentityRequestMessage

   Bases: :py:obj:`jdxi_editor.midi.message.midi.MidiMessage`


   MIDI Identity Request message


   .. py:attribute:: device_id
      :type:  int
      :value: 16



   .. py:method:: to_message_list() -> List[int]

      Convert to list of bytes for sending

      :return: list



