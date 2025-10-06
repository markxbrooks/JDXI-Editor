jdxi_editor.midi.sysex.tokenizer
================================

.. py:module:: jdxi_editor.midi.sysex.tokenizer

.. autoapi-nested-parse::

   Tokeniser for lexing
   # Example input
   # input_data = "DIGITAL_SYNTH_1 COMMON"
   # mapping = generate_mapping(input_data)
   # print(mapping)



Attributes
----------

.. autoapisummary::

   jdxi_editor.midi.sysex.tokenizer.TOKEN_PATTERNS


Functions
---------

.. autoapisummary::

   jdxi_editor.midi.sysex.tokenizer.tokenize
   jdxi_editor.midi.sysex.tokenizer.generate_mapping


Module Contents
---------------

.. py:data:: TOKEN_PATTERNS

.. py:function:: tokenize(input_string: str) -> dict[str, str]

   tokenize

   :param input_string: str
   :return: dict[str,str] tokens


.. py:function:: generate_mapping(input_string: str) -> Optional[dict[str, str]]

   generate_mapping

   :param input_string: str
   :return: Optional[dict[str, str]]


