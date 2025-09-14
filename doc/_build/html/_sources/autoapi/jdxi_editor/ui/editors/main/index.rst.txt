jdxi_editor.ui.editors.main
===========================

.. py:module:: jdxi_editor.ui.editors.main

.. autoapi-nested-parse::

   JD-Xi Editor UI setup.

   This class defines the main user interface for the JD-Xi Editor application, inheriting from QMainWindow.
   Key Features:
   - Initializes the main window with a tabbed editor interface.

   .. method:: - __init__

      Initializes the UI adds elements and sets up the main layout.

   .. method:: - _close_editor_tab

      Handles the closing of editor tabs.
      



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.main.MainEditor


Module Contents
---------------

.. py:class:: MainEditor(parent: PySide6.QtWidgets.QMainWindow = None)

   Bases: :py:obj:`PySide6.QtWidgets.QMainWindow`


   JD-Xi UI setup, with as little as possible functionality, which is to be super-classed


   .. py:attribute:: jdxi_main_window
      :value: None



   .. py:attribute:: editor_registry
      :value: None



   .. py:attribute:: editors
      :value: []



   .. py:attribute:: editor_tab_widget


   .. py:method:: closeEvent(event)

      close the editor tab widget, but dont delete it

      :param event: QEvent



