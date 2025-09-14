jdxi_editor.log.error
=====================

.. py:module:: jdxi_editor.log.error

.. autoapi-nested-parse::

   log message



Functions
---------

.. autoapisummary::

   jdxi_editor.log.error.log_error


Module Contents
---------------

.. py:function:: log_error(message: str, exception: Optional[Exception] = None, level: int = logging.ERROR, stacklevel=2) -> None

   Log an error message with emojis based on severity and content keywords.

   :param message: str The message to log.
   :param exception: Optional [str] error message
   :param level: int Logging level (default: logging.ERROR).
   :param stacklevel: int sets the stack level to log the message from the caller's context
   :return: None


