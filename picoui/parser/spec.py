"""
This module defines dataclasses to specify configurations for argument parsers.

The module provides data structures for defining key parser specifications,
such as arguments' metadata, program descriptions, help texts, and other
configuration details that enable the creation of customizable parsers.
"""

from dataclasses import dataclass


@dataclass
class ArgParseSpec:
    """ArgParseSpec"""

    prog: str = ""
    description: str = ""
    usage: str = ""
    type = None


@dataclass
class ParserSpec:
    """Parser Spec"""

    obj: str = None
    long: str = None
    dest: str = None
    default: str = None
    choices: list = None
    help_text: str = None
    type: str = None