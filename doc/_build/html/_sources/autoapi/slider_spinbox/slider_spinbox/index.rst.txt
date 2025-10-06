slider_spinbox.slider_spinbox
=============================

.. py:module:: slider_spinbox.slider_spinbox

.. autoapi-nested-parse::

   Slider Spinbox Widget for Roland JD-Xi



Classes
-------

.. autoapisummary::

   slider_spinbox.slider_spinbox.AdsrSliderSpinbox


Functions
---------

.. autoapisummary::

   slider_spinbox.slider_spinbox.create_spinbox
   slider_spinbox.slider_spinbox.create_double_spinbox


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


.. py:class:: AdsrSliderSpinbox(param: jdxi_editor.midi.data.parameter.synth.AddressParameter, min_value: float = 0.0, max_value: float = 1.0, units: str = '', label: str = '', value: int = None, create_parameter_slider: Callable = None, parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   ADSR Slider and Spinbox widget for Roland JD-Xi


   .. py:attribute:: envelope_changed


   .. py:attribute:: param


   .. py:attribute:: factor
      :value: 127



   .. py:attribute:: create_parameter_slider
      :value: None



   .. py:attribute:: slider


   .. py:method:: convert_to_envelope(value: float) -> float

      Convert the slider value to envelope value based on parameter type

      :param value: float
      :return: float



   .. py:method:: convert_from_envelope(value: float)


   .. py:method:: _slider_changed(value: int) -> None

      Handle changes from the slider and update the spinbox and envelope

      :param value:
      :return:



   .. py:method:: _spinbox_changed(value: float) -> None

      Handle changes from the spinbox and update the slider and envelope

      :param value:
      :return: None



   .. py:method:: setValue(value: float)

      Set the value of the spinbox and slider

      :param value: int
      :return: None



   .. py:method:: value() -> float

      Get the value of the spinbox

      :return: int



   .. py:method:: update()

      Update the envelope values and plot



