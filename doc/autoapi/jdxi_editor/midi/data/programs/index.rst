jdxi_editor.midi.data.programs
==============================

.. py:module:: jdxi_editor.midi.data.programs


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/jdxi_editor/midi/data/programs/analog/index
   /autoapi/jdxi_editor/midi/data/programs/digital/index
   /autoapi/jdxi_editor/midi/data/programs/drum/index
   /autoapi/jdxi_editor/midi/data/programs/programs/index
   /autoapi/jdxi_editor/midi/data/programs/t/index


Attributes
----------

.. autoapisummary::

   jdxi_editor.midi.data.programs.all


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.programs.JDXiProgramList


Package Contents
----------------

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



.. py:data:: all

