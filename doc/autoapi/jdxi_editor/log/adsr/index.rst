jdxi_editor.log.adsr
====================

.. py:module:: jdxi_editor.log.adsr

.. autoapi-nested-parse::

   Log ADSR Parameter



Functions
---------

.. autoapisummary::

   jdxi_editor.log.adsr.log_adsr_parameter


Module Contents
---------------

.. py:function:: log_adsr_parameter(umb: int, lmb: int, param: jdxi_editor.midi.data.parameter.synth.AddressParameter, value: int, level: int = logging.INFO) -> None

   Log slider parameters for debugging.

   :param umb: int The UMB
   :param lmb: int The LMB
   :param param: AddressParameter The parameter
   :param value: int The value
   :param level: int The log level
   :return: None


