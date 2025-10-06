jdxi_editor.ui.windows.patch.name_editor
========================================

.. py:module:: jdxi_editor.ui.windows.patch.name_editor

.. autoapi-nested-parse::

   Patch Name Editor Module
   ========================

   This module defines the `PatchNameEditor` class, a PySide6-based dialog for
   editing the name of a JD-Xi patch.

   Features:
   - Provides a simple UI for renaming patches with a maximum of 12 characters.
   - Ensures patch names are converted to uppercase, matching JD-Xi conventions.
   - Includes "Save" and "Cancel" buttons for user confirmation.
   - Applies a custom dark theme for styling.

   Classes:
   - PatchNameEditor: A QDialog that allows users to modify a patch name.

   Dependencies:
   - PySide6
   - jdxi_editor.ui.style.Style

   Example Usage
   =============
   >>>dialog = PatchNameEditor(current_name="Piano")
   ...if dialog.exec_():  # If the user clicks Save
   ...    sys_ex_bytes = dialog.get_sysex_bytes()
   ...    print("SysEx Bytes:", sys_ex_bytes)



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.windows.patch.name_editor.PatchNameEditor
   jdxi_editor.ui.windows.patch.name_editor.PatchNameEditorOld


Module Contents
---------------

.. py:class:: PatchNameEditor(current_name='', parent=None)

   Bases: :py:obj:`PySide6.QtWidgets.QDialog`


   .. py:attribute:: tone_name_input


   .. py:method:: get_sysex_string()

      Converts the current name input to SysExAddress bytes.
      JD-Xi patch names are encoded as ASCII characters, padded with spaces if shorter than 12 chars.



   .. py:method:: get_sysex_bytes()

      Converts the current name input to SysExAddress bytes.
      JD-Xi patch names are encoded as ASCII characters, padded with spaces if shorter than 12 chars.



.. py:class:: PatchNameEditorOld(current_name='', parent=None)

   Bases: :py:obj:`PySide6.QtWidgets.QDialog`


   .. py:attribute:: name_input


   .. py:method:: get_name()

      Get the edited patch name



