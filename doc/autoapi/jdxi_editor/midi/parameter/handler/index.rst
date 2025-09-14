jdxi_editor.midi.parameter.handler
==================================

.. py:module:: jdxi_editor.midi.parameter.handler

.. autoapi-nested-parse::

   Module: parameter_handler

   This module defines the `ParameterHandler` class, which manages MIDI parameter values
   and emits signals when parameters are updated.

   Classes:
       - ParameterHandler: Handles storing, updating, retrieving, and clearing MIDI parameters.

   Signals:
       - parameters_updated: Emitted when parameter values change.

   .. method:: - update_parameter(address, value)

      Updates the value of a parameter at the given address.

   .. method:: - get_parameter(address)

      Retrieves the value of a parameter at the given address.

   .. method:: - clear_parameters()

      Clears all stored parameters.
      



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.parameter.handler.ParameterHandler


Module Contents
---------------

.. py:class:: ParameterHandler

   Bases: :py:obj:`PySide6.QtCore.QObject`


   .. py:attribute:: parameters_updated


   .. py:attribute:: _parameters


   .. py:method:: update_parameter(address: List[int], value: int) -> None

      Update address parameter value
      :param address: List[int]
      :param value: int
      :return: None



   .. py:method:: get_parameter(address: List[int]) -> int

      Get address parameter value
      :param address: List[int]
      :return: int



   .. py:method:: clear_parameters() -> None

      Clear all parameters
      :return: None



