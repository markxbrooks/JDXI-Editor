jdxi_editor.midi.data.parameter.digital.modify
==============================================

.. py:module:: jdxi_editor.midi.data.parameter.digital.modify

.. autoapi-nested-parse::

   AddressParameterDigitalModify: JD-Xi Digital Synthesizer Parameter Mapping
   ====================================================================
   Defines the AddressParameterDigitalModify class for modifying parameters of
   Digital/SuperNATURAL synth tones in the JD-Xi.

   This class provides attributes and methods to manage various modulation
   parameters shared across all partials of a digital synth tone. It also
   includes methods for retrieving display text representations of switch
   values, parameter lookup by name, and value validation.

   Example usage:

   # Create a AddressParameterDigitalModify instance for Attack Time Interval Sensitivity
   attack_time_param = AddressParameterDigitalModify(*AddressParameterDigitalModify.ATTACK_TIME_INTERVAL_SENS)

   # Validate a value
   validated_value = attack_time_param.validate_value(100)

   # Get display text for a switch value
   text = attack_time_param.get_switch_text(1)  # For ENVELOPE_LOOP_MODE, returns "FREE-RUN"

   # Retrieve parameter by name
   param = AddressParameterDigitalModify.get_by_name("ENVELOPE_LOOP_MODE")
   if param:
       print(param.name, param.min_val, param.max_val)



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.parameter.digital.modify.AddressParameterDigitalModify


Module Contents
---------------

.. py:class:: AddressParameterDigitalModify(address: int, min_val: int, max_val: int, tooltip: str = '')

   Bases: :py:obj:`jdxi_editor.midi.data.parameter.synth.AddressParameter`


   Modify parameters for Digital/SuperNATURAL synth tones.
   These parameters are shared across all partials.


   .. py:attribute:: address


   .. py:attribute:: min_val


   .. py:attribute:: max_val


   .. py:attribute:: tooltip
      :value: ''



   .. py:attribute:: ATTACK_TIME_INTERVAL_SENS


   .. py:attribute:: RELEASE_TIME_INTERVAL_SENS


   .. py:attribute:: PORTAMENTO_TIME_INTERVAL_SENS


   .. py:attribute:: ENVELOPE_LOOP_MODE


   .. py:attribute:: ENVELOPE_LOOP_SYNC_NOTE


   .. py:attribute:: CHROMATIC_PORTAMENTO


   .. py:method:: get_switch_text(value: int) -> str

      Get display text for switch values



   .. py:method:: get_by_name(param_name)
      :staticmethod:


      Get the Parameter by name.



   .. py:method:: validate_value(value: int) -> int

      Validate and convert parameter value



   .. py:method:: get_address_for_partial(partial_number: int = 0)

      Get the address for the partial number.

      :param partial_number: int
      :return: int default area to be subclassed



