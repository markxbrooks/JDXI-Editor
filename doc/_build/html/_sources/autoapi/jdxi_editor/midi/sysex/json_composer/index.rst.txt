jdxi_editor.midi.sysex.json_composer
====================================

.. py:module:: jdxi_editor.midi.sysex.json_composer

.. autoapi-nested-parse::

   JDXiSysExComposer



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.sysex.json_composer.JDXiJSONComposer


Module Contents
---------------

.. py:class:: JDXiJSONComposer(editor: Optional[jdxi_editor.ui.editors.SynthEditor] = None)

   JSON SysExComposer


   .. py:attribute:: json_string
      :value: None



   .. py:attribute:: temp_folder


   .. py:method:: compose_message(editor: jdxi_editor.ui.editors.SynthEditor) -> Optional[dict[Union[str, Any], Union[str, Any]]]

      :param editor: SynthEditor Editor instance to process

      :return: str JSON SysEx message



   .. py:method:: save_json(file_path: str) -> None

      Save the JSON string to a file

      :param file_path: str File path to save the JSON
      :return: None



   .. py:method:: process_editor(editor: jdxi_editor.ui.editors.SynthEditor, temp_folder: pathlib.Path) -> pathlib.Path

      Process the editor and save the JSON

      :param editor: SynthEditor Editor instance to process
      :param temp_folder: str Temporary folder to save the JSON
      :return: None



