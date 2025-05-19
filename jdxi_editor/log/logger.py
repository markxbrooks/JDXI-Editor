""" log message """

import json
import logging
from typing import Optional, Any

from jdxi_editor.globals import LOG_PADDING_WIDTH, LOGGING
from jdxi_editor.log.decorator import decorate_log_message


def format_midi_message_to_hex_string(message):
    """hexlify message"""
    formatted_message = " ".join([hex(x)[2:].upper().zfill(2) for x in message])
    return formatted_message


class Logger:
    def __init__(self):
        pass

    @staticmethod
    def error(
        message: str,
        exception: Optional[Exception] = None,
        level: int = logging.ERROR,
        stacklevel: int = 2,
        silent: bool = False
    ) -> None:
        """
        Log an error message, optionally with an exception.
        """
        if exception:
            message = f"{message}: {exception}"
        Logger.message(message, stacklevel=stacklevel, silent=silent, level=level)

    @staticmethod
    def warning(
        message: str,
        exception: Optional[Exception] = None,
        level: int = logging.WARNING,
        stacklevel: int = 3,
        silent: bool = False
    ) -> None:
        """
        Log an error message, optionally with an exception.
        """
        if exception:
            message = f"{message}: {exception}"
        Logger.message(message, stacklevel=stacklevel, silent=silent, level=level)

    @staticmethod
    def json(data: Any, silent: bool = False) -> None:
        """
        Log a JSON object or JSON string as a single compact line.
        """
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                Logger.message("Invalid JSON string provided.", level=logging.WARNING, stacklevel=3)
                return

        try:
            compact_json = json.dumps(data, separators=(",", ":"))
        except (TypeError, ValueError) as e:
            Logger.error("Failed to serialize JSON", e)
            return

        if not silent:
            Logger.message(compact_json, stacklevel=3)

    @staticmethod
    def message(
        message: str,
        level: int = logging.INFO,
        stacklevel: int = 2,
        silent: bool = False
    ) -> None:
        """
        Log a plain message with optional formatting.
        """
        full_message = decorate_log_message(message, level)
        if LOGGING and not silent:
            logging.log(level, full_message, stacklevel=stacklevel)

    @staticmethod
    def parameter(
        message: str,
        parameter: Any,
        float_precision: int = 2,
        max_length: int = 300,
        level: int = logging.INFO,
        stacklevel: int = 3,
        silent: bool = False
    ) -> None:
        """
        Log a structured message including the type and value of a parameter.
        """

        def format_value(param: Any) -> str:
            if param is None:
                return "None"
            if isinstance(param, float):
                return f"{param:.{float_precision}f}"
            if isinstance(param, list):
                try:
                    return format_midi_message_to_hex_string(param)
                except TypeError:
                    return ", ".join(str(item) for item in param)
            if isinstance(param, dict):
                return ", ".join(f"{k}={v}" for k, v in param.items())
            if isinstance(param, (bytes, bytearray)):
                return " ".join(f"0x{b:02X}" for b in param)
            return str(param)

        type_name = type(parameter).__name__
        formatted_value = format_value(parameter)

        if len(formatted_value) > max_length:
            formatted_value = formatted_value[: max_length - 3] + "..."

        padded_message = f"{message:<{LOG_PADDING_WIDTH}}"
        padded_type = f"{type_name:<12}"
        final_message = f"{padded_message} {padded_type} {formatted_value}".rstrip()
        Logger.message(final_message, silent=silent, stacklevel=stacklevel, level=level)

    @staticmethod
    def header_message(message: str, level: int = logging.INFO, silent: bool = False, stacklevel: int = 3) -> None:
        """
        Logs a visually distinct header message with separator lines and emojis.

        :param silent: bool whether or not to write to the log
        :param message: The message to log.
        :param level: Logging level (default: logging.INFO).
        """
        full_separator = f"{'=' * 142}"
        separator = f"{'=' * 100}"

        Logger.message(f"\n{full_separator}", level=level, stacklevel=stacklevel, silent=silent)
        Logger.message(f"{message}", level=level, stacklevel=stacklevel, silent=silent)
        Logger.message(separator, level=level, stacklevel=stacklevel, silent=silent)

    @staticmethod
    def debug_info(successes: list, failures: list, stacklevel=3) -> None:
        """
        Logs debug information about the parsed SysEx data.

        :param successes: list – Parameters successfully decoded.
        :param failures: list – Parameters that failed decoding.
        """
        for listing in [successes, failures]:
            try:
                listing.remove("SYNTH_TONE")
            except ValueError:
                pass  # or handle the error

        total = len(successes) + len(failures)
        success_rate = (len(successes) / total * 100) if total else 0.0

        Logger.message(f"Successes ({len(successes)}): {successes}", stacklevel=stacklevel)
        Logger.message(f"Failures ({len(failures)}): {failures}", stacklevel=stacklevel)
        Logger.message(f"Success Rate: {success_rate:.1f}%", stacklevel=stacklevel)
        Logger.message("=" * 100, stacklevel=3)
