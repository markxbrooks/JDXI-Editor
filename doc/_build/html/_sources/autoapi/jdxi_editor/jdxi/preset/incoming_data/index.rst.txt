jdxi_editor.jdxi.preset.incoming_data
=====================================

.. py:module:: jdxi_editor.jdxi.preset.incoming_data


Classes
-------

.. autoapisummary::

   jdxi_editor.jdxi.preset.incoming_data.IncomingPresetData


Module Contents
---------------

.. py:class:: IncomingPresetData

   .. py:attribute:: program_number
      :type:  Optional[int]
      :value: None



   .. py:attribute:: program_name
      :type:  Optional[str]
      :value: None



   .. py:attribute:: channel
      :type:  Optional[int]
      :value: None



   .. py:attribute:: msb
      :type:  Optional[int]
      :value: None



   .. py:attribute:: lsb
      :type:  Optional[int]
      :value: None



   .. py:attribute:: tone_names
      :type:  Dict[str, str]


   .. py:method:: set_tone_name(part: str, name: str)


   .. py:method:: get_tone_name(part: str) -> Optional[str]


   .. py:method:: clear()


