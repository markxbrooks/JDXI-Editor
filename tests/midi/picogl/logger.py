"""log message"""

import json
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Optional

from picogl.project import __project__

NOW = datetime.now()
DATE_STRING = NOW.strftime("%d%b%Y")
TIME_STRING = NOW.strftime("%H-%M")

LOG_PADDING_WIDTH = 40

LOGGING = True


def setup_logging():
    """Set up logging configuration"""
    try:
        # Create logs shader_directory in user's home shader_directory
        _ = logging.getLogger(__project__)
        log_dir = Path.home() / f".{__project__}" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        # Log file path
        log_file = log_dir / f"{__project__}-{DATE_STRING}-{TIME_STRING}.log"
        print(f"Setting up logging to: {log_file}")

        # Reset root handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        # Configure rotating file logging
        file_handler = RotatingFileHandler(
            str(log_file),
            maxBytes=1024 * 1024,  # 1MB per file
            backupCount=5,  # Keep 5 backup files
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(filename)-20s| %(lineno)-5s| %(levelname)-8s| %(message)-24s"
        )
        file_handler.setFormatter(file_formatter)

        # Configure console logging
        console_handler = logging.StreamHandler(
            sys.__stdout__
        )  # Use sys.__stdout__ explicitly
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter(
            "%(filename)-20s| %(lineno)-5s| %(levelname)-8s| %(message)-24s"
        )
        console_handler.setFormatter(console_formatter)

        # Configure root logger
        logging.root.setLevel(logging.DEBUG)
        logging.root.addHandler(file_handler)
        logging.root.addHandler(console_handler)

        logger = logging.getLogger(__project__)
        logger.info("Logging setup complete")
        logger.info(f"{__project__} starting up...")
        logger.debug(f"Log file: {log_file}")
        logging.getLogger("OpenGL").setLevel(logging.WARNING)
        return logger

    except Exception as ex:
        print(f"Error setting up logging: {str(ex)}")
        raise


LEVEL_EMOJIS = {
    logging.DEBUG: "🔍",
    logging.INFO: "ℹ️",
    logging.WARNING: "⚠️",
    logging.ERROR: "❌",
    logging.CRITICAL: "💥",
}


def get_qc_tag(msg: str) -> str:
    """
    get QC emoji etc
    :param msg: str
    :return: str
    """
    msg = f"{msg}".lower()
    if "success rate" in msg:
        return "📊"
    if (
        "updat" in msg
        or "success" in msg
        or "passed" in msg
        or "Enabl" in msg
        or "Setting up" in msg
    ):
        return "✅"
    if "fail" in msg or "error" in msg:
        return "❌"
    return " "


def decorate_log_message(message: str, level: int) -> str:
    """
    Adds emoji decoration to a log message based on its content and log level.
    :param message: The original log message
    :param level: The logging level
    :return: Decorated log message string
    """

    level_emoji_tag = LEVEL_EMOJIS.get(level, "🔔")
    qc_tag = get_qc_tag(message)
    return f"{level_emoji_tag}{qc_tag}{message}"


class Logger:
    def __init__(self):
        pass

    @staticmethod
    def error(
        message: str,
        exception: Optional[Exception] = None,
        level: int = logging.ERROR,
        stacklevel: int = 4,
        silent: bool = False,
    ) -> None:
        """
        Log an error message, optionally with an exception.
        """
        if exception:
            message = f"{message}: {exception}"
        Logger.message(message, stacklevel=stacklevel, silent=silent, level=level)

    exception = error

    @staticmethod
    def warning(
        message: str,
        exception: Optional[Exception] = None,
        level: int = logging.WARNING,
        stacklevel: int = 4,
        silent: bool = False,
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
                Logger.message(
                    "Invalid JSON string provided.", level=logging.WARNING, stacklevel=3
                )
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
        stacklevel: int = 3,
        silent: bool = False,
    ) -> None:
        """
        Log a plain message with optional formatting.
        """
        full_message = decorate_log_message(message, level)
        if LOGGING and not silent:
            logging.log(level, full_message, stacklevel=stacklevel)

    debug = message
    info = message

    @staticmethod
    def parameter(
        message: str,
        parameter: Any,
        float_precision: int = 2,
        max_length: int = 300,
        level: int = logging.INFO,
        stacklevel: int = 4,
        silent: bool = False,
    ) -> None:
        """
        Log a structured message including the type and uniform_value of a parameter.
        """

        def format_value(param: Any) -> str:
            if param is None:
                return "None"
            if isinstance(param, float):
                return f"{param:.{float_precision}f}"
            if isinstance(param, list):
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
    def header_message(
        message: str,
        level: int = logging.INFO,
        silent: bool = False,
        stacklevel: int = 3,
    ) -> None:
        """
        Logs a visually distinct header message with separator lines and emojis.

        :param stacklevel: int
        :param silent: bool whether or not to write to the log
        :param message: The message to log.
        :param level: Logging level (default: logging.INFO).
        """
        full_separator = f"{'=' * 142}"
        separator = f"{'=' * 100}"

        Logger.message(
            f"\n{full_separator}", level=level, stacklevel=stacklevel, silent=silent
        )
        Logger.message(f"{message}", level=level, stacklevel=stacklevel, silent=silent)
        Logger.message(separator, level=level, stacklevel=stacklevel, silent=silent)

    @staticmethod
    def debug_info(successes: list, failures: list, stacklevel: int = 3) -> None:
        """
        Logs debug information about the parsed SysEx data.

        :param stacklevel: int - stacklevel
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

        Logger.message(
            f"Successes ({len(successes)}): {successes}", stacklevel=stacklevel
        )
        Logger.message(f"Failures ({len(failures)}): {failures}", stacklevel=stacklevel)
        Logger.message(f"Success Rate: {success_rate:.1f}%", stacklevel=stacklevel)
        Logger.message("=" * 100, stacklevel=3)
