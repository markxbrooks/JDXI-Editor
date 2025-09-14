jdxi_editor.log.logger
======================

.. py:module:: jdxi_editor.log.logger

.. autoapi-nested-parse::

   log message



Classes
-------

.. autoapisummary::

   jdxi_editor.log.logger.Logger


Functions
---------

.. autoapisummary::

   jdxi_editor.log.logger.format_midi_message_to_hex_string


Module Contents
---------------

.. py:function:: format_midi_message_to_hex_string(message: list) -> str

   format_midi_message_to_hex_string

   :param message: list of bytes
   :return: str


.. py:class:: Logger

   Logger class


   .. py:method:: error(message: str, exception: Optional[Exception] = None, level: int = logging.ERROR, stacklevel: int = 4, silent: bool = False) -> None
      :staticmethod:


      Log an error message, optionally with an exception.



   .. py:attribute:: exception


   .. py:method:: warning(message: str, exception: Optional[Exception] = None, level: int = logging.WARNING, stacklevel: int = 4, silent: bool = False) -> None
      :staticmethod:


      Log an error message, optionally with an exception.



   .. py:method:: json(data: Any, stacklevel: int = 3, silent: bool = False) -> None
      :staticmethod:


      Log a JSON object or JSON string as a single compact line.



   .. py:method:: message(message: str, level: int = logging.INFO, stacklevel: int = 3, silent: bool = False) -> None
      :staticmethod:


      Log a plain message with optional formatting.



   .. py:attribute:: info


   .. py:attribute:: debug


   .. py:method:: parameter(message: str, parameter: Any, float_precision: int = 2, max_length: int = 300, level: int = logging.INFO, stacklevel: int = 4, silent: bool = False) -> None
      :staticmethod:


      Log a structured message including the type and value of a parameter.



   .. py:method:: header_message(message: str, level: int = logging.INFO, silent: bool = False, stacklevel: int = 4) -> None
      :staticmethod:


      Logs a visually distinct header message with separator lines and emojis.

      :param stacklevel:
      :param silent: bool whether or not to write to the log
      :param message: The message to log.
      :param level: Logging level (default: logging.INFO).



   .. py:method:: debug_info(successes: list, failures: list, stacklevel: int = 4) -> None
      :staticmethod:


      Logs debug information about the parsed SysEx data.

      :param stacklevel: int
      :param successes: list – Parameters successfully decoded.
      :param failures: list – Parameters that failed decoding.



