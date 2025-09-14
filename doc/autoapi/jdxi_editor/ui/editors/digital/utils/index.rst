jdxi_editor.ui.editors.digital.utils
====================================

.. py:module:: jdxi_editor.ui.editors.digital.utils

.. autoapi-nested-parse::

   This module contains utility functions for handling SysEx data related to digital synths.



Functions
---------

.. autoapisummary::

   jdxi_editor.ui.editors.digital.utils.filter_sysex_keys
   jdxi_editor.ui.editors.digital.utils._get_synth_number
   jdxi_editor.ui.editors.digital.utils.get_partial_number
   jdxi_editor.ui.editors.digital.utils._is_valid_sysex_area
   jdxi_editor.ui.editors.digital.utils.log_synth_area_info
   jdxi_editor.ui.editors.digital.utils._is_digital_synth_area
   jdxi_editor.ui.editors.digital.utils._sysex_area_matches
   jdxi_editor.ui.editors.digital.utils._sysex_area2_matches
   jdxi_editor.ui.editors.digital.utils._sysex_tone_matches
   jdxi_editor.ui.editors.digital.utils.get_area
   jdxi_editor.ui.editors.digital.utils.to_hex


Module Contents
---------------

.. py:function:: filter_sysex_keys(sysex_data: dict) -> dict

   Filter out unwanted keys from the SysEx data.

   :param sysex_data: dict
   :return: dict


.. py:function:: _get_synth_number(synth_tone: str) -> int

   Get the synth number based on the synth tone.

   :param synth_tone: str
   :return: int


.. py:function:: get_partial_number(synth_tone: str, partial_map: dict = SYNTH_PARTIAL_MAP) -> int

   Get the partial number based on the synth tone.

   :param synth_tone: str
   :param partial_map: str
   :return: int


.. py:function:: _is_valid_sysex_area(sysex_data: dict) -> bool

   Check if the SysEx data is from a valid digital synth area.

   :param sysex_data: dict
   :return: bool


.. py:function:: log_synth_area_info(sysex_data: dict) -> None

   Log information about the SysEx area.

   :param sysex_data: dict
   :return: None


.. py:function:: _is_digital_synth_area(area_code: int) -> bool

   Check if the area code corresponds to a digital synth area.

   :param area_code: int
   :return: bool


.. py:function:: _sysex_area_matches(sysex_data: dict, area: int) -> bool

   Check if the SysEx data matches the expected area.

   :param sysex_data: dict
   :param area: int
   :return: bool


.. py:function:: _sysex_area2_matches(sysex_data: dict, area: int) -> bool

   Check if the SysEx data matches the expected area.

   :param sysex_data: dict
   :param area: int
   :return: bool


.. py:function:: _sysex_tone_matches(sysex_data: dict, tone: int) -> bool

   Check if the SysEx data matches the expected area.

   :param sysex_data: dict
   :param tone: int
   :return: bool


.. py:function:: get_area(data: list) -> str

   Map address bytes to corresponding temporary area.

   :param data: list[int, int]
   :return: str


.. py:function:: to_hex(value: int, width: int = 2) -> str

   Convert a value to a hex string.

   :param value: int
   :param width: int
   :return: str


