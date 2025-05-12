import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging():
    """Set up logging configuration"""
    try:
        # Create logs directory in user's home directory
        _ = logging.getLogger("jdxi_editor")
        log_dir = Path.home() / ".jdxi_editor" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        # Log file path
        log_file = log_dir / "jdxi_editor.log"
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

        logger = logging.getLogger("jdxi_editor")
        logger.info("Logging setup complete")
        logger.info("JD-Xi Editor starting up...")
        logger.debug(f"Log file: {log_file}")
        return logger

    except Exception as ex:
        print(f"Error setting up logging: {str(ex)}")
        raise
