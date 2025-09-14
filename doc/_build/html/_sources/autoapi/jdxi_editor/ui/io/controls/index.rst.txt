jdxi_editor.ui.io.controls
==========================

.. py:module:: jdxi_editor.ui.io.controls

.. autoapi-nested-parse::

   Save all controls to a single JSON file.
   This module provides a function to save the controls from multiple editor instances
   to a single JSON file. The function takes a list of editor instances and a file path
   as input, and it combines the controls into a single JSON object before saving it.



Functions
---------

.. autoapisummary::

   jdxi_editor.ui.io.controls.save_all_controls_to_single_file


Module Contents
---------------

.. py:function:: save_all_controls_to_single_file(editors: list, file_path: str) -> None

   Save the controls from all editors to a single JSON file.

   :param editors: list A list of editor instances (e.g., AnalogSynthEditor, DigitalSynthEditor).
   :param file_path: str The file path where the combined JSON data will be saved.
   :return: None


