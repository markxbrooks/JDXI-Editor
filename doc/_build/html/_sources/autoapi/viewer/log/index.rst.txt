viewer.log
==========

.. py:module:: viewer.log

.. autoapi-nested-parse::

   Module: log_viewer
   ==================

   This module provides a graphical log viewer using PySide6. The `LogViewer` class is a
   QMainWindow-based widget that displays real-time logging messages in a styled QTextEdit
   widget. It supports color-coded log levels and provides a button to clear the log display.

   Classes:
   --------
   - `LogViewer`: A main window that captures and displays log messages in real time.
   - `LogHandler`: A custom logging handler that redirects log output to the `QTextEdit` widget.

   Features:
   ---------
   - Dark theme with a modern red-accented styling.
   - Supports logging levels with color-coded messages:
     - **Red** for errors
     - **Orange** for warnings
     - **White** for info messages
     - **Gray** for debug messages
   - Provides a "Clear Log" button to reset the log display.
   - Automatically removes the log handler when closed.

   Usage Example:
   --------------
   >>> viewer = LogViewer()
   >>> viewer.show()
   >>> log.message("This is an info message.")
   >>> log.message("This is an error message.")



Classes
-------

.. autoapisummary::

   viewer.log.LogViewer
   viewer.log.LogHandler


Module Contents
---------------

.. py:class:: LogViewer(midi_helper=None, parent=None)

   Bases: :py:obj:`PySide6.QtWidgets.QMainWindow`


   .. py:attribute:: log_text


   .. py:attribute:: log_handler


   .. py:method:: clear_log()

      Clear the log display



   .. py:method:: closeEvent(event)

      Remove log handler when window is closed



.. py:class:: LogHandler(text_widget)

   Bases: :py:obj:`logging.Handler`


   Custom logging handler to display logs in QTextEdit


   .. py:attribute:: text_widget


   .. py:method:: emit(record)

      Do whatever it takes to actually log the specified logging record.

      This version is intended to be implemented by subclasses and so
      raises a NotImplementedError.



