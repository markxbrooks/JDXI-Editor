jdxi_editor.midi.data.address.program
=====================================

.. py:module:: jdxi_editor.midi.data.address.program


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.address.program.ProgramCommonAddress


Module Contents
---------------

.. py:class:: ProgramCommonAddress(msb: int = AddressStartMSB.TEMPORARY_PROGRAM, umb: int = MidiConstant.ZERO_BYTE, lmb: int = MidiConstant.ZERO_BYTE, lsb: int = MidiConstant.ZERO_BYTE)

   Bases: :py:obj:`jdxi_editor.midi.data.address.address.RolandSysExAddress`


   A convenient subclass for the standard "Program Common" address in Roland SysEx messages.


