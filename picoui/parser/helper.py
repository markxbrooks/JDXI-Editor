"""
This module provides functionality to create and configure ArgumentParser
instances based on provided specifications.

The module focuses on integrating custom specifications into argparse parsers.
It includes tools for adding arguments to a parser from a specification and
constructing parsers from specification objects.
"""

import argparse
from argparse import ArgumentParser

from picoui.parser.spec import ArgParseSpec, ParserSpec


def add_arg_to_parser_from_spec(parser: ArgumentParser, spec: ParserSpec) -> None:
    """Add a CLI argument to *parser* from a :class:`~picoui.parser.spec.ParserSpec`."""
    kwargs: dict = {
        "dest": spec.dest,
        "help": spec.help_text,
    }
    if spec.type is not None:
        kwargs["type"] = spec.type
    if spec.default is not None:
        kwargs["default"] = spec.default
    if spec.choices is not None:
        kwargs["choices"] = spec.choices
    parser.add_argument(spec.obj, spec.long, **kwargs)


def parser_from_arg_parse_spec(arg_parse_spec: ArgParseSpec) -> ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=arg_parse_spec.prog,
        description=arg_parse_spec.description,
        usage=arg_parse_spec.usage,
    )
    return parser