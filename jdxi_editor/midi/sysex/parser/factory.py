"""
Factories and adapters for parsed JD-Xi SysEx data.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, TextIO, Union

import mido
from decologr import Decologr as log

from jdxi_editor.midi.io.utils import nibble_data
from jdxi_editor.midi.message.sysex.offset import (
    JDXIControlChangeOffset,
    JDXIProgramChangeOffset,
    JDXiSysExMessageLayout,
)
from jdxi_editor.midi.sysex.parser.model import JDXiSysExMessage, ParsedSysExMessage
from picomidi.constant import Midi
from picomidi.core.bitmask import BitMask
from picomidi.message.type import MidoMessageType

MAX_SYSEX_CHUNK = 128


@dataclass(slots=True)
class JsonSysExLogSink:
    log_folder: Path

    def __call__(self, parsed: dict) -> None:
        self.log_folder.mkdir(parents=True, exist_ok=True)
        json_log_file = (
            self.log_folder / f"jdxi_tone_data_{parsed.get('ADDRESS', 'unknown')}.json"
        )
        with open(json_log_file, "w", encoding="utf-8") as file_handle:  # type: TextIO
            json.dump(parsed, file_handle, ensure_ascii=False, indent=2)


class JDXiMessageFactory:
    """Build typed JD-Xi domain messages from parsed SysEx IR."""

    @staticmethod
    def from_parsed(parsed: ParsedSysExMessage) -> JDXiSysExMessage:
        return JDXiSysExMessage(
            raw=parsed.raw,
            message_type=parsed.message_type,
            model_id=parsed.model_id,
            command_id=parsed.command_id,
            address=parsed.address,
            payload=parsed.data,
            valid_checksum=parsed.valid_checksum,
            checksum=parsed.checksum,
            tone_name=parsed.tone_name,
        )


class JDXiMessageDeduplicator:
    """Deduplicate domain messages by identity, keeping the best/latest instance."""

    @staticmethod
    def deduplicate(messages: List[JDXiSysExMessage]) -> List[JDXiSysExMessage]:
        best_by_identity: dict[str, tuple[int, JDXiSysExMessage]] = {}

        for index, message in enumerate(messages):
            current = best_by_identity.get(message.identity_key)
            if current is None or JDXiMessageDeduplicator._is_better(
                candidate=message,
                candidate_index=index,
                existing=current[1],
                existing_index=current[0],
            ):
                best_by_identity[message.identity_key] = (index, message)

        return [message for _, message in best_by_identity.values()]

    @staticmethod
    def _is_better(
        candidate: JDXiSysExMessage,
        candidate_index: int,
        existing: JDXiSysExMessage,
        existing_index: int,
    ) -> bool:
        return (candidate.quality_score, candidate_index) > (
            existing.quality_score,
            existing_index,
        )


class JDXiMessageJsonAdapter:
    """Serialize domain SysEx messages without depending on parser dictionaries."""

    @staticmethod
    def to_dict(message: JDXiSysExMessage) -> dict:
        command_id = message.command_id
        return {
            "message_type": message.message_type,
            "identity_key": message.identity_key,
            "model_id": message.model_id.hex() if message.model_id else None,
            "command_id": getattr(command_id, "name", command_id),
            "address": message.address.hex() if message.address else None,
            "payload": message.payload.hex(),
            "valid_checksum": message.valid_checksum,
            "checksum": message.checksum,
            "tone_name": message.tone_name,
        }

    @staticmethod
    def to_json(message: JDXiSysExMessage) -> str:
        return json.dumps(JDXiMessageJsonAdapter.to_dict(message), indent=2)


class MidiMessageFactory:
    """Convert raw MIDI byte content into mido transport messages."""

    @staticmethod
    def from_bytes(
        message_content: List[int],
    ) -> Optional[Union[mido.Message, List[mido.Message]]]:
        if not message_content:
            return None
        status_byte = message_content[JDXIProgramChangeOffset.STATUS_BYTE]

        try:
            if (
                status_byte == Midi.sysex.START
                and message_content[JDXiSysExMessageLayout.END] == Midi.sysex.END
            ):
                return MidiMessageFactory._sysex_from_bytes(message_content)
        except Exception as ex:
            log.error(
                scope="MidiMessageFactory", message=f"Error parsing SysEx message: {ex}"
            )

        try:
            if (
                Midi.pc.STATUS <= status_byte <= Midi.pc.MAX_STATUS
                and len(message_content) >= 2
            ):
                return MidiMessageFactory._program_change_from_bytes(message_content)
        except Exception as ex:
            log.error(
                scope="MidiMessageFactory",
                message=f"Error parsing Program Change: {ex}",
            )

        try:
            if (
                Midi.cc.STATUS <= status_byte <= Midi.cc.MAX_STATUS
                and len(message_content) >= 3
            ):
                return MidiMessageFactory._control_change_from_bytes(message_content)
        except Exception as ex:
            log.error(
                scope="MidiMessageFactory",
                message=f"Error parsing Control Change: {ex}",
            )

        log.message(
            scope="MidiMessageFactory",
            message=f"Unhandled MIDI message: {message_content}",
        )
        return None

    @staticmethod
    def _sysex_from_bytes(
        message_content: List[int],
    ) -> Union[mido.Message, List[mido.Message]]:
        sysex_data = nibble_data(
            message_content[
                JDXIProgramChangeOffset.PROGRAM_NUMBER : JDXIProgramChangeOffset.END
            ]
        )
        if len(sysex_data) > MAX_SYSEX_CHUNK:
            nibbles = [sysex_data[i : i + 4] for i in range(0, len(sysex_data), 4)]
            return [mido.Message("sysex", data=nibble) for nibble in nibbles]
        return mido.Message("sysex", data=sysex_data)

    @staticmethod
    def _program_change_from_bytes(message_content: List[int]) -> mido.Message:
        status_byte = message_content[JDXIProgramChangeOffset.STATUS_BYTE]
        channel = status_byte & BitMask.LOW_4_BITS
        program = message_content[JDXIProgramChangeOffset.PROGRAM_NUMBER]
        return mido.Message(
            MidoMessageType.PROGRAM_CHANGE.value, channel=channel, program=program
        )

    @staticmethod
    def _control_change_from_bytes(message_content: List[int]) -> mido.Message:
        status_byte = message_content[JDXIProgramChangeOffset.STATUS_BYTE]
        channel = status_byte & BitMask.LOW_4_BITS
        control = message_content[JDXIControlChangeOffset.CONTROL]
        value = message_content[JDXIControlChangeOffset.VALUE]
        return mido.Message(
            MidoMessageType.CONTROL_CHANGE.value,
            channel=channel,
            control=control,
            value=value,
        )
