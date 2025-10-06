jdxi_editor.midi.data.parameter.program.controller
==================================================

.. py:module:: jdxi_editor.midi.data.parameter.program.controller

.. autoapi-nested-parse::

   Module for controlling arpeggio parameters in a synthesizer or sequencer.

   This module defines the `ProgramController` class, which manages various arpeggio-related
   parameters, including grid, duration, switch state, style, motif, octave range, accent rate,
   and velocity. These parameters are used to configure and control the behavior of arpeggios in
   a music production environment.

   The class provides static methods to retrieve human-readable display values for each parameter
   based on raw numerical values. It also includes predefined constants for each arpeggio-related
   parameter, with specific value ranges and corresponding meanings.

   Parameters defined in the class include:
   - Arpeggio grid, duration, switch, style, motif, octave, accent, and velocity values
   - Methods for converting raw integer values to display-friendly strings
   - Various grid types (e.g., 04_, 08_, 16_)
   - Duration values expressed as percentages (e.g., 30%, 50%, 100%)
   - Motif values representing arpeggio patterns and phrases (e.g., UP/L, dn/H, PHRASE)

   This module can be used in a synthesizer, sequencer, or other digital audio workstation
   to dynamically configure arpeggio settings and translate raw parameter values into readable
   formats for display and interaction with users.

   Classes:
   - ProgramController: Contains the logic for handling arpeggio parameters and converting
     raw values to human-readable strings.



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.parameter.program.controller.AddressParameterProgramController


Module Contents
---------------

.. py:class:: AddressParameterProgramController(address: int, min_val: int, max_val: int)

   Bases: :py:obj:`jdxi_editor.midi.data.parameter.synth.AddressParameter`


   Program Controller parameters


   .. py:attribute:: ARPEGGIO_GRID
      :value: (1, 0, 8)



   .. py:attribute:: ARPEGGIO_DURATION
      :value: (2, 0, 9)



   .. py:attribute:: ARPEGGIO_SWITCH
      :value: (3, 0, 1)



   .. py:attribute:: ARPEGGIO_STYLE
      :value: (5, 0, 127)



   .. py:attribute:: ARPEGGIO_MOTIF
      :value: (6, 0, 11)



   .. py:attribute:: ARPEGGIO_OCTAVE_RANGE


   .. py:attribute:: ARPEGGIO_ACCENT_RATE
      :value: (9, 0, 100)



   .. py:attribute:: ARPEGGIO_VELOCITY
      :value: (10, 0, 127)


      # Grid values
      GRID_4 = 0  # 04_
      GRID_8 = 1  # 08_
      GRID_8L = 2  # 08L
      GRID_8H = 3  # 08H
      GRID_8T = 4  # 08t
      GRID_16 = 5  # 16_
      GRID_16L = 6  # 16L
      GRID_16H = 7  # 16H
      GRID_16T = 8  # 16t

      # Duration values
      DUR_30 = 0  # 30%
      DUR_40 = 1  # 40%
      DUR_50 = 2  # 50%
      DUR_60 = 3  # 60%
      DUR_70 = 4  # 70%
      DUR_80 = 5  # 80%
      DUR_90 = 6  # 90%
      DUR_100 = 7  # 100%
      DUR_120 = 8  # 120%
      DUR_FULL = 9  # FULL

      # Motif values
      MOTIF_UP_L = 0  # UP/L
      MOTIF_UP_H = 1  # UP/H
      MOTIF_UP = 2  # UP/_
      MOTIF_DN_L = 3  # dn/L
      MOTIF_DN_H = 4  # dn/H
      MOTIF_DN = 5  # dn/_
      MOTIF_UD_L = 6  # Ud/L
      MOTIF_UD_H = 7  # Ud/H
      MOTIF_UD = 8  # Ud/_
      MOTIF_RN_L = 9  # rn/L
      MOTIF_RN = 10  # rn/_
      MOTIF_PHRASE = 11  # PHRASE


   .. py:method:: get_grid_name(value: int) -> str
      :staticmethod:


      Get grid name from value

      :param value: int The value
      :return: str The grid name



   .. py:method:: get_duration_name(value: int) -> str
      :staticmethod:


      Get duration name from value

      :param value: int The value
      :return: str The duration name



   .. py:method:: get_motif_name(value: int) -> str
      :staticmethod:


      Get motif name from value

      :param value: int The value
      :return: str The motif name



   .. py:method:: get_display_value(param: int, value: int) -> str
      :staticmethod:


      Convert raw value to display value

      :param param: int The parameter
      :param value: int The value
      :return: str The display value



