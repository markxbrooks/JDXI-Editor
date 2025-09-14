jdxi_editor.midi.channel.channel
================================

.. py:module:: jdxi_editor.midi.channel.channel

.. autoapi-nested-parse::

   This module defines an enumeration for MIDI channels used in a synthesizer, specifically for a Roland JD-Xi-style instrument editor.

   The `MidiChannel` class extends `IntEnum` and provides symbolic names for the common MIDI channels, including:
   - DIGITAL1 (channel 1)
   - DIGITAL2 (channel 2)
   - ANALOG (channel 3)
   - DRUM (channel 10)
   - PROGRAM (channel 16)

   The class also provides utility methods for handling MIDI channels, including:
   - `__str__`: Returns a string representation of the channel.
   - `midi_channel_number`: A property that returns the actual MIDI channel number (1-based).
   - `from_midi_channel`: A class method that retrieves a `MidiChannel` from a given MIDI channel number.

   Usage example:
       channel = MidiChannel.DIGITAL1
       print(str(channel))  # Output: "Digital 1 (Ch.1)"
       print(channel.midi_channel_number)  # Output: 1
       print(MidiChannel.from_midi_channel(9))  # Output: MidiChannel.DRUM_KIT



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.channel.channel.MidiChannel


Module Contents
---------------

.. py:class:: MidiChannel

   Bases: :py:obj:`enum.IntEnum`


   MIDI Channel Enum


   .. py:attribute:: DIGITAL_SYNTH_1
      :value: 0



   .. py:attribute:: DIGITAL_SYNTH_2
      :value: 1



   .. py:attribute:: ANALOG_SYNTH
      :value: 2



   .. py:attribute:: DRUM_KIT
      :value: 9



   .. py:attribute:: PROGRAM
      :value: 15



   .. py:attribute:: VOCAL_FX
      :value: 6



   .. py:method:: __str__()

      Return str(self).



   .. py:property:: midi_channel_number
      :type: int



   .. py:method:: from_midi_channel(channel: int)
      :classmethod:



