jdxi_editor.midi.sysex.request.factory
======================================

.. py:module:: jdxi_editor.midi.sysex.request.factory

.. autoapi-nested-parse::

   This module contains constants, functions, and logic to generate and compute
   Roland JD-Xi SysEx messages for requesting program and tone names.

   It defines a set of SysEx constants specific to the JD-Xi and provides the
   following functionality:

   1. **Constants**: A dictionary `SYSEX_CONSTANTS` containing key constants
      required to construct the SysEx messages, including the JD-Xi header,
      tone areas, and other necessary fields.
   2. **Checksum Calculation**: A function `roland_checksum` that computes the
      Roland checksum for a given SysEx data string. This checksum is used
      to ensure the integrity of the message.
   3. **Request Generation**: A function `create_request` that dynamically generates
      a SysEx message based on the header, tone area, and parameters provided.
   4. **Program and Tone Requests**: A list `PROGRAM_AND_TONE_NAME_REQUESTS`
      containing pre-generated SysEx requests for various program and tone areas
      like digital, analog, and drums.

   SysEx message format includes:
   - Start byte `F0`, end byte `F7`
   - JD-Xi specific header and command information
   - Roland checksum for data integrity

   Functions:
   - `roland_checksum(data: str) -> str`: Computes and returns the Roland checksum
     based on the input SysEx data string.
   - `create_request(header, tone_area, param1) -> str`: Constructs a complete
     SysEx request message, appends the checksum, and returns the full message.

       Examples
       --------
       To generate a request for the program common area:

       >>> request = create_request(
       ...     TEMPORARY_PROGRAM_RQ11_HEADER,
       ...     SYSEX_CONSTANTS['PROGRAM_COMMON_AREA'],
       ...     "00 00 00 00 00 40"
       )

       To retrieve a list of all program and tone name requests:
       all_requests = PROGRAM_AND_TONE_NAME_REQUESTS



Functions
---------

.. autoapisummary::

   jdxi_editor.midi.sysex.request.factory.roland_checksum
   jdxi_editor.midi.sysex.request.factory.create_request


Module Contents
---------------

.. py:function:: roland_checksum(data: str) -> str

   Compute Roland checksum for a given SysEx data string (space-separated hex).


.. py:function:: create_request(header: str, temp_area: Union[str, jdxi_editor.midi.sysex.request.hex.JDXISysExHex], part: str) -> str

   Create a SysEx request string using header, area, parameter, and Roland checksum.


