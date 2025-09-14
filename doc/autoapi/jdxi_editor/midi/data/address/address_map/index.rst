jdxi_editor.midi.data.address.address_map
=========================================

.. py:module:: jdxi_editor.midi.data.address.address_map

.. autoapi-nested-parse::

   5. Parameter Address Map
   ========================

   **Transmission of “#” marked address is divided to some packets. For
   example, ABH in hexadecimal notation will be divided to 0AH and
   0BH, and is sent/received in this order.
   **“<*>” marked address

   For reference:
   JD-Xi (ModelID = 00H 00H 00H 0EH)
   +------------------------------------------------------------------------------+
   | Start       |                                                                |
   | Address     |               Description                                      |
   |-------------+----------------------------------------------------------------|
   | 01 00 00 00 | Setup                                                          |
   |-------------+----------------------------------------------------------------|
   | 02 00 00 00 | System                                                         |
   |-------------+----------------------------------------------------------------|
   | 18 00 00 00 | Temporary Program                                              |
   | 19 00 00 00 | Temporary Tone (Digital Synth Part 1)                          |
   | 19 20 00 00 | Temporary Tone (Digital Synth Part 2)                          |
   | 19 40 00 00 | Temporary Tone (Analog Synth Part)                             |
   | 19 60 00 00 | Temporary Tone (Drums Part)                                    |
   +------------------------------------------------------------------------------+
   **System
   +------------------------------------------------------------------------------+
   | Offset      |                                                                |
   | Offset      |                                                                |
   |-------------+----------------------------------------------------------------|
   |    00 00 00 | System Common                                                  |
   |    00 03 00 | System Controller                                              |
   +------------------------------------------------------------------------------+
   **Temporary Tone
   +------------------------------------------------------------------------------+
   | Offset      |                                                                |
   | Address     | Description                                                    |
   |-------------+----------------------------------------------------------------|
   |    01 00 00 | Temporary SuperNATURAL Synth Tone                              |
   |    02 00 00 | Temporary Analog Synth Tone                                    |
   |    10 00 00 | Temporary Drum Kit                                             |
   +------------------------------------------------------------------------------+
   **Program
   +------------------------------------------------------------------------------+
   | Offset      |                                                                |
   | Address     | Description                                                    |
   |-------------+----------------------------------------------------------------|
   |    00 00 00 | Program Common                                                 |
   |    00 01 00 | Program Vocal Effect                                           |
   |    00 02 00 | Program Effect 1                                               |
   |    00 04 00 | Program Effect 2                                               |
   |    00 06 00 | Program Delay                                                  |
   |    00 08 00 | Program Reverb                                                 |
   |    00 20 00 | Program Part (Digital Synth Part 1)                            |
   |    00 21 00 | Program Part (Digital Synth Part 2)                            |
   |    00 22 00 | Program Part (Analog Synth Part)                               |
   |    00 23 00 | Program Part (Drums Part)                                      |
   |    00 30 00 | Program Zone (Digital Synth Part 1)                            |
   |    00 31 00 | Program Zone (Digital Synth Part 2)                            |
   |    00 32 00 | Program Zone (Analog Synth Part)                               |
   |    00 33 00 | Program Zone (Drums Part)                                      |
   |    00 40 00 | Program Controller                                             |
   +------------------------------------------------------------------------------+
   **SuperNATURAL Synth Tone
   +------------------------------------------------------------------------------+
   | Offset      |                                                                |
   | Address     | Description                                                    |
   |-------------+----------------------------------------------------------------|
   |    00 00 00 | SuperNATURAL Synth Tone Common                                 |
   |    00 20 00 | SuperNATURAL Synth Tone Partial (1)                            |
   |    00 21 00 | SuperNATURAL Synth Tone Partial (2)                            |
   |    00 22 00 | SuperNATURAL Synth Tone Partial (3)                            |
   |    00 50 00 | SuperNATURAL Synth Tone Modify                                 |
   +------------------------------------------------------------------------------+
   **Analog Synth Tone
   +------------------------------------------------------------------------------+
   | Offset      |                                                                |
   | Address     | Description                                                    |
   |-------------+----------------------------------------------------------------|
   |    00 00 00 | Analog Synth Tone                                              |
   +------------------------------------------------------------------------------+
   **Drum Kit
   +------------------------------------------------------------------------------+
   | Offset      |                                                                |
   | Address     | Description                                                    |
   |-------------+----------------------------------------------------------------|
   |    00 00 00 | Drum Kit Common                                                |
   |    00 2E 00 | Drum Kit Partial (Key # 36)                                    |
   |    00 30 00 | Drum Kit Partial (Key # 37)                                    |
   |        :    |                                                                |
   |    00 76 00 | Drum Kit Partial (Key # 72)                                    |
   +------------------------------------------------------------------------------+



Attributes
----------

.. autoapisummary::

   jdxi_editor.midi.data.address.address_map.PARAMETER_ADDRESS_MAP


Module Contents
---------------

.. py:data:: PARAMETER_ADDRESS_MAP

