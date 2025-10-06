jdxi_editor.ui.windows.patch.manager
====================================

.. py:module:: jdxi_editor.ui.windows.patch.manager

.. autoapi-nested-parse::

   Patch Manager Module
   ====================s

   This module defines the `PatchManager` class, a PySide6-based GUI for loading
   and saving MIDI patch files for the Roland JD-Xi synthesizer.

   Features:
   - Allows users to browse for patch files using a file dialog.
   - Supports both saving and loading patches, depending on the mode.
   - Integrates with `MIDIHelper` for handling MIDI patch operations.
   - Implements a simple, dark-themed UI with action buttons.

   Classes:
   - PatchManager: A QMainWindow that provides a user interface for managing patch files.

   Dependencies:
   - PySide6
   - jdxi_editor.midi.io.MIDIHelper
   - jdxi_editor.ui.style.Style



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.windows.patch.manager.PatchManager


Functions
---------

.. autoapisummary::

   jdxi_editor.ui.windows.patch.manager.zip_directory


Module Contents
---------------

.. py:function:: zip_directory(folder_path, zip_path)

.. py:class:: PatchManager(midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper] = None, parent=None, save_mode=False, editors=None)

   Bases: :py:obj:`PySide6.QtWidgets.QMainWindow`


   .. py:attribute:: midi_helper
      :value: None



   .. py:attribute:: save_mode
      :value: False



   .. py:attribute:: editors
      :value: None



   .. py:attribute:: path_input


   .. py:attribute:: json_composer


   .. py:method:: _browse_file()

      Open file dialog for selecting patch file



   .. py:method:: _handle_action()

      Handle save/load action



