jdxi_editor.log.decorator
=========================

.. py:module:: jdxi_editor.log.decorator


Functions
---------

.. autoapisummary::

   jdxi_editor.log.decorator.get_qc_tag
   jdxi_editor.log.decorator.get_midi_tag
   jdxi_editor.log.decorator.decorate_log_message


Module Contents
---------------

.. py:function:: get_qc_tag(msg: str) -> str

   get QC emoji etc

   :param msg: str
   :return: str


.. py:function:: get_midi_tag(msg: str) -> str

   get Midi emoji etc

   :param msg: str
   :return: str


.. py:function:: decorate_log_message(message: str, level: int) -> str

   Adds emoji decoration to a log message based on its content and log level.

   :param message: The original log message
   :param level: The logging level
   :return: Decorated log message string


