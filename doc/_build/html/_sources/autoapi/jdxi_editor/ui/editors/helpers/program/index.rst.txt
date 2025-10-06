jdxi_editor.ui.editors.helpers.program
======================================

.. py:module:: jdxi_editor.ui.editors.helpers.program

.. autoapi-nested-parse::

   MIDI Program Management and Calculation Utilities

   This module provides utilities for retrieving and calculating
   information related to MIDI programs, including the ability to get program details by ID,
   calculate MSB (Most Significant Byte), LSB (Least Significant Byte),
   and Program Change (PC) values based on bank and program numbers,
    as well as logging useful program and MIDI data.

   Functions:
       - get_program_index_by_id(program_id: str) -> Optional[int]:
           Retrieves the index of a program by its ID from the `PROGRAM_LIST`.

       - get_program_by_id(program_id: str) -> Optional[Dict[str, str]]:
           Retrieves a program by its ID from the `PROGRAM_LIST`.

       - calculate_midi_values(bank: str, program_number: int) -> tuple:
           Calculates the MSB, LSB, and PC based on the given bank and program number.

       - calculate_index(bank: str, program_number: int) -> int:
           Calculates the program index based on the bank and program number.

       - log_midi_info(msb: int, lsb: int, pc: int):
           Logs the MSB, LSB, and PC values for MIDI operations.

       - log_program_info(program_name: str, program_id: Optional[str] = None, program_details: Optional[Dict] = None):
           Logs information about the loaded program.

       - get_msb_lsb_pc(program_number: int) -> tuple:
           Retrieves the MSB, LSB, and PC for a specific program number from the `PROGRAM_LIST`.

   Constants:
       - PROGRAM_LIST: A list of dictionaries containing MIDI program information used throughout the functions.

   Logging:
       This module uses Python's `logging` module to log key operations and errors, such as retrieving programs, calculating MIDI values,
       and verifying program values within valid ranges.

   Usage Example:
       >>> msb, lsb, pc = calculate_midi_values("A", 5)
       >>> log_midi_info(msb, lsb, pc)



Functions
---------

.. autoapisummary::

   jdxi_editor.ui.editors.helpers.program.get_program_index_by_id
   jdxi_editor.ui.editors.helpers.program.get_program_by_id
   jdxi_editor.ui.editors.helpers.program.get_program_by_bank_and_number
   jdxi_editor.ui.editors.helpers.program.get_program_id_by_name
   jdxi_editor.ui.editors.helpers.program.add_program
   jdxi_editor.ui.editors.helpers.program.load_programs
   jdxi_editor.ui.editors.helpers.program.save_programs
   jdxi_editor.ui.editors.helpers.program.get_program_number_by_name
   jdxi_editor.ui.editors.helpers.program.get_program_name_by_id
   jdxi_editor.ui.editors.helpers.program.get_program_parameter_value
   jdxi_editor.ui.editors.helpers.program.calculate_midi_values
   jdxi_editor.ui.editors.helpers.program.calculate_index
   jdxi_editor.ui.editors.helpers.program.get_msb_lsb_pc


Module Contents
---------------

.. py:function:: get_program_index_by_id(program_id: str) -> Optional[int]

   Retrieve the index of a program by its ID.

   :param program_id: str
   :return: int


.. py:function:: get_program_by_id(program_id: str) -> Optional[jdxi_editor.jdxi.program.program.JDXiProgram]

   Retrieve a program by its ID from PROGRAM_LIST

   :param program_id: str
   :return: Optional[JDXiProgram]


.. py:function:: get_program_by_bank_and_number(bank: str, program_number: int) -> Optional[jdxi_editor.jdxi.program.program.JDXiProgram]

   Retrieve a program by its bank letter and number

   :param bank: str
   :param program_number: int
   :return: Optional[JDXiProgram]


.. py:function:: get_program_id_by_name(name: str) -> Optional[str]

   get_program_id_by_name

   :param name: str
   :return: Optional[str]


.. py:function:: add_program(program_list: List[jdxi_editor.jdxi.program.program.JDXiProgram], new_program: jdxi_editor.jdxi.program.program.JDXiProgram) -> bool

   add_program

   :param program_list: List[JDXiProgram]
   :param new_program: JDXiProgram
   :return:


.. py:function:: load_programs() -> List[Dict[str, str]]

   load programs

   :return: list


.. py:function:: save_programs(program_list: List[Dict[str, str]]) -> None

   save_programs

   :param program_list: List[Dict[str, str]]
   :return: None


.. py:function:: get_program_number_by_name(program_name: str) -> Optional[int]

   Retrieve a program's number (without bank letter) by its name from JDXiProgramList.PROGRAM_LIST

   :param program_name: str
   :return: int


.. py:function:: get_program_name_by_id(program_id: str) -> Optional[str]

   Retrieve a program name by its ID from JDXiProgramList.PROGRAM_LIST

   :param program_id: int
   :return: str


.. py:function:: get_program_parameter_value(parameter: str, program_id: str) -> Optional[str]

   Retrieve a specific parameter value from a program by its ID

   :param parameter: str
   :param program_id: str
   :return:


.. py:function:: calculate_midi_values(bank: str, program_number: int) -> tuple[int, int, int]

   Calculate MSB, LSB, and PC based on bank and program number

   :param bank: str
   :param program_number: int
   :return: tuple[int, int, int] msb lsb pc


.. py:function:: calculate_index(bank: str, program_number: int) -> int

   Calculate the index based on bank and program number

   :param bank: str
   :param program_number:
   :return: int


.. py:function:: get_msb_lsb_pc(program_number: int) -> tuple[int, int, int]

   Get MSB, LSB, and PC values for a program at the given index.

   :param program_number: Index in the program list (0-based).
   :return: Tuple of (MSB, LSB, PC) values as integers.
   :raises IndexError: If the index is out of range.
   :raises ValueError: If any of the values can't be converted to int.


