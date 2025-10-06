jdxi_editor.midi.data.programs.digital
======================================

.. py:module:: jdxi_editor.midi.data.programs.digital

.. autoapi-nested-parse::

   Digital preset list



Attributes
----------

.. autoapisummary::

   jdxi_editor.midi.data.programs.digital.DIGITAL_PRESET_LIST
   jdxi_editor.midi.data.programs.digital.RAW_PRESETS_CSV


Functions
---------

.. autoapisummary::

   jdxi_editor.midi.data.programs.digital.generate_preset_list
   jdxi_editor.midi.data.programs.digital.get_preset_by_program_number
   jdxi_editor.midi.data.programs.digital.get_preset_parameters


Module Contents
---------------

.. py:data:: DIGITAL_PRESET_LIST

.. py:data:: RAW_PRESETS_CSV
   :value: ''


.. py:function:: generate_preset_list()

   Generate a list of presets from RAW_PRESETS_CSV data.


.. py:function:: get_preset_by_program_number(program_number: str) -> Optional[dict]

   Get preset information by program number.
   :param program_number: str The program number (e.g., '090')
   :return: Optional[dict] The preset information containing msb, lsb, pc, and other details
   :return: None If preset not found


.. py:function:: get_preset_parameters(program_number: str) -> Optional[Tuple[int, int, int]]

   Get MSB, LSB, and PC values for a given program number.

   :param program_number: str The program number (e.g., '090')
   :return: Tuple[int, int, int] The MSB, LSB, and PC values as integers
   :return: Optional[Tuple[int, int, int]] The MSB, LSB, and PC values as integers
   :return: None If preset not found


