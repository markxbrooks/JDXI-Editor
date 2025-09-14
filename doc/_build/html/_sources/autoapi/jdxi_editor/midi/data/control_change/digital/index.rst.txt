jdxi_editor.midi.data.control_change.digital
============================================

.. py:module:: jdxi_editor.midi.data.control_change.digital

.. autoapi-nested-parse::

   DigitalControlChange

   Example usage

   # Get Cutoff CC value for Partial 2
   cutoff_partial_2 = DigitalControlChange.get_cc_value("Cutoff", 2)
   print(f"Cutoff (Partial 2): {cutoff_partial_2}")

   # Get Envelope NRPN value for Partial 3
   envelope_partial_3 = DigitalControlChange.get_nrpn_value("Envelope", 3)
   print(f"Envelope (Partial 3): {envelope_partial_3}")

   envelope_map = DigitalControlChange.get_nrpn_map("Envelope")



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.control_change.digital.DigitalControlChange


Module Contents
---------------

.. py:class:: DigitalControlChange

   Grouped version of Control Change (CC) values for easier access.


   .. py:attribute:: CC


   .. py:attribute:: NRPN


   .. py:method:: get_cc_value(group: str, partial: int) -> int
      :staticmethod:


      Retrieve CC value based on group and partial.



   .. py:method:: get_nrpn_value(group: str, partial: int) -> int
      :staticmethod:


      Retrieve NRPN value based on group and partial.



   .. py:method:: get_display_value(value: int, group: str, partial: int) -> str
      :staticmethod:


      Convert raw value to display value



   .. py:method:: get_nrpn_map(group: str) -> dict
      :staticmethod:


      Return dynamic NRPN values for each partial from the given group.



   .. py:method:: get_cc_map(group: str) -> dict
      :staticmethod:


      Return dynamic CC values for each partial from the given group.



