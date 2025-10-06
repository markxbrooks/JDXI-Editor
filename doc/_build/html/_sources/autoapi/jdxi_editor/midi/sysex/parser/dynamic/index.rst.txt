jdxi_editor.midi.sysex.parser.dynamic
=====================================

.. py:module:: jdxi_editor.midi.sysex.parser.dynamic

.. autoapi-nested-parse::

   Dynamic Parameter Map resolver



Functions
---------

.. autoapisummary::

   jdxi_editor.midi.sysex.parser.dynamic.dynamic_map_resolver
   jdxi_editor.midi.sysex.parser.dynamic.parse_sysex_with_dynamic_mapping


Module Contents
---------------

.. py:function:: dynamic_map_resolver(data: bytes) -> Dict[str, str]

   Dynamically resolve mappings for SysEx data.

   :param data: bytes SysEx message data
   :return: Dict[str, str]


.. py:function:: parse_sysex_with_dynamic_mapping(data: bytes) -> Dict[str, str]

   Parse SysEx data using dynamic mapping.

   :param data: bytes SysEx message data
   :return: Dict[str, str]


