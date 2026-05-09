"""
Orchestration service for JD-Xi SysEx parsing pipelines.
"""

from dataclasses import replace
from typing import Iterable, Optional, Type

from jdxi_editor.midi.sysex.parser.factory import (
    JDXiMessageDeduplicator,
    JDXiMessageFactory,
)
from jdxi_editor.midi.sysex.parser.model import JDXiSysExMessage, ParseResult
from picoui.parser.service import ParsingService


class JDXiSysExService(ParsingService):
    """
    Compose parser, domain factory, and optional stream deduplication.

    This keeps orchestration outside the raw parser so callers can use a single
    service entry point without re-coupling parsing to adapters or persistence.
    """

    def __init__(self, parser_cls: Optional[Type] = None, strict: bool = False):
        if parser_cls is None:
            from jdxi_editor.midi.sysex.parser.sysex import JDXiSysExParser

            parser_cls = JDXiSysExParser
        self.parser_cls = parser_cls
        self.strict = strict

    def parse(self, data: bytes) -> JDXiSysExMessage:
        parser = self.parser_cls(data, strict=self.strict)
        parsed = parser.parse_to_ir()
        return JDXiMessageFactory.from_parsed(parsed)

    def parse_result(self, data: bytes) -> ParseResult:
        parser = self.parser_cls(data, strict=self.strict)
        return parser.parse_to_result()

    def parse_stream_results(self, messages: Iterable[bytes]) -> list[ParseResult]:
        return [
            replace(self.parse_result(message), source_index=index)
            for index, message in enumerate(messages)
        ]

    def parse_stream(
        self,
        messages: Iterable[bytes],
        deduplicate: bool = True,
    ) -> list[JDXiSysExMessage]:
        parsed_messages = [
            result.message
            for result in self.parse_stream_results(messages)
            if result.success and result.message is not None
        ]
        if deduplicate:
            return JDXiMessageDeduplicator.deduplicate(parsed_messages)
        return parsed_messages
