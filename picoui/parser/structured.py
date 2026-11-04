"""A generic structured parser for processing raw data into an intermediate representation.

This module provides a `StructuredParser` class for parsing raw data based on a given
layout specification and transforming the parsed data into an intermediate representation
using a builder function. It supports strict and non-strict parsing modes.

"""

from typing import Any, Callable, Generic, Iterable, TypeVar

T_Raw = TypeVar("T_Raw")     # bytes | str
T_IR = TypeVar("T_IR")       # ParsedSysExMessage | PDBLigandData


class StructuredParser(Generic[T_Raw, T_IR]):
    def __init__(
        self,
        layout: Iterable[Any],  # FieldSpec or LineSpec
        builder: Callable[[dict, T_Raw], T_IR],
        strict: bool = False,
    ):
        self.layout = layout
        self.builder = builder
        self.strict = strict

    def parse(self, raw: T_Raw) -> T_IR:
        fields = self._parse_fields(raw)
        return self.builder(fields, raw)

    def _parse_fields(self, raw: T_Raw) -> dict:
        parsed = {}
        for field in self.layout:
            try:
                parsed[field.name] = field.extract(raw)
            except Exception:
                if self.strict:
                    raise
        return parsed
