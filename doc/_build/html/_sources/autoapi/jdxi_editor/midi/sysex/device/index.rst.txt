jdxi_editor.midi.sysex.device
=============================

.. py:module:: jdxi_editor.midi.sysex.device

.. autoapi-nested-parse::

   JD-Xi Device Information Module

   This module defines the `DeviceInfo` class, which represents identity information
   for a Roland JD-Xi synthesizer. It provides utilities for checking manufacturer
   and model identity, extracting firmware version, and constructing an instance
   from a MIDI Identity Reply message.

   Usage Example:
   --------------
   >>> from device_info import DeviceInfo
   >>> identity_data = bytes([0xF0, 0x7E, 0x10, 0x06, 0x02, 0x41, 0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x01, 0x00, 0x00, 0xF7])
   >>> device = DeviceInfo.from_identity_reply(identity_data)
   >>> if device:
   >>>     print(f"Device: JD-Xi, Version: {device.version_string}")

   Expected Output:
   ----------------
   Device: JD-Xi, Version: v1.00

   Classes:
   --------
   - DeviceInfo: Represents JD-Xi device information, including manufacturer, model,
     and firmware version. Provides utility properties for checking if the device
     is a JD-Xi and formatting the version string.

   Methods:
   --------
   - `from_identity_reply(data: bytes) -> Optional[DeviceInfo]`
       Parses a MIDI Identity Reply message to create a `DeviceInfo` instance.
   - `is_roland -> bool`
       Returns `True` if the device manufacturer is Roland.
   - `is_jdxi -> bool`
       Returns `True` if the device is identified as a JD-Xi.
   - `version_string -> str`
       Returns the firmware version as a formatted string.

   Dependencies:
   -------------
   - dataclasses
   - typing (List, Optional)



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.sysex.device.DeviceInfo


Module Contents
---------------

.. py:class:: DeviceInfo

   JD-Xi device information parser from MIDI Identity Reply.


   .. py:attribute:: device_id
      :type:  int


   .. py:attribute:: manufacturer
      :type:  List[int]


   .. py:attribute:: family
      :type:  List[int]


   .. py:attribute:: model
      :type:  List[int]


   .. py:attribute:: version
      :type:  List[int]


   .. py:property:: is_roland
      :type: bool


      Check if the device is from Roland.


   .. py:property:: is_jdxi
      :type: bool


      Check if the device is a JD-Xi.


   .. py:property:: version_string
      :type: str


      Format the version number as a string (e.g., 'v1.03').


   .. py:property:: to_string
      :type: str


      Generate a readable string describing the device.


   .. py:method:: from_identity_reply(data: bytes) -> Optional[DeviceInfo]
      :classmethod:


      Parse an Identity Reply SysEx message into a DeviceInfo object.

      :param data: bytes
      :return: DeviceInfo



