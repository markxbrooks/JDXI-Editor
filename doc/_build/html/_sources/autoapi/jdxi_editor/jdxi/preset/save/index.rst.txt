jdxi_editor.jdxi.preset.save
============================

.. py:module:: jdxi_editor.jdxi.preset.save


Functions
---------

.. autoapisummary::

   jdxi_editor.jdxi.preset.save.load_programs
   jdxi_editor.jdxi.preset.save.save_programs
   jdxi_editor.jdxi.preset.save.add_program_and_save


Module Contents
---------------

.. py:function:: load_programs() -> List[Dict[str, str]]

.. py:function:: save_programs(program_list: List[Dict[str, str]]) -> None

   Save the program list to USER_PROGRAMS_FILE, creating the file and directory if needed.

   :param program_list: List of program dictionaries.


.. py:function:: add_program_and_save(new_program: Dict[str, str]) -> bool

   add_program_and_save

   :param new_program:
   :return:


