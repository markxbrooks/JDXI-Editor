jdxi_editor.midi.data.parameter.digital.helpers.digital_common
==============================================================

.. py:module:: jdxi_editor.midi.data.parameter.digital.helpers.digital_common

.. autoapi-nested-parse::

   Digital Common



Functions
---------

.. autoapisummary::

   jdxi_editor.midi.data.parameter.digital.helpers.digital_common.parse_digital_common_parameters


Module Contents
---------------

.. py:function:: parse_digital_common_parameters(data: list) -> dict

   Parses JD-Xi tone parameters from SysEx data, including Oscillator, Filter, and Amplitude parameters.

   :param data: SysEx message containing tone parameters.
   :type data: :py:class:`bytes`

   :returns: Parsed parameters.
   :rtype: dict


