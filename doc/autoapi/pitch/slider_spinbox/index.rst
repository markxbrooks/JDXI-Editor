pitch.slider_spinbox
====================

.. py:module:: pitch.slider_spinbox


Classes
-------

.. autoapisummary::

   pitch.slider_spinbox.PitchEnvSliderSpinbox


Functions
---------

.. autoapisummary::

   pitch.slider_spinbox.create_spinbox
   pitch.slider_spinbox.create_double_spinbox


Module Contents
---------------

.. py:function:: create_spinbox(min_value: int, max_value: int, suffix: str, value: int) -> PySide6.QtWidgets.QSpinBox

   Create a spinbox with specified range and suffix

   :param min_value: int
   :param max_value: int
   :param suffix: str
   :param value: int
   :return: QSpinBox


.. py:function:: create_double_spinbox(min_value: float, max_value: float, step: float, value: int) -> PySide6.QtWidgets.QDoubleSpinBox

   Create a double spinbox with specified range, step, and initial value.

   :param min_value: int
   :param max_value: int
   :param step: float
   :param value: int
   :return: QDoubleSpinBox


.. py:class:: PitchEnvSliderSpinbox(param: jdxi_editor.midi.data.parameter.synth.AddressParameter, min_value: float = 0.0, max_value: float = 1.0, units: str = '', label: str = '', value: int = None, create_parameter_slider: Callable = None, parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Pitch Env Slider and Spinbox widget for Roland JD-Xi


   .. py:attribute:: envelope_changed


   .. py:attribute:: param


   .. py:attribute:: factor
      :value: 127



   .. py:attribute:: create_parameter_slider
      :value: None



   .. py:attribute:: slider


   .. py:method:: convert_to_envelope(value: float) -> float

      Convert MIDI value to envelope value

      :param value: float
      :return: float



   .. py:method:: convert_from_envelope(value: float) -> int

      Convert envelope value to MIDI value

      :param value: int
      :return: int



   .. py:method:: _slider_changed(value: int) -> None

      slider changed

      :param value: int slider value
      :return: None



   .. py:method:: _spinbox_changed(value: float)

      Spinbox changed

      :param value: float double spinbox value
      :return: None



   .. py:method:: setValue(value: float)

      Set the value of the double spinbox and slider

      :param value: float
      :return: None



   .. py:method:: value() -> float

      Get the value of the spinbox

      :return: int



   .. py:method:: update()

      Update the envelope values and plot



