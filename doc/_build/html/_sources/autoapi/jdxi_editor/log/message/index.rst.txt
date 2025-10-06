jdxi_editor.log.message
=======================

.. py:module:: jdxi_editor.log.message

.. autoapi-nested-parse::

   log message



Functions
---------

.. autoapisummary::

   jdxi_editor.log.message.log_message


Module Contents
---------------

.. py:function:: log_message(message: str, level: int = logging.INFO, stacklevel=2, silent=False) -> None

   Log a message with emojis based on severity and content keywords.

   :param stacklevel: int sets the stack level to log the message from the caller's context
   :param message: str The message to log.
   :param level: int Logging level (default: logging.INFO).
   :param silent: bool
   :return: None


