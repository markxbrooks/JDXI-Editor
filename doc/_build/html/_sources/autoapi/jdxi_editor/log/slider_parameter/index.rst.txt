jdxi_editor.log.slider_parameter
================================

.. py:module:: jdxi_editor.log.slider_parameter

.. autoapi-nested-parse::

   Log Slider Parameters



Functions
---------

.. autoapisummary::

   jdxi_editor.log.slider_parameter.log_slider_parameters


Module Contents
---------------

.. py:function:: log_slider_parameters(address: jdxi_editor.midi.data.address.address.RolandSysExAddress, param: jdxi_editor.midi.data.parameter.synth.AddressParameter, midi_value: int, slider_value: Union[int, float], level: int = logging.INFO) -> None

   Log slider parameters for debugging.

   :param address: int The address
   :param param: AddressParameter The parameter
   :param midi_value: int The value
   :param slider_value: int The slider value
   :param level: int The log level
   :return: None


