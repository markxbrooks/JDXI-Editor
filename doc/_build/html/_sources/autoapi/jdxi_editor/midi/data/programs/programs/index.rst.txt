jdxi_editor.midi.data.programs.programs
=======================================

.. py:module:: jdxi_editor.midi.data.programs.programs


Attributes
----------

.. autoapisummary::

   jdxi_editor.midi.data.programs.programs.ROM_PROGRAMS


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.programs.programs.JDXiProgramList


Module Contents
---------------

.. py:data:: ROM_PROGRAMS

.. py:class:: JDXiProgramList

   JDXiProgramList

   Convert each dict to a JDXiProgram instance


   .. py:attribute:: ROM_PROGRAM_LIST


   .. py:attribute:: json_folder


   .. py:attribute:: USER_PROGRAMS_FILE
      :value: ''



   .. py:attribute:: USER_PROGRAMS
      :value: []



   .. py:method:: list_rom_and_user_programs() -> List[jdxi_editor.jdxi.program.program.JDXiProgram]
      :classmethod:


      list_rom_and_user_programs

      :return: List[JDXiProgram]



   .. py:method:: _load_user_programs() -> List[jdxi_editor.jdxi.program.program.JDXiProgram]
      :classmethod:


      _load_user_programs

      :return: List[JDXiProgram]



   .. py:method:: save_to_file(filepath: Optional[str] = None) -> None
      :classmethod:


      save_to_file

      :param filepath: str
      :return: None



   .. py:method:: reload_from_file(filepath: Optional[str] = None, append: bool = True) -> None
      :classmethod:


      reload_from_file
      :return:
      :param filepath:
      :param append:
      :return:



   .. py:method:: get_from_user_file(filepath: Optional[str] = None) -> list[jdxi_editor.jdxi.program.program.JDXiProgram]
      :classmethod:



