jdxi_editor.midi.utils.conversions
==================================

.. py:module:: jdxi_editor.midi.utils.conversions

.. autoapi-nested-parse::

   MIDI CC Conversion Utilities

   This module provides utility functions for converting between MIDI values
   and various numerical representations such as milliseconds and fractional values.

   These functions are useful for mapping MIDI messages to meaningful time or intensity values
   in a synthesizer or effect unit.
   from jdxi_editor.jdxi.midi.constant import MidiConstant



Functions
---------

.. autoapisummary::

   jdxi_editor.midi.utils.conversions.midi_value_to_ms
   jdxi_editor.midi.utils.conversions.ms_to_midi_value
   jdxi_editor.midi.utils.conversions.fraction_to_midi_value
   jdxi_editor.midi.utils.conversions.midi_value_to_fraction


Module Contents
---------------

.. py:function:: midi_value_to_ms(midi_value: int, min_time: int = 10, max_time: int = 1000) -> float

   Converts a MIDI value (0–127) to a time value in milliseconds.

   :param midi_value: int MIDI CC value (0–127).
   :param min_time: int, optional: Minimum time in milliseconds. Default is 10 ms.
   :param max_time: int, optional: Maximum time in milliseconds. Default is 1000 ms.
   :returns: int Corresponding time value in milliseconds.


.. py:function:: ms_to_midi_value(ms_time: float, min_time: int = 10, max_time: int = 1000) -> int

   Converts address time value in milliseconds to address MIDI byte range value (0-127)

   :param ms_time: float: Time value in milliseconds.
   :param min_time: int, optional: Minimum time in milliseconds. Default is 10 ms.
   :param max_time: int, optional: Maximum time in milliseconds. Default is 1000 ms.
   :return: int Corresponding MIDI value (1-127)


.. py:function:: fraction_to_midi_value(fractional_value: float, minimum: float = 0.0, maximum: float = 1.0) -> int

   Converts address fractional value (0.0-1.0) to address MIDI CC value (0-127).

   :param fractional_value: float Fractional value between min and max.
   :param minimum: float optional Minimum possible fractional value. Default is 0.
   :param maximum: float optional Maximum possible fractional value. Default is 1.
   :returns: int: Corresponding MIDI value.


.. py:function:: midi_value_to_fraction(midi_value: int, minimum: float = 0.0, maximum: float = 1.0) -> float

   Converts address MIDI value (0-127) to address fractional value (0.0-1.0).

   :param midi_value: int: MIDI CC value (0-127).
   :param minimum: float, optional Minimum possible fractional value. Default is 0.
   :param maximum: float, optional Maximum possible fractional value. Default is 1.
   :returns: float Corresponding fractional value.


