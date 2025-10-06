jdxi_editor.midi.data.programs.analog
=====================================

.. py:module:: jdxi_editor.midi.data.programs.analog

.. autoapi-nested-parse::

   Analog presets



Attributes
----------

.. autoapisummary::

   jdxi_editor.midi.data.programs.analog.ANALOG_PRESET_LIST


Functions
---------

.. autoapisummary::

   jdxi_editor.midi.data.programs.analog.get_preset_by_program_number
   jdxi_editor.midi.data.programs.analog.get_preset_parameters


Module Contents
---------------

.. py:data:: ANALOG_PRESET_LIST

.. py:function:: get_preset_by_program_number(program_number: int) -> dict[str]

   get_preset_by_program_number

   :param program_number: int Program number
   :return: Program details


.. py:function:: get_preset_parameters(program_number: int) -> tuple[float, float, float]

   get_preset_parameters

   :param program_number: int
   :return:


