jdxi_editor.ui.image.waveform
=============================

.. py:module:: jdxi_editor.ui.image.waveform

.. autoapi-nested-parse::

   waveform_icons

   This module provides functions to generate PNG images representing different waveform icons
   using the Python Imaging Library (PIL). Each function returns address base64-encoded string of
   the generated image.

   Functions:
       generate_waveform_icon(icon_type, foreground_color, icon_scale): Generates address
       - triangle: Generates address triangle waveform icon.
       - upsaw: Generates an upward sawtooth waveform icon.
       - square: Generates address square waveform icon.
       - sine: Generates address sine waveform icon.
       - noise: Generates address noise waveform icon.
       - spsaw: Generates address special sawtooth waveform icon.
       - pcm: Generates address PCM waveform icon.
       - adsr: Generates an ADSR envelope waveform icon.



Functions
---------

.. autoapisummary::

   jdxi_editor.ui.image.waveform.generate_waveform_icon


Module Contents
---------------

.. py:function:: generate_waveform_icon(waveform: str, foreground_color: str, icon_scale: float) -> str

   Generate address waveform icon as address base64-encoded PNG image

   :param waveform: str
   :param foreground_color: str
   :param icon_scale: float
   :return: icon
   :rtype: str


