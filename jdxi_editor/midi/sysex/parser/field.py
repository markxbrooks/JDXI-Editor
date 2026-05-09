"""
Structured field parsing for JD-Xi SysEx layouts.
"""

from typing import Any, Iterable

from decologr import Decologr as log

from jdxi_editor.midi.message.sysex.offset import FieldSpec


class StructuredFieldParser:
    """Extract and parse fields declared by SysEx layout specs."""

    def __init__(
        self,
        data: bytes,
        fields: Iterable[FieldSpec],
        strict: bool = False,
    ):
        self.data = data
        self.fields = tuple(fields)
        self.strict = strict

    def extract_field_bytes(self, field: FieldSpec) -> bytes:
        data_len = len(self.data)
        start = field.normalized_offset(data_len)
        end = field.end_offset(data_len)

        if start < 0 or start >= data_len:
            raise ValueError(
                f"Field offset {field.offset} out of range for data length {data_len}"
            )
        if end > data_len:
            raise ValueError(f"Field end {end} out of range for data length {data_len}")

        return self.data[start:end]

    def parse_field(self, field: FieldSpec) -> Any:
        raw_bytes = self.extract_field_bytes(field)
        if field.validator is not None and not field.validator(raw_bytes):
            raise ValueError(
                f"Validation failed for field {field.name or '<unnamed>'}: "
                f"{raw_bytes.hex(' ')}"
            )

        if field.parser is None:
            return raw_bytes

        parser = field.parser
        if isinstance(parser, type) and hasattr(parser, "__members__"):
            try:
                byte_value = raw_bytes[0] if len(raw_bytes) == 1 else None
                if byte_value is not None:
                    for member in parser:
                        if member.value == byte_value:
                            return member
                    if self.strict:
                        raise ValueError(
                            f"No {parser.__name__} member for byte 0x{byte_value:02X}"
                        )
            except (AttributeError, IndexError) as ex:
                if self.strict:
                    raise ValueError(
                        f"Failed to parse enum field {field.name or '<unnamed>'}"
                    ) from ex

        if hasattr(parser, "from_bytes"):
            try:
                return parser.from_bytes(raw_bytes)
            except (AttributeError, ValueError, TypeError) as ex:
                if self.strict:
                    raise ValueError(
                        f"Failed to parse field {field.name or '<unnamed>'} "
                        f"from {raw_bytes.hex(' ')}"
                    ) from ex

        if parser is bytes:
            return raw_bytes

        return raw_bytes

    def parse_fields(self) -> dict:
        parsed_fields = {}

        for index, field in enumerate(self.fields):
            try:
                parsed_value = self.parse_field(field)
                field_name = field.name or f"field_{index}"
                parsed_fields[field_name] = parsed_value
            except (ValueError, IndexError) as ex:
                if self.strict:
                    raise ValueError(
                        f"Failed to parse field {field.name or f'field_{index}'} "
                        f"at offset {field.offset} with length {field.length}"
                    ) from ex
                log.debug(
                    scope="StructuredFieldParser",
                    message=f"Failed to parse field {index}: {ex}",
                )
                continue

        return parsed_fields
