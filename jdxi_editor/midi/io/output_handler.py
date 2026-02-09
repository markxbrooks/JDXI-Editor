"""
MIDI Output Handler
===================

This module provides the `MIDIOutHandler` class for managing MIDI output, allowing users to send
note-on, note-off, and control change messages through address specified MIDI output port.

Dependencies:
    - rtmidi: A library for working with MIDI messages and ports.

Example usage:
    handler = MIDIOutHandler("MIDI Output Port")
    handler.send_note_on(60, velocity=100)
    handler.send_note_off(60)
    handler.send_control_change(7, 127)
    handler.close()

"""

import logging
from typing import Iterable, Optional

from decologr import Decologr as log
from picomidi.constant import Midi
from picomidi.core.bitmask import BitMask
from picomidi.utils.formatting import (
    format_message_to_hex_string as format_midi_message_to_hex_string,
)
from PySide6.QtCore import Signal

from jdxi_editor.midi.data.parsers.util import OUTBOUND_MESSAGE_IGNORED_KEYS
from jdxi_editor.midi.io.controller import MidiIOController
from jdxi_editor.midi.message import (
    ControlChangeMessage,
    IdentityRequestMessage,
    MidiMessage,
    ProgramChangeMessage,
)
from jdxi_editor.midi.message.channel.message import ChannelMessage
from jdxi_editor.midi.message.roland import JDXiSysEx
from jdxi_editor.midi.sysex.parser.sysex import JDXiSysExParser
from jdxi_editor.midi.sysex.validation import validate_midi_message


class MidiOutHandler(MidiIOController):
    """Helper class for MIDI communication with the JD-Xi."""

    midi_message_outgoing = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.channel = 1
        self.sysex_parser = JDXiSysExParser()

    import threading

    # Global lock for all MIDI output operations
    _midi_send_lock = threading.RLock()

    def send_raw_message(self, message: Iterable[int]) -> bool:
        """
        Thread-safe version of sending a raw MIDI message.
        Handles logging, validation, and exceptions safely.
        """
        with self._midi_send_lock:
            try:
                if not validate_midi_message(message):
                    log.message("[MidiOutHandler] MIDI message validation failed.")
                    return False

                # Ensure message is a list of integers before formatting
                def safe_int(val):
                    # Check for enums FIRST (IntEnum inherits from int, so isinstance check must come after)
                    if hasattr(val, "value") and not isinstance(
                        val, type
                    ):  # Handle enums (but not enum classes)
                        enum_val = val.value
                        # Ensure we get the actual integer value, not the enum
                        if isinstance(enum_val, int) and not hasattr(enum_val, "value"):
                            return enum_val
                        # If enum_val is still an enum, recurse
                        if hasattr(enum_val, "value"):
                            return safe_int(enum_val)
                        try:
                            return int(float(enum_val))  # Handle string enum values
                        except (ValueError, TypeError):
                            return 0
                    if isinstance(val, int):
                        return val
                    try:
                        return int(float(val))  # Handle floats and strings
                    except (ValueError, TypeError):
                        return 0

                message_list_for_formatting = [safe_int(x) for x in message]
                formatted_message = format_midi_message_to_hex_string(
                    message_list_for_formatting
                )

                if not self.midi_out.is_port_open():
                    log.message("[MidiOutHandler] MIDI output port is not open.")
                    return False

                # Parse SysEx safely - only attempt if message is actually SysEx (starts with 0xF0)
                filtered_data = {}
                message_list = list(message)
                if message_list and message_list[0] == Midi.SYSEX.START:
                    # This is a SysEx message, try to parse it
                    try:
                        parsed_data = self.sysex_parser.parse_bytes(bytes(message))
                        filtered_data = {
                            k: v
                            for k, v in parsed_data.items()
                            if k not in OUTBOUND_MESSAGE_IGNORED_KEYS
                        }
                    except ValueError as parse_ex:
                        # Skip logging for non-JD-Xi messages (e.g., universal identity_request requests)
                        error_msg = str(parse_ex)
                        if "Not a JD-Xi SysEx message" in error_msg:
                            # This is a universal MIDI message, not a JD-Xi message - skip silently
                            filtered_data = {}
                        else:
                            # Log warning for actual JD-Xi parsing errors
                            log.message(
                                f"SysEx parsing failed: {parse_ex}",
                                level=logging.WARNING,
                            )
                            filtered_data = {}
                    except Exception as parse_ex:
                        # Log warning for other parsing errors
                        log.message(
                            f"SysEx parsing failed: {parse_ex}", level=logging.WARNING
                        )
                        filtered_data = {}
                # For non-SysEx messages, filtered_data remains empty (no warning needed)

                # Log safely
                log.message(
                    scope="MidiOutHandler",
                    message=f"[MIDI QC passed] [ Sending message: {formatted_message} ] {filtered_data}",
                    level=logging.INFO,
                    silent=False,
                )
                # Send the message
                self.midi_out.send_message(message)
                self.midi_message_outgoing.emit(message)
                return True

            except Exception as ex:
                # Catch everything to prevent C-level crash from propagating
                log.error(
                    scope="MidiOutHandler",
                    message=f"Unexpected error sending MIDI message: {ex}",
                )
                return False

    def send_note_on(
        self, note: int = 60, velocity: int = 127, channel: int = 1
    ) -> None:
        """
        Send 'Note On' message to the specified MIDI channel.

        :param note: int MIDI note number (0–127), default is 60 (Middle C).
        :param velocity: int Note velocity (0–127), default is 127.
        :param channel: int MIDI channel (1–16), default is 1.
        """
        self.send_channel_message(Midi.NOTE.ON, note, velocity, channel)

    def send_note_off(
        self, note: int = 60, velocity: int = 0, channel: int = 1
    ) -> None:
        """
        Send address 'Note Off' message

        :param note: int MIDI note number (0–127), default is 60 (Middle C).
        :param velocity: int Note velocity (0–127), default is 127.
        :param channel: int MIDI channel (1–16), default is 1.
        """
        self.send_channel_message(Midi.NOTE.OFF, note, velocity, channel)

    def send_channel_message(
        self,
        status: int,
        data1: Optional[int] = None,
        data2: Optional[int] = None,
        channel: int = 1,
    ) -> None:
        """
        Send a MIDI Channel Message.

        :param status: int Status byte (e.g., NOTE_ON, NOTE_OFF, CONTROL_CHANGE).
        :param data1: Optional[int]): First data byte, typically a note or controller number.
        :param data2: Optional[int]): Second data byte, typically velocity or value.
        :param channel: int MIDI channel (1-based, range 1-16).
        :raises: ValueError If the channel is out of range (1-16).
        """
        if not 1 <= channel <= 16:
            raise ValueError(
                "[MidiOutHandler] Invalid MIDI channel: {channel}. Must be 1-16."
            )
        channel_message = ChannelMessage(
            status, data1, data2, channel - 1
        )  # convert to 0-based
        message_bytes_list = channel_message.to_message_list()
        self.send_raw_message(message_bytes_list)

    def send_bank_select(self, msb: int, lsb: int, channel: int = 0) -> bool:
        """
        Send address bank select message.

        :param msb: int Upper byte of the bank.
        :param lsb: int Lower byte of the bank.
        :param channel: int midi channel (0-15).
        :return: bool True if successful, False otherwise.
        """
        log.message(
            scope="MidiOutHandler", message="========Sending bank select=========="
        )
        log.parameter(scope="MidiOutHandler", message="MSB", parameter=msb)
        log.parameter(scope="MidiOutHandler", message="LSB", parameter=lsb)
        log.parameter(scope="MidiOutHandler", message="channel", parameter=channel)
        try:
            # --- Bank Select MSB (CC#0)
            status = Midi.CC.STATUS | (channel & BitMask.LOW_4_BITS)
            self.send_raw_message([status, Midi.CC.BANK.MSB, msb])
            # --- Bank Select LSB (CC#32)
            self.send_raw_message([status, Midi.CC.BANK.LSB, lsb])
            return True
        except (ValueError, TypeError, OSError, IOError) as ex:
            log.error(
                scope="MidiOutHandler", message=f"Error sending bank select: {ex}"
            )
            return False

    def send_identity_request(self) -> bool:
        """
        Send identity_request request message (Universal System Exclusive).

        :return: bool True if the message was sent successfully, False otherwise.
        """
        log.message(
            scope="MidiOutHandler",
            message="=========Sending identity_request request========",
        )
        try:
            identity_request_message = IdentityRequestMessage()
            identity_request_bytes_list = identity_request_message.to_message_list()
            log.message(
                scope="MidiOutHandler",
                message="sending identity_request request message: "
                f"{type(identity_request_bytes_list)} {identity_request_bytes_list}",
            )
            self.send_raw_message(identity_request_bytes_list)
            return True
        except (ValueError, TypeError, OSError, IOError) as ex:
            log.error(
                scope="MidiOutHandler",
                message="Error sending identity_request request: {ex}",
            )
            return False

    def send_midi_message(self, sysex_message: MidiMessage | JDXiSysEx) -> bool:
        """
        Send SysEx parameter change message using a MidiMessage.

        :param sysex_message: MidiMessage instance to be converted and sent.
        :return: True if the message was successfully sent, False otherwise.
        """
        try:
            message = sysex_message.to_message_list()
            return self.send_raw_message(message)

        except (ValueError, TypeError, OSError, IOError) as ex:
            log.error(scope="MidiOutHandler", message=f"Error sending message: {ex}")
            return False

    def send_program_change(self, program: int, channel: int = 0) -> bool:
        """
        Send address program change message.

        :param program: int Program number (0-127).
        :param channel: int MIDI channel (0-15).
        :return: True if successful, False otherwise.
        """
        log.message(scope="MidiOutHandler", message="=====Sending program change====")
        log.parameter(scope="MidiOutHandler", message="program", parameter=program)
        log.parameter(scope="MidiOutHandler", message="channel", parameter=channel)
        try:
            program_change_message = ProgramChangeMessage(
                channel=channel, program=program
            )
            message = program_change_message.to_message_list()
            return self.send_raw_message(message)
        except (ValueError, TypeError, OSError, IOError) as ex:
            log.error(
                scope="MidiOutHandler", message="Error sending program change: {ex}"
            )
            return False

    def send_control_change(
        self, controller: int, value: int, channel: int = 0
    ) -> bool:
        """
        Send control change message.

        :param controller: int Controller number (0–127).
        :param value: int Controller value (0–127).
        :param channel: int MIDI channel (0–15).
        :return: bool True if successful, False otherwise.
        """
        log.message(scope="MidiOutHandler", message="=====Sending control change====")
        log.parameter(
            scope="MidiOutHandler", message="controller", parameter=controller
        )
        log.parameter(scope="MidiOutHandler", message="value", parameter=value)
        log.parameter(scope="MidiOutHandler", message="channel", parameter=channel)
        if not 0 <= channel <= 15:
            log.message(f"Invalid MIDI channel: {channel}. Must be 0-15.")
            return False
        if not 0 <= controller <= 127:
            log.message(f"Invalid controller number: {controller}. Must be 0-127.")
            return False
        if not 0 <= value <= 127:
            log.message(f"Invalid controller value: {value}. Must be 0-127.")
            return False
        try:
            control_change_message = ControlChangeMessage(channel, controller, value)
            message = control_change_message.to_message_list()
            return self.send_raw_message(message)
        except (ValueError, TypeError, OSError, IOError) as ex:
            log.message(f"send_control_change: Error sending control change: {ex}")
            return False

    def send_rpn(self, parameter: int, value: int, channel: int = 0) -> bool:
        """
        Send a Registered Parameter Number (RPN) message via MIDI Control Change.

        :param parameter: int RPN parameter number (0–16383).
        :param value: int Parameter value (0–16383).
        :param channel: int MIDI channel (0–15).
        :return: True if messages sent successfully, False otherwise.
        """
        log.message(scope="MidiOutHandler", message="========sending rpn=========")
        if not 0 <= parameter <= 16383:
            log.message(f"Invalid RPN parameter: {parameter}. Must be 0–16383.")
            return False
        if not 0 <= value <= 16383:
            log.message(f"Invalid RPN value: {value}. Must be 0–16383.")
            return False

        # Split into MSB/LSB
        rpn_msb = (parameter >> 7) & BitMask.LOW_7_BITS
        rpn_lsb = parameter & BitMask.LOW_7_BITS
        value_msb = (value >> 7) & BitMask.LOW_7_BITS
        value_lsb = value & BitMask.LOW_7_BITS

        success = (
            self.send_control_change(101, rpn_msb, channel)
            and self.send_control_change(100, rpn_lsb, channel)  # RPN MSB
            and self.send_control_change(6, value_msb, channel)  # RPN LSB
            and self.send_control_change(  # Data Entry MSB
                38, value_lsb, channel
            )  # Data Entry LSB
        )

        if success:
            log.message(scope="MidiOutHandler", message="Success: Sent RPN")
            log.parameter(scope="MidiOutHandler", message="Param", parameter=parameter)
            log.parameter(scope="MidiOutHandler", message="Value", parameter=value)
            log.parameter(scope="MidiOutHandler", message="Channel", parameter=channel)
        else:
            log.message(scope="MidiOutHandler", message="Failed to send RPN messages.")

        return success

    def send_nrpn(
        self, parameter: int, value: int, channel: int = 0, use_14bit: bool = False
    ) -> bool:
        """
        Send a Non-Registered Parameter Number (NRPN) message via MIDI Control Change.

        :param parameter: int NRPN parameter number (0–16383).
        :param value: int Parameter value (0–16383 for 14-bit, 0–127 for 7-bit).
        :param channel: int MIDI channel (0–15).
        :param use_14bit: bool If True, send both MSB and LSB for value (14-bit). If False, send only MSB (7-bit).
        :return: True if all messages were sent successfully, False otherwise.
        """
        log.message(scope="MidiOutHandler", message="========sending nrpn=========")
        log.parameter(scope="MidiOutHandler", message="parameter", parameter=parameter)
        log.parameter(scope="MidiOutHandler", message="value", parameter=value)
        log.parameter(scope="MidiOutHandler", message="channel", parameter=channel)
        log.parameter(scope="MidiOutHandler", message="use_14bit", parameter=use_14bit)
        if not 0 <= parameter <= 16383:
            log.message(f"Invalid NRPN parameter: {parameter}. Must be 0–16383.")
            return False
        if not 0 <= value <= (16383 if use_14bit else 127):
            log.message(
                f"Invalid NRPN value: {value}. Must be 0–{16383 if use_14bit else 127}."
            )
            return False

        nrpn_msb = (parameter >> 7) & BitMask.LOW_7_BITS
        nrpn_lsb = parameter & BitMask.LOW_7_BITS
        if use_14bit:
            value_msb = (value >> 7) & BitMask.LOW_7_BITS
            value_lsb = value & BitMask.LOW_7_BITS
        else:
            value_msb = value & BitMask.LOW_7_BITS
            value_lsb = 0  # Optional; not sent anyway

        ok = True
        ok &= self.send_control_change(99, nrpn_msb, channel)  # NRPN MSB
        ok &= self.send_control_change(98, nrpn_lsb, channel)  # NRPN LSB
        ok &= self.send_control_change(6, value_msb, channel)  # Data Entry MSB
        if use_14bit:
            ok &= self.send_control_change(38, value_lsb, channel)  # Data Entry LSB

        # Optional cleanup (nulling NRPN, not required but can prevent stuck parameters)
        ok &= self.send_control_change(99, 127, channel)  # NRPN MSB null
        ok &= self.send_control_change(98, 127, channel)  # NRPN LSB null

        if ok:
            log.message(scope="MidiOutHandler", message="Sent NRPN:")
            log.parameter(
                scope="MidiOutHandler", message="parameter", parameter=parameter
            )
            log.parameter(scope="MidiOutHandler", message="value", parameter=value)
            log.parameter(scope="MidiOutHandler", message="channel", parameter=channel)
        else:
            log.message(scope="MidiOutHandler", message="Failed to send NRPN messages.")
        return ok

    def send_bank_select_and_program_change(
        self, channel: int, bank_msb: int, bank_lsb: int, program: int
    ) -> bool:
        """
        Sends Bank Select and Program Change messages with delays between messages
        to ensure the synthesizer can process them correctly.

        :param channel: int MIDI channel (1-16).
        :param bank_msb: int Bank MSB value.
        :param bank_lsb: int Bank LSB value.
        :param program: int Program number.
        :return: bool True if all messages are sent successfully, False otherwise.
        """
        try:
            import time

            from jdxi_editor.midi.sleep import MIDI_SLEEP_TIME

            log.message(
                scope="MidiOutHandler",
                message="========send_bank_select_and_program_change=========",
            )
            log.parameter(scope="MidiOutHandler", message="channel", parameter=channel)
            log.parameter(
                scope="MidiOutHandler", message="bank_msb", parameter=bank_msb
            )
            log.parameter(
                scope="MidiOutHandler", message="bank_lsb", parameter=bank_lsb
            )
            log.parameter(scope="MidiOutHandler", message="program", parameter=program)
            log.message(
                f"-------#1 send_control_change controller=0, bank_msb={bank_msb}, channel: {channel} --------"
            )
            self.send_control_change(0, bank_msb, channel)
            time.sleep(MIDI_SLEEP_TIME)  # Small delay between bank select messages

            log.message(
                f"-------#2 send_control_change controller=32, bank_lsb={bank_lsb}, channel: {channel} --------"
            )
            self.send_control_change(32, bank_lsb, channel)
            time.sleep(MIDI_SLEEP_TIME)  # Small delay before program change

            log.message(
                f"-------#3 send_program_change program: {program} channel: {channel} --------"
            )
            self.send_program_change(program, channel)
            return True
        except Exception as ex:
            log.error(
                scope="MidiOutHandler",
                message="Error {ex} occurred sending bank and program change message",
            )
            return False

    def identify_device(self) -> None:
        """
        Send Identity Request and verify response

        :return: None
        """
        request = IdentityRequestMessage()
        self.send_message(request)
        log.parameter(
            scope="MidiOutHandler",
            message="sending identity_request request message:",
            parameter=request,
        )

    def send_message(self, message: MidiMessage) -> None:
        """
        unpack the message list and send it

        :param message: MidiMessage
        :return: None
        """
        try:
            raw_message = message.to_message_list()
            self.send_raw_message(raw_message)
            log.parameter(
                scope="MidiOutHandler",
                message="Sent MIDI message:",
                parameter=raw_message,
            )
        except Exception as ex:
            log.error(
                scope="MidiOutHandler",
                message="Error sending identity_request request: {str(ex)}",
            )
