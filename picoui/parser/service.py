"""
A service for parsing raw input, converting it into domain-specific objects, and optionally deduplicating results.

This module provides the ParsingService class, which uses a parser and a factory
to process raw data into intermediate representations and finally into domain-specific
objects. It also includes an optional deduplication function.

Classes:

- ParsingService: Handles parsing of raw data, supports stream processing,
  and allows for optional deduplication.
"""

from typing import Callable, Generic, Iterable, TypeVar

from picoui.parser.structured import T_IR, StructuredParser, T_Raw

T_Domain = TypeVar("T_Domain")


class ParsingService(Generic[T_Raw, T_IR, T_Domain]):
    def __init__(
        self,
        parser: StructuredParser[T_Raw, T_IR],
        factory: Callable[[T_IR], T_Domain],
        deduplicator: Callable[[Iterable[T_Domain]], Iterable[T_Domain]] | None = None,
    ):
        self.parser = parser
        self.factory = factory
        self.deduplicator = deduplicator

    def parse(self, raw: T_Raw) -> T_Domain:
        ir = self.parser.parse(raw)
        return self.factory(ir)

    def parse_stream(self, raws: Iterable[T_Raw]) -> Iterable[T_Domain]:
        for raw in raws:
            yield self.parse(raw)

    def parse_stream_dedup(self, raws: Iterable[T_Raw]) -> list[T_Domain]:
        results = list(self.parse_stream(raws))
        if self.deduplicator:
            return list(self.deduplicator(results))
        return results