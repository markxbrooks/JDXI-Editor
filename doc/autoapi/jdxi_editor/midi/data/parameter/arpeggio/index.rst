jdxi_editor.midi.data.parameter.arpeggio
========================================

.. py:module:: jdxi_editor.midi.data.parameter.arpeggio

.. autoapi-nested-parse::

   Module: ArpeggioParameter
   =========================

   This module defines the ArpeggioParameter class, which represents arpeggiator-related parameters
   in a synthesizer. These parameters control various aspects of arpeggios, such as grid, duration,
   style, motif, octave range, accent rate, and velocity, as well as pattern, rhythm, and note settings.

   The class provides methods to:

   - Initialize arpeggio parameters with a given address, range, and optional display range.
   - Store the minimum and maximum values for display and parameter validation.
   - Define a variety of arpeggio and pattern-related parameters with specific ranges, including:
     - Arpeggio grid (e.g., 4_, 8_, 16_)
     - Arpeggio duration (e.g., 30, 40, 50, 60)
     - Arpeggio style and motif
     - Arpeggio octave range (-3 to +3)
     - Accent rate and velocity
     - Arpeggio pattern, rhythm, and note settings

   Parameters include:
   - Arpeggio grid, duration, switch, style, motif, octave range, accent rate, and velocity.
   - Pattern parameters (4 patterns, each with a range from 0 to 127).
   - Rhythm parameters (4 rhythm settings, each with a range from 0 to 127).
   - Note parameters (4 note settings, each with a range from 0 to 127).

   ```python
   Usage example:
       # Initialize an arpeggio parameter object
       param = ArpeggioParameter(address=0x01, min_val=0, max_val=8)

       # Access display range values
       log.message(param.display_min)  # Output: 0
       log.message(param.display_max)  # Output: 8

       # Validate a value for the parameter
       valid_value = param.validate_value(5)



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.parameter.arpeggio.AddressParameterArpeggio


Module Contents
---------------

.. py:class:: AddressParameterArpeggio(address: int, min_val: int, max_val: int, display_min: Optional[int] = None, display_max: Optional[int] = None, tooltip: Optional[str] = '')

   Bases: :py:obj:`jdxi_editor.midi.data.parameter.synth.AddressParameter`


   Arpeggiator parameters with address and range


   .. py:attribute:: display_min
      :value: None



   .. py:attribute:: display_max
      :value: None



   .. py:attribute:: tooltip
      :value: ''



   .. py:attribute:: ARPEGGIO_GRID


   .. py:attribute:: ARPEGGIO_DURATION


   .. py:attribute:: ARPEGGIO_SWITCH
      :value: (3, 0, 1, 0, 1, 'Arpeggio ON/OFF')



   .. py:attribute:: ARPEGGIO_STYLE


   .. py:attribute:: ARPEGGIO_MOTIF


   .. py:attribute:: ARPEGGIO_OCTAVE_RANGE


   .. py:attribute:: ARPEGGIO_ACCENT_RATE


   .. py:attribute:: ARPEGGIO_VELOCITY


   .. py:attribute:: PATTERN_1
      :value: (16, 0, 127)



   .. py:attribute:: PATTERN_2
      :value: (17, 0, 127)



   .. py:attribute:: PATTERN_3
      :value: (18, 0, 127)



   .. py:attribute:: PATTERN_4
      :value: (19, 0, 127)



   .. py:attribute:: RHYTHM_1
      :value: (32, 0, 127)



   .. py:attribute:: RHYTHM_2
      :value: (33, 0, 127)



   .. py:attribute:: RHYTHM_3
      :value: (34, 0, 127)



   .. py:attribute:: RHYTHM_4
      :value: (35, 0, 127)



   .. py:attribute:: NOTE_1
      :value: (48, 0, 127)



   .. py:attribute:: NOTE_2
      :value: (49, 0, 127)



   .. py:attribute:: NOTE_3
      :value: (50, 0, 127)



   .. py:attribute:: NOTE_4
      :value: (51, 0, 127)



   .. py:method:: get_address_for_partial(partial_number: int = 0)

      Get the address for the partial number.

      :param partial_number: int
      :return: int default area to be subclassed



