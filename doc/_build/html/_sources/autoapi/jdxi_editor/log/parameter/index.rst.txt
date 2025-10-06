jdxi_editor.log.parameter
=========================

.. py:module:: jdxi_editor.log.parameter

.. autoapi-nested-parse::

   parameter.py



Functions
---------

.. autoapisummary::

   jdxi_editor.log.parameter.log_parameter


Module Contents
---------------

.. py:function:: log_parameter(message: str, parameter: Any, float_precision: int = 2, max_length: int = 300, level: int = logging.INFO, silent: bool = False)

   Log a structured representation of a parameter with type, formatted value, and optional emoji context.

   :param silent: bool suppress the log or not
   :param message: str The message to log.
   :param parameter: Any The parameter to log.
   :param float_precision: int The float precision.
   :param max_length: int The max length.
   :param level: int The log level.


