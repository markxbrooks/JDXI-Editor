import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from jdxi_editor.project import __package_name__, __program__, __version__


def setup_logging(log_level: int = logging.DEBUG) -> logging.Logger:
    """Set up logging configuration"""
    try:
        _ = logging.getLogger(__package_name__)
        log_dir = Path.home() / f".{__package_name__}" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f"{__package_name__}.log"
        print(f"Setting up logging to: {log_file}")

        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        file_handler = RotatingFileHandler(
            str(log_file),
            maxBytes=1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)

        file_formatter = logging.Formatter(
            "%(filename)-20s| %(lineno)-5s| %(levelname)-8s| %(message)-24s"
        )
        file_handler.setFormatter(file_formatter)

        console_handler = logging.StreamHandler(sys.__stdout__)
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(
            "%(filename)-20s| %(lineno)-5s| %(levelname)-8s| %(message)-24s"
        )
        console_handler.setFormatter(console_formatter)

        logging.root.setLevel(log_level)
        logging.root.addHandler(file_handler)
        logging.root.addHandler(console_handler)

        logger = logging.getLogger(__package_name__)
        logger.info("Logging setup complete")
        logger.info(f"{__program__} starting up...")
        logger.debug(f"Log file: {log_file}")
        handlers = [file_handler, console_handler]
        return logger

    except Exception as ex:
        print(f"Error setting up logging: {str(ex)}")
        raise
