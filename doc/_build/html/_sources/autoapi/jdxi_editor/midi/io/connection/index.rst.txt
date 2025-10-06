jdxi_editor.midi.io.connection
==============================

.. py:module:: jdxi_editor.midi.io.connection

.. autoapi-nested-parse::

   MIDI Connection Singleton for JD-Xi

   This module defines the `MIDIConnection` class, which serves as a singleton for managing
   MIDI input and output connections with the Roland JD-Xi synthesizer. It provides methods
   for sending MIDI messages, setting input callbacks, and identifying connected devices.

   Features:
   - Implements a singleton pattern to ensure a single MIDI connection instance.
   - Manages MIDI input and output ports.
   - Sends MIDI messages with an optional UI indicator blink.
   - Sets a callback function for incoming MIDI messages.
   - Sends an Identity Request to detect and verify the connected device.
   - Retrieves firmware version information from the JD-Xi.

   Dependencies:
   - `rtmidi` for MIDI communication.
   - `logging` for debugging and error handling.
   - `DeviceInfo` and `IdentityRequest` for device identification.

   Example Usage:
       midi_conn = MIDIConnection()
       midi_conn.initialize(midi_in, midi_out, main_window)
       midi_conn.send_message([0x90, 0x40, 0x7F])  # Send a Note On message
       if midi_conn.identify_device():
           print("Connected to JD-Xi:", midi_conn.device_version)



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.io.connection.MIDIConnection


Module Contents
---------------

.. py:class:: MIDIConnection

   Midi connection object


   .. py:attribute:: _instance
      :value: None



   .. py:attribute:: _midi_in
      :value: None



   .. py:attribute:: _midi_out
      :value: None



   .. py:attribute:: _main_window
      :value: None



   .. py:attribute:: device_info
      :type:  Optional[jdxi_editor.midi.sysex.device.DeviceInfo]
      :value: None



   .. py:property:: midi_in

      Get MIDI input port


   .. py:property:: midi_out

      Get MIDI output port


   .. py:method:: initialize(midi_in: rtmidi.MidiIn, midi_out: rtmidi.MidiOut, main_window=Optional[QMainWindow]) -> None

      Initialize MIDI connection with input and output ports

      :param midi_in: rtmidi.MidiIn
      :param midi_out: rtmidi.MidiOut
      :param main_window: Optional[QMainWindow] for UI interaction
      :return: None



   .. py:method:: send_message(message: Iterable[int]) -> None

      Send MIDI message and trigger indicator

      :param message: Iterable[int], MIDI message to send
      :return: None



   .. py:method:: identify_device() -> None

      Send Identity Request and verify response



   .. py:property:: is_connected
      :type: bool


      Check if connected to JD-Xi


   .. py:property:: device_version
      :type: str


      Get device firmware version


