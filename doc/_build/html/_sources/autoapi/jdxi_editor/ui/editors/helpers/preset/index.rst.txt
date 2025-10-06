jdxi_editor.ui.editors.helpers.preset
=====================================

.. py:module:: jdxi_editor.ui.editors.helpers.preset


Functions
---------

.. autoapisummary::

   jdxi_editor.ui.editors.helpers.preset.get_preset_list_number_by_name
   jdxi_editor.ui.editors.helpers.preset.get_preset_parameter_value


Module Contents
---------------

.. py:function:: get_preset_list_number_by_name(preset_name: str, preset_list: List[Dict[str, str]]) -> Optional[int]

   Retrieve a program's number (without bank letter) by its name using regex search

   :param preset_name: str
   :param preset_list: list
   :return: int preset id


.. py:function:: get_preset_parameter_value(parameter: str, id: Union[str, int], preset_list: List[dict] = DIGITAL_PRESET_LIST) -> Union[Optional[int], Any]

   Retrieve a specific parameter value from a preset by its ID.

   :param parameter: Name of the parameter to retrieve.
   :param id: Preset ID (e.g., "001" or integer 1).
   :param preset_list: List of preset dictionaries.
   :return: The parameter value, or None if not found.


