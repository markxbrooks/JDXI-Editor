jdxi_editor.midi.data.programs.t
================================

.. py:module:: jdxi_editor.midi.data.programs.t


Attributes
----------

.. autoapisummary::

   jdxi_editor.midi.data.programs.t.log


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.programs.t.JDXiProgramManager


Module Contents
---------------

.. py:data:: log

.. py:class:: JDXiProgramManager

   .. py:attribute:: USER_PROGRAMS_FILE
      :value: None



   .. py:attribute:: ROM_PROGRAMS
      :value: []



   .. py:method:: setup()
      :classmethod:



   .. py:method:: _load_programs() -> List
      :classmethod:



   .. py:property:: PROGRAM_LIST
      :type: List



   .. py:method:: add_program(program: JDXiProgram) -> None
      :classmethod:



   .. py:method:: save_to_file(filepath: Optional[str] = None) -> None
      :classmethod:



   .. py:method:: load_from_file(filepath: Optional[str] = None, append: bool = True) -> None
      :classmethod:



