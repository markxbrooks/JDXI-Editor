"""
Provides tools and utilities for logging setup and message management with
additional decorations and level-specific configurations.

This module includes methods for cleaning up logging handlers, setting up a
rotating file and console-based logging setup, and managing log levels
dynamically. It also provides helper functions to manipulate and decorate log
messages, format JSON objects, and generate QC-specific emojis for logs.

Functions:
    cleanup_logging(logger): Ensures logging handlers are cleaned up properly.
    setup_logging(verbose, project_name): Sets up comprehensive logging to both file and console.
    decorate_log_message(message, level, decorate): Adds decorations to log messages.
    get_qc_tag(msg): Generates QC emojis based on message content.

Example Usage:
==============
>>> from decologr import Decologr, set_project_name, setup_logging

>>> # Set project name (optional, defaults to "decologr")
>>> set_project_name("myproject")
>>> # Setup logging (optional)
>>> setup_logging(verbose=True, project_name="myproject") # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
╭─────────── myproject ────────────╮
│  myproject Application Starting  │
╰──────────────────────────────────╯
[...] INFO     ℹ️ myproject starting up with log file
                             .../.myproject/logs/myproject-...
<Logger myproject (INFO)>
>>> # Use Logger
>>> Decologr.info("Hello, world!") # doctest: +NORMALIZE_WHITESPACE
                    INFO     ℹ️ Hello, world!
>>> Decologr.error("Something went wrong", exception=ValueError("test")) # doctest: +NORMALIZE_WHITESPACE
❌ Something went wrong
ValueError: test
>>> Decologr.json({"key": "value"})# doctest: +NORMALIZE_WHITESPACE
{
  "key": "value"
}
"""

import json
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Optional

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.json import JSON as RichJSON
    from rich.table import Table
    from rich.tree import Tree
    from rich.traceback import Traceback
    from rich.panel import Panel
    from rich.console import Console as RichConsole
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    RichHandler = None
    Console = None
    RichJSON = None
    Table = None
    Tree = None
    Traceback = None
    Panel = None
    RichConsole = None

NOW = datetime.now()
DATE_STRING = NOW.strftime("%d%b%Y")
TIME_STRING = NOW.strftime("%H-%M")

LOG_PADDING_WIDTH = 40

LOGGING = True

# Default project name - can be overridden
_DEFAULT_PROJECT_NAME = "decologr"


class _RichFileHandler(RotatingFileHandler):
    """
    Custom file handler that writes Rich-formatted output to log files.
    
    This allows log files to contain Rich markup which can be viewed
    with Rich-enabled viewers like the Textual log viewer.
    """
    
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
        """Initialize the Rich file handler."""
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        # Create a standard formatter to match RichHandler console output format
        # RichHandler format: [HH:MM:SS] LEVEL     message
        # We'll match this structure for consistency
        self.formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s %(message)s",
            datefmt="%H:%M:%S"
        )
        if HAS_RICH:
            # Create a Console that writes to the file
            self.console = RichConsole(
                file=self.stream,
                width=None,  # No width limit for files
                force_terminal=False,  # Don't force terminal features
                no_color=False,  # Keep colors/markup in file
                markup=True,  # Enable markup
                highlight=False,  # Disable syntax highlighting for performance
            )
        else:
            self.console = None
    
    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record with Rich formatting.
        """
        try:
            if HAS_RICH and self.console:
                # First format using the standard formatter to get exact format
                base_formatted = self.formatter.format(record)
                
                # Get color for level
                level_color = LEVEL_COLORS.get(record.levelno, "white")
                
                # Wrap the entire line with color markup
                # This preserves the exact format while adding Rich colors
                formatted = f"[{level_color}]{base_formatted}[/{level_color}]"
                
                # Write to file using Rich console (preserves markup)
                self.console.print(formatted, markup=True, end="\n")
            else:
                # Fallback to standard formatting
                msg = self.format(record)
                self.stream.write(msg + self.terminator)
                self.flush()
        except Exception:
            self.handleError(record)


def cleanup_logging(logger: logging.Logger) -> None:
    """Clean up logging handlers to prevent resource warnings."""
    for handler in Decologr.handlers:
        handler.close()
    Decologr.handlers.clear()


def setup_logging(
    verbose: bool = False,
    project_name: str = _DEFAULT_PROJECT_NAME,
    use_rich: Optional[bool] = None,
) -> object:
    """Set up logging configuration
    
    Args:
        verbose: Whether to enable verbose logging
        project_name: Name of the project for logging (default: "decologr")
        use_rich: Whether to use Rich formatting for console output.
                 If None, will use Rich if available, otherwise fallback to plain.
                 If True and Rich is not available, will raise ImportError.
    
    Returns:
        Logger instance
    """
    try:
        # Create logs directory in user's home directory
        _ = logging.getLogger(project_name)
        log_dir = Path.home() / f".{project_name}" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        # Log file path - use dynamic timestamp to ensure atomic file creation
        # Format: projectname-DDMonYYYY-HH-MM-SS.log
        now = datetime.now()
        date_string = now.strftime("%d%b%Y")
        time_string = now.strftime("%H-%M-%S")  # Added seconds for atomic file creation
        log_file = log_dir / f"{project_name}-{date_string}-{time_string}.log"

        # Reset root handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        # Determine if we should use Rich (needed for file handler too)
        should_use_rich = False
        if use_rich is True:
            if not HAS_RICH:
                raise ImportError(
                    "Rich is requested but not installed. Install with: pip install decologr[rich]"
                )
            should_use_rich = True
        elif use_rich is None:
            # Auto-detect: use Rich if available
            should_use_rich = HAS_RICH

        # Configure rotating file logging
        # Use Rich formatting if available, otherwise plain text
        if should_use_rich and HAS_RICH:
            # Create Rich file handler that writes formatted output to file
            file_handler = _RichFileHandler(
                str(log_file),
                maxBytes=1024 * 1024,  # 1MB per file
                backupCount=5,  # Keep 5 backup wrappers
                encoding="utf-8",
            )
        else:
            # Plain text file handler
            file_handler = RotatingFileHandler(
                str(log_file),
                maxBytes=1024 * 1024,  # 1MB per file
                backupCount=5,  # Keep 5 backup wrappers
                encoding="utf-8",
            )
            file_formatter = logging.Formatter(
                "[%(asctime)s] %(levelname)-8s %(message)s",
                datefmt="%H:%M:%S"
            )
            file_handler.setFormatter(file_formatter)
        
        file_handler.setLevel(logging.INFO)

        # Configure console logging
        if should_use_rich and HAS_RICH:
            # Use Rich handler for console output
            console_handler = RichHandler(
                console=Console(stderr=False),
                show_path=False,
                rich_tracebacks=True,
                tracebacks_show_locals=False,
                markup=True,
                show_time=True,
                show_level=True,
            )
            console_handler.setLevel(logging.INFO)
        else:
            # Fallback to standard console handler
            console_handler = logging.StreamHandler(
                sys.__stdout__
            )  # Use sys.__stdout__ explicitly
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                "%(filename)-20s| %(lineno)-5s| %(levelname)-8s| %(message)-24s"
            )
            console_handler.setFormatter(console_formatter)

        # Configure root logger
        logging.root.setLevel(logging.INFO)
        logging.root.addHandler(file_handler)
        logging.root.addHandler(console_handler)

        logger = logging.getLogger(project_name)
        
        # Set the global project name for Decologr methods
        global _project_name
        _project_name = project_name
        
        # Display startup header
        startup_message = f"{project_name} Application Starting"
        Decologr.header_message(
            startup_message,
            level=logging.INFO,
            use_rich=should_use_rich if HAS_RICH else False,
            title=f"[bold cyan]{project_name}[/bold cyan]",
        )
        
        Decologr.info(f"{project_name} starting up with log file {log_file}...")
        logging.getLogger("OpenGL").setLevel(logging.WARNING)
        return logger

    except Exception as ex:
        print(f"Error setting up logging: {str(ex)}")
        raise


def _restore_log_level_from_settings(project_name: str = _DEFAULT_PROJECT_NAME):
    """Restore log level from saved preferences at startup."""
    try:
        from PySide6.QtCore import QSettings

        # Load saved log level from settings
        settings = QSettings("elmo", "preferences")
        saved_level = settings.value("log_level", None, type=str)

        if saved_level:
            # Apply the saved log level using the same comprehensive method
            _apply_log_level_comprehensive(saved_level, project_name)
            print(f"🔧 Restored log level from preferences: {saved_level}")
        else:
            print("🔧 No saved log level found, using default INFO level")

    except Exception as ex:
        print(f"⚠️ Could not restore log level from settings: {ex}")


def _apply_log_level_comprehensive(level_name: str, project_name: str = _DEFAULT_PROJECT_NAME):
    """Apply the specified log level to all loggers and handlers (comprehensive version)."""
    try:
        numeric_level = getattr(logging, level_name.upper(), logging.CRITICAL)

        # Set root logger level
        root_logger = logging.getLogger()
        root_Decologr.setLevel(numeric_level)

        # Set all handler levels to match
        for handler in root_Decologr.handlers:
            handler.setLevel(numeric_level)

        # Set ALL existing loggers to the new level
        for logger_name in logging.Decologr.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            Decologr.setLevel(numeric_level)

        # Set project-specific logger level
        project_logger = logging.getLogger(project_name)
        project_Decologr.setLevel(numeric_level)

        # Set OpenGL logger level
        opengl_logger = logging.getLogger("OpenGL")
        opengl_Decologr.setLevel(numeric_level)

    except Exception as ex:
        print(f"⚠️ Error applying log level {level_name}: {ex}")


LEVEL_EMOJIS = {
    logging.DEBUG: "🔍",
    logging.INFO: "ℹ️",
    logging.WARNING: "⚠️",
    logging.ERROR: "❌",
    logging.CRITICAL: "💥",
}

# Rich color mapping for log levels
LEVEL_COLORS = {
    logging.DEBUG: "dim white",
    logging.INFO: "blue",
    logging.WARNING: "yellow",
    logging.ERROR: "red",
    logging.CRITICAL: "bold red on white",
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


def decorate_log_message(message: str, level: int, decorate: bool = False, use_rich_colors: bool = False) -> str:
    """
    Adds emoji decoration to a log message based on its content and log level.
    Optionally adds Rich color markup when Rich is available.

    :param message: The original log message
    :param level: The logging level
    :param decorate: Whether to decorate the message or not
    :param use_rich_colors: Whether to add Rich color markup (requires Rich to be installed)
    :return: Decorated log message string
    """
    if not decorate:
        return message
    if message.startswith("{") or message.startswith(
        "["
    ):  # JSON shouldn't be decorated
        return message
    
    level_emoji_tag = LEVEL_EMOJIS.get(level, "🔔")
    qc_tag = get_qc_tag(message)
    decorated_message = f"{level_emoji_tag}{qc_tag}{message}"
    
    # Add Rich color markup if requested and Rich is available
    if use_rich_colors and HAS_RICH:
        color = LEVEL_COLORS.get(level, "white")
        decorated_message = f"[{color}]{decorated_message}[/{color}]"
    
    return decorated_message


# Module-level variable to store the project name
# Can be set by calling set_project_name() or accessed directly
_project_name = _DEFAULT_PROJECT_NAME


def _is_rich_handler_available() -> bool:
    """
    Check if Rich handler is currently being used for logging.
    
    Returns:
        True if RichHandler is available and in use, False otherwise
    """
    if not HAS_RICH:
        return False
    
    logger = logging.getLogger(_project_name)
    # Check if any handler is a RichHandler
    for handler in logger.handlers:
        if isinstance(handler, RichHandler):
            return True
    # Also check root logger handlers
    for handler in logging.root.handlers:
        if isinstance(handler, RichHandler):
            return True
    return False


def set_project_name(project_name: str) -> None:
    """Set the project name used by Logger for logging.
    
    Args:
        project_name: Name of the project (e.g., "mxlib", "mxpandda")
    """
    global _project_name
    _project_name = project_name


def get_project_name() -> str:
    """Get the current project name used by Decologr.
    
    Returns:
        Current project name
    """
    return _project_name


class Decologr:
    """Decologr is a simple logging utility that provides additional features and convenience methods."""
    def __init__(self):
        pass

    @staticmethod
    def error(
        message: str,
        *args,
        exception: Optional[Exception] = None,
        level: int = logging.ERROR,
        stacklevel: int = 4,
        silent: bool = False,
        use_rich_traceback: Optional[bool] = None,
    ) -> None:
        """
        Log an error message, optionally with an exception, and support lazy formatting.
        
        Args:
            message: Error message
            *args: Format arguments for message
            exception: Optional exception to log
            level: Logging level (default: ERROR)
            stacklevel: Stack level for logging
            silent: If True, don't output anything
            use_rich_traceback: If True, use Rich traceback formatting (when Rich is available).
                               If None, auto-detect (uses Rich if available).
                               If False, use standard traceback formatting.
        """
        if silent:
            return

        # Determine if we should use Rich traceback
        use_rich = False
        if exception is not None and HAS_RICH and Traceback is not None:
            if use_rich_traceback is None:
                # Auto-detect: use Rich if RichHandler is available
                use_rich = _is_rich_handler_available()
            elif use_rich_traceback is True:
                use_rich = True

        if exception is not None and use_rich:
            # Use Rich traceback for beautiful exception display
            try:
                console = Console(stderr=False)
                
                # Format message with args if provided
                if args:
                    try:
                        formatted_message = message % args
                    except Exception:
                        formatted_message = message
                else:
                    formatted_message = message
                
                # Print error message in red
                console.print(f"[bold red]❌ {formatted_message}[/bold red]")
                
                # Print Rich traceback
                traceback = Traceback.from_exception(
                    type(exception),
                    exception,
                    exception.__traceback__,
                    show_locals=False,  # Don't show local variables by default
                )
                console.print(traceback)
                
                # Also log compact version to file handlers
                # Format exception info for file logging
                exc_info = f"({exception.__class__.__name__}: {exception})"
                file_message = f"{formatted_message} {exc_info}"
                
                # Temporarily remove console handlers, log, then restore
                logger = logging.getLogger(_project_name)
                root_logger = logging.root
                
                console_handlers = []
                for handler in list(logger.handlers):
                    if isinstance(handler, (RichHandler, logging.StreamHandler)):
                        console_handlers.append((handler, logger))
                        logger.removeHandler(handler)
                for handler in list(root_logger.handlers):
                    if isinstance(handler, (RichHandler, logging.StreamHandler)):
                        if not any(h == handler for h, _ in console_handlers):
                            console_handlers.append((handler, root_logger))
                            root_logger.removeHandler(handler)
                
                # Log to file handlers
                Decologr.message(file_message, stacklevel=stacklevel, silent=False, level=level)
                
                # Restore console handlers
                for handler, source_logger in console_handlers:
                    source_logger.addHandler(handler)
                
                return
                
            except Exception as e:
                # Fallback to standard formatting if Rich traceback fails
                Decologr.warning(f"Rich traceback formatting failed, using standard format: {e}", stacklevel=stacklevel)
        
        # Standard formatting (fallback or when Rich not available)
        if exception is not None:
            # Append the exception AFTER the message but do NOT disturb printf args
            # Example:
            #   message="could not open %s"
            #   => "could not open %s (ValueError: bad)"
            message = f"{message} ({exception.__class__.__name__}: {exception})"

        Decologr.message(
            message,
            *args,
            stacklevel=stacklevel,
            silent=silent,
            level=level,
        )

    exception = error

    @staticmethod
    def warning(
        message: str,
        *args,
        exception: Optional[Exception] = None,
        level: int = logging.WARNING,
        stacklevel: int = 4,
        silent: bool = False,
        use_rich_traceback: Optional[bool] = None,
    ) -> None:
        """
        Log a warning message, optionally with an exception, and support lazy formatting.
        
        Args:
            message: Warning message
            *args: Format arguments for message
            exception: Optional exception to log
            level: Logging level (default: WARNING)
            stacklevel: Stack level for logging
            silent: If True, don't output anything
            use_rich_traceback: If True, use Rich traceback formatting (when Rich is available).
                               If None, auto-detect (uses Rich if available).
                               If False, use standard traceback formatting.
        """
        if silent:
            return

        # Determine if we should use Rich traceback
        use_rich = False
        if exception is not None and HAS_RICH and Traceback is not None:
            if use_rich_traceback is None:
                # Auto-detect: use Rich if RichHandler is available
                use_rich = _is_rich_handler_available()
            elif use_rich_traceback is True:
                use_rich = True

        if exception is not None and use_rich:
            # Use Rich traceback for beautiful exception display
            try:
                console = Console(stderr=False)
                
                # Format message with args if provided
                if args:
                    try:
                        formatted_message = message % args
                    except Exception:
                        formatted_message = message
                else:
                    formatted_message = message
                
                # Print warning message in yellow
                console.print(f"[bold yellow]⚠️  {formatted_message}[/bold yellow]")
                
                # Print Rich traceback
                traceback = Traceback.from_exception(
                    type(exception),
                    exception,
                    exception.__traceback__,
                    show_locals=False,  # Don't show local variables by default
                )
                console.print(traceback)
                
                # Also log compact version to file handlers
                exc_info = f"({exception.__class__.__name__}: {exception})"
                file_message = f"{formatted_message} {exc_info}"
                
                # Temporarily remove console handlers, log, then restore
                logger = logging.getLogger(_project_name)
                root_logger = logging.root
                
                console_handlers = []
                for handler in list(logger.handlers):
                    if isinstance(handler, (RichHandler, logging.StreamHandler)):
                        console_handlers.append((handler, logger))
                        logger.removeHandler(handler)
                for handler in list(root_logger.handlers):
                    if isinstance(handler, (RichHandler, logging.StreamHandler)):
                        if not any(h == handler for h, _ in console_handlers):
                            console_handlers.append((handler, root_logger))
                            root_logger.removeHandler(handler)
                
                # Log to file handlers
                Decologr.message(file_message, stacklevel=stacklevel, silent=False, level=level)
                
                # Restore console handlers
                for handler, source_logger in console_handlers:
                    source_logger.addHandler(handler)
                
                return
                
            except Exception as e:
                # Fallback to standard formatting if Rich traceback fails
                Decologr.warning(f"Rich traceback formatting failed, using standard format: {e}", stacklevel=stacklevel)
        
        # Standard formatting (fallback or when Rich not available)
        if exception is not None:
            # Append the exception AFTER the message but do NOT disturb printf args
            message = f"{message} ({exception.__class__.__name__}: {exception})"

        Decologr.message(
            message,
            *args,
            stacklevel=stacklevel,
            silent=silent,
            level=level,
        )

    @staticmethod
    def json(data: Any, silent: bool = False, pretty: Optional[bool] = None) -> None:
        """
        Log a JSON object or JSON string with optional Rich formatting.
        
        Args:
            data: JSON-serializable object or JSON string
            silent: If True, don't output anything
            pretty: If True, use Rich pretty-printing (when Rich is available).
                   If None, auto-detect (pretty when Rich is available).
                   If False, use compact JSON format.
        
        When Rich is available and pretty=True:
            - Console output: Pretty-printed, syntax-highlighted JSON
            - File output: Compact JSON (for log files)
        
        When Rich is not available or pretty=False:
            - Both console and file: Compact JSON
        """
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                Decologr.message(
                    "Invalid JSON string provided.", level=logging.WARNING, stacklevel=3
                )
                return

        if silent:
            return

        # Determine if we should use Rich pretty-printing
        use_rich_json = False
        if HAS_RICH and RichJSON is not None:
            # Check if RichHandler is being used
            logger = logging.getLogger(_project_name)
            has_rich_handler = False
            for handler in logger.handlers:
                if isinstance(handler, RichHandler):
                    has_rich_handler = True
                    break
            if not has_rich_handler:
                for handler in logging.root.handlers:
                    if isinstance(handler, RichHandler):
                        has_rich_handler = True
                        break
            
            # Use Rich JSON if RichHandler is available and pretty is not False
            if has_rich_handler:
                if pretty is None:
                    # Auto-detect: use Rich pretty-printing
                    use_rich_json = True
                elif pretty is True:
                    use_rich_json = True

        # Serialize to compact JSON for file logging
        try:
            compact_json = json.dumps(data, separators=(",", ":"))
        except (TypeError, ValueError) as e:
            Decologr.error("Failed to serialize JSON", exception=e)
            return

        if use_rich_json:
            # Use Rich JSON for console output (pretty-printed, syntax-highlighted)
            try:
                rich_json = RichJSON.from_data(data)
                console = Console(stderr=False)
                console.print(rich_json)
                
                # Log compact JSON only to file handlers (not console)
                # Temporarily remove console handlers, log, then restore
                logger = logging.getLogger(_project_name)
                root_logger = logging.root
                
                # Collect console handlers with their source logger
                console_handlers = []  # List of (handler, logger) tuples
                for handler in list(logger.handlers):
                    if isinstance(handler, (RichHandler, logging.StreamHandler)):
                        console_handlers.append((handler, logger))
                        logger.removeHandler(handler)
                for handler in list(root_logger.handlers):
                    if isinstance(handler, (RichHandler, logging.StreamHandler)):
                        # Check if we already have this handler
                        if not any(h == handler for h, _ in console_handlers):
                            console_handlers.append((handler, root_logger))
                            root_logger.removeHandler(handler)
                
                # Log compact JSON (will only go to file handlers now)
                Decologr.message(compact_json, stacklevel=3)
                
                # Restore console handlers to their original loggers
                for handler, source_logger in console_handlers:
                    source_logger.addHandler(handler)
                        
            except Exception as e:
                # Fallback to compact JSON if Rich JSON fails
                Decologr.warning(f"Rich JSON formatting failed, using compact format: {e}", stacklevel=3)
                Decologr.message(compact_json, stacklevel=3)
        else:
            # Log compact JSON (will go to both file and console)
            Decologr.message(compact_json, stacklevel=3)

    @staticmethod
    def message(
        format_string: str,
        *args,
        level: int = logging.INFO,
        stacklevel: int = 3,
        silent: bool = False,
    ) -> None:

        if args:
            # --- Only perform printf-formatting when args provided
            try:
                formatted_message = format_string % args
            except Exception as ex:
                formatted_message = f"{format_string}  [formatting failed: {ex}]"
        else:
            formatted_message = format_string

        # Check if Rich handler is being used
        use_rich_colors = False
        if HAS_RICH:
            logger = logging.getLogger(_project_name)
            # Check if any handler is a RichHandler
            for handler in logger.handlers:
                if isinstance(handler, RichHandler):
                    use_rich_colors = True
                    break
            # Also check root logger handlers
            if not use_rich_colors:
                for handler in logging.root.handlers:
                    if isinstance(handler, RichHandler):
                        use_rich_colors = True
                        break

        full_message = decorate_log_message(formatted_message, level, decorate=True, use_rich_colors=use_rich_colors)
        if LOGGING and not silent:
            logger = logging.getLogger(_project_name)
            try:
                logger.log(level, full_message, stacklevel=stacklevel)
            except Exception as ex:
                print(f"Error logging message: {ex}") # Maybe another process got there first

    debug = message
    info = message
    
    @staticmethod
    def critical(
        message: str,
        *args,
        exception: Optional[Exception] = None,
        level: int = logging.CRITICAL,
        stacklevel: int = 4,
        silent: bool = False,
        use_rich_traceback: Optional[bool] = None,
    ) -> None:
        """
        Log a critical message, optionally with an exception, and support lazy formatting.
        
        Args:
            message: Critical message
            *args: Format arguments for message
            exception: Optional exception to log
            level: Logging level (default: CRITICAL)
            stacklevel: Stack level for logging
            silent: If True, don't output anything
            use_rich_traceback: If True, use Rich traceback formatting (when Rich is available).
                               If None, auto-detect (uses Rich if available).
                               If False, use standard traceback formatting.
        """
        if silent:
            return

        # Determine if we should use Rich traceback
        use_rich = False
        if exception is not None and HAS_RICH and Traceback is not None:
            if use_rich_traceback is None:
                # Auto-detect: use Rich if RichHandler is available
                use_rich = _is_rich_handler_available()
            elif use_rich_traceback is True:
                use_rich = True

        if exception is not None and use_rich:
            # Use Rich traceback for beautiful exception display
            try:
                console = Console(stderr=False)
                
                # Format message with args if provided
                if args:
                    try:
                        formatted_message = message % args
                    except Exception:
                        formatted_message = message
                else:
                    formatted_message = message
                
                # Print critical message in bold red
                console.print(f"[bold red on white]💥 {formatted_message}[/bold red on white]")
                
                # Print Rich traceback
                traceback = Traceback.from_exception(
                    type(exception),
                    exception,
                    exception.__traceback__,
                    show_locals=False,  # Don't show local variables by default
                )
                console.print(traceback)
                
                # Also log compact version to file handlers
                exc_info = f"({exception.__class__.__name__}: {exception})"
                file_message = f"{formatted_message} {exc_info}"
                
                # Temporarily remove console handlers, log, then restore
                logger = logging.getLogger(_project_name)
                root_logger = logging.root
                
                console_handlers = []
                for handler in list(logger.handlers):
                    if isinstance(handler, (RichHandler, logging.StreamHandler)):
                        console_handlers.append((handler, logger))
                        logger.removeHandler(handler)
                for handler in list(root_logger.handlers):
                    if isinstance(handler, (RichHandler, logging.StreamHandler)):
                        if not any(h == handler for h, _ in console_handlers):
                            console_handlers.append((handler, root_logger))
                            root_logger.removeHandler(handler)
                
                # Log to file handlers
                Decologr.message(file_message, stacklevel=stacklevel, silent=False, level=level)
                
                # Restore console handlers
                for handler, source_logger in console_handlers:
                    source_logger.addHandler(handler)
                
                return
                
            except Exception as e:
                # Fallback to standard formatting if Rich traceback fails
                Decologr.warning(f"Rich traceback formatting failed, using standard format: {e}", stacklevel=stacklevel)
        
        # Standard formatting (fallback or when Rich not available)
        if exception is not None:
            # Append the exception AFTER the message but do NOT disturb printf args
            message = f"{message} ({exception.__class__.__name__}: {exception})"

        Decologr.message(
            message,
            *args,
            stacklevel=stacklevel,
            silent=silent,
            level=level,
        )

    @staticmethod
    def parameter(
        message: str,
        parameter: Any,
        float_precision: int = 2,
        max_length: int = 300,
        level: int = logging.INFO,
        stacklevel: int = 4,
        silent: bool = False,
        use_rich: Optional[bool] = None,
    ) -> None:
        """
        Log a structured message including type and a summarized value of a parameter.
        Fast for large collections, arrays, enums, and dicts.
        
        Args:
            message: Label/description for the parameter
            parameter: The parameter value to log
            float_precision: Number of decimal places for floats
            max_length: Maximum length for text representation (fallback mode)
            level: Logging level
            stacklevel: Stack level for logging
            silent: If True, don't output anything
            use_rich: If True, use Rich tables/trees (when Rich is available).
                     If None, auto-detect (uses Rich if available).
                     If False, use text-based formatting.
        """

        if silent:
            return

        # Determine if we should use Rich formatting
        use_rich_formatting = False
        if HAS_RICH and (use_rich is None or use_rich is True):
            use_rich_formatting = _is_rich_handler_available()
            if use_rich is False:
                use_rich_formatting = False

        # Use Rich formatting for dictionaries and nested structures
        if use_rich_formatting and HAS_RICH:
            try:
                if isinstance(parameter, dict):
                    # Use Rich Table for dictionaries
                    table = Table(title=message, show_header=True, header_style="bold cyan")
                    table.add_column("Key", style="cyan", no_wrap=False)
                    table.add_column("Value", style="green", no_wrap=False)
                    
                    for key, value in parameter.items():
                        # Format value for display
                        value_str = Decologr._format_parameter_value(value, float_precision, max_length)
                        table.add_row(str(key), value_str)
                    
                    console = Console(stderr=False)
                    console.print(table)
                    
                    # Also log compact version to file handlers
                    Decologr._log_parameter_to_file(message, parameter, type(parameter).__name__, 
                                                   float_precision, max_length, level, stacklevel)
                    return
                
                elif isinstance(parameter, (list, tuple)) and len(parameter) > 0:
                    # Use Rich Tree for lists/tuples (especially nested ones)
                    tree = Tree(f"[bold cyan]{message}[/bold cyan] [dim]({type(parameter).__name__}, len={len(parameter)})[/dim]")
                    
                    # Check if items are complex (dicts, lists, etc.)
                    has_complex_items = any(isinstance(item, (dict, list, tuple)) for item in parameter[:10])
                    
                    if has_complex_items:
                        # Use tree structure for complex items
                        for i, item in enumerate(parameter[:20]):  # Limit to 20 items
                            if isinstance(item, dict):
                                item_branch = tree.add(f"[cyan]Item {i}[/cyan]")
                                for k, v in list(item.items())[:5]:  # Limit nested dict items
                                    value_str = Decologr._format_parameter_value(v, float_precision, max_length)
                                    item_branch.add(f"[yellow]{k}[/yellow]: {value_str}")
                            elif isinstance(item, (list, tuple)):
                                item_branch = tree.add(f"[cyan]Item {i}[/cyan] [dim]({type(item).__name__}, len={len(item)})[/dim]")
                                for j, subitem in enumerate(item[:5]):  # Limit nested list items
                                    value_str = Decologr._format_parameter_value(subitem, float_precision, max_length)
                                    item_branch.add(f"[green]{j}[/green]: {value_str}")
                            else:
                                value_str = Decologr._format_parameter_value(item, float_precision, max_length)
                                tree.add(f"[green]{i}[/green]: {value_str}")
                        
                        if len(parameter) > 20:
                            tree.add(f"[dim]... and {len(parameter) - 20} more items[/dim]")
                    else:
                        # Simple list - show as table-like structure
                        for i, item in enumerate(parameter[:50]):  # Limit to 50 items
                            value_str = Decologr._format_parameter_value(item, float_precision, max_length)
                            tree.add(f"[green]{i}[/green]: {value_str}")
                        if len(parameter) > 50:
                            tree.add(f"[dim]... and {len(parameter) - 50} more items[/dim]")
                    
                    console = Console(stderr=False)
                    console.print(tree)
                    
                    # Also log compact version to file handlers
                    Decologr._log_parameter_to_file(message, parameter, type(parameter).__name__,
                                                   float_precision, max_length, level, stacklevel)
                    return
                    
            except Exception as e:
                # Fallback to text-based formatting if Rich fails
                Decologr.warning(f"Rich parameter formatting failed, using text format: {e}", stacklevel=stacklevel)
                use_rich_formatting = False

        # Fallback to text-based formatting
        def format_value(param: Any) -> str:
            if param is None:
                return "None"

            # Handle enums (use .name if available, fallback to value)
            try:
                import enum

                if isinstance(param, enum.Enum):
                    return param.name
            except ImportError:
                pass

            # Float formatting
            if isinstance(param, float):
                return f"{param:.{float_precision}f}"

            # List / tuple
            if isinstance(param, (list, tuple)):
                n = len(param)
                if n > 5:
                    preview = ", ".join(str(item) for item in param[:5])
                    return f"{type(param).__name__}[len={n}, preview=[{preview}, ...]]"
                return str(param)

            # Dictionary
            if isinstance(param, dict):
                items = list(param.items())
                n = len(items)
                if n > 3:
                    preview = ", ".join(f"{k}={v}" for k, v in items[:3])
                    return (
                        f"{type(param).__name__}[len={n}, preview={{ {preview}, ... }}]"
                    )
                return str(param)

            # Bytes / bytearray
            if isinstance(param, (bytes, bytearray)):
                n = len(param)
                if n > 8:
                    preview = " ".join(f"0x{b:02X}" for b in param[:8])
                    return f"{type(param).__name__}[len={n}, preview={preview} ...]"
                return " ".join(f"0x{b:02X}" for b in param)

            # NumPy arrays
            if HAS_NUMPY:
                try:
                    if isinstance(param, np.ndarray):
                        return f"ndarray(shape={param.shape}, dtype={param.dtype})"
                except ImportError:
                    pass

            # Default string with recursion protection
            try:
                return str(param)
            except RecursionError:
                return f"<{type(param).__name__} with circular reference>"

        type_name = type(parameter).__name__
        formatted_value = format_value(parameter)

        # Truncate final string if still too long
        if len(formatted_value) > max_length:
            formatted_value = formatted_value[: max_length - 3] + "..."

        padded_message = f"{message:<{LOG_PADDING_WIDTH}}"
        padded_type = f"{type_name:<12}"
        final_message = f"{padded_message} {padded_type} {formatted_value}".rstrip()

        Decologr.message(final_message, silent=silent, stacklevel=stacklevel, level=level)

    @staticmethod
    def _format_parameter_value(param: Any, float_precision: int = 2, max_length: int = 300) -> str:
        """
        Format a parameter value for display in Rich tables/trees.
        
        Args:
            param: The value to format
            float_precision: Number of decimal places for floats
            max_length: Maximum length for string representation
        
        Returns:
            Formatted string representation with Rich markup
        """
        if param is None:
            return "[dim]None[/dim]"
        
        # Handle enums
        try:
            import enum
            if isinstance(param, enum.Enum):
                return param.name
        except ImportError:
            pass
        
        # Float formatting
        if isinstance(param, float):
            return f"{param:.{float_precision}f}"
        
        # Boolean
        if isinstance(param, bool):
            return "[green]True[/green]" if param else "[red]False[/red]"
        
        # String
        if isinstance(param, str):
            if len(param) > max_length:
                return param[:max_length - 3] + "..."
            return param
        
        # List / tuple (simple representation)
        if isinstance(param, (list, tuple)):
            n = len(param)
            if n == 0:
                return f"[dim]{type(param).__name__} (empty)[/dim]"
            if n <= 3:
                items = ", ".join(Decologr._format_parameter_value(item, float_precision, 50) for item in param)
                return f"[{items}]"
            return f"[dim]{type(param).__name__}[/dim] (len={n})"
        
        # Dictionary (simple representation)
        if isinstance(param, dict):
            n = len(param)
            if n == 0:
                return "[dim]dict (empty)[/dim]"
            return f"[dim]dict[/dim] (len={n})"
        
        # NumPy arrays
        if HAS_NUMPY:
            try:
                if isinstance(param, np.ndarray):
                    return f"[cyan]ndarray[/cyan](shape={param.shape}, dtype={param.dtype})"
            except Exception:
                pass
        
        # Default string representation
        try:
            str_repr = str(param)
            if len(str_repr) > max_length:
                return str_repr[:max_length - 3] + "..."
            return str_repr
        except RecursionError:
            return f"[dim]<{type(param).__name__} with circular reference>[/dim]"

    @staticmethod
    def _log_parameter_to_file(
        message: str,
        parameter: Any,
        type_name: str,
        float_precision: int,
        max_length: int,
        level: int,
        stacklevel: int,
    ) -> None:
        """
        Log parameter to file handlers only (compact format).
        Used when Rich formatting is used for console output.
        """
        def format_value(param: Any) -> str:
            if param is None:
                return "None"
            
            try:
                import enum
                if isinstance(param, enum.Enum):
                    return param.name
            except ImportError:
                pass
            
            if isinstance(param, float):
                return f"{param:.{float_precision}f}"
            
            if isinstance(param, (list, tuple)):
                n = len(param)
                if n > 5:
                    preview = ", ".join(str(item) for item in param[:5])
                    return f"{type(param).__name__}[len={n}, preview=[{preview}, ...]]"
                return str(param)
            
            if isinstance(param, dict):
                items = list(param.items())
                n = len(items)
                if n > 3:
                    preview = ", ".join(f"{k}={v}" for k, v in items[:3])
                    return f"{type(param).__name__}[len={n}, preview={{ {preview}, ... }}]"
                return str(param)
            
            if isinstance(param, (bytes, bytearray)):
                n = len(param)
                if n > 8:
                    preview = " ".join(f"0x{b:02X}" for b in param[:8])
                    return f"{type(param).__name__}[len={n}, preview={preview} ...]"
                return " ".join(f"0x{b:02X}" for b in param)
            
            if HAS_NUMPY:
                try:
                    if isinstance(param, np.ndarray):
                        return f"ndarray(shape={param.shape}, dtype={param.dtype})"
                except ImportError:
                    pass
            
            try:
                return str(param)
            except RecursionError:
                return f"<{type(param).__name__} with circular reference>"
        
        formatted_value = format_value(parameter)
        if len(formatted_value) > max_length:
            formatted_value = formatted_value[: max_length - 3] + "..."
        
        padded_message = f"{message:<{LOG_PADDING_WIDTH}}"
        padded_type = f"{type_name:<12}"
        final_message = f"{padded_message} {padded_type} {formatted_value}".rstrip()
        
        # Log only to file handlers (temporarily remove console handlers)
        logger = logging.getLogger(_project_name)
        root_logger = logging.root
        
        console_handlers = []
        for handler in list(logger.handlers):
            if isinstance(handler, (RichHandler, logging.StreamHandler)):
                console_handlers.append((handler, logger))
                logger.removeHandler(handler)
        for handler in list(root_logger.handlers):
            if isinstance(handler, (RichHandler, logging.StreamHandler)):
                if not any(h == handler for h, _ in console_handlers):
                    console_handlers.append((handler, root_logger))
                    root_logger.removeHandler(handler)
        
        # Log to file handlers
        Decologr.message(final_message, silent=False, stacklevel=stacklevel, level=level)
        
        # Restore console handlers
        for handler, source_logger in console_handlers:
            source_logger.addHandler(handler)

    @staticmethod
    def header_message(
        message: str,
        level: int = logging.INFO,
        silent: bool = False,
        stacklevel: int = 3,
        use_rich: Optional[bool] = None,
        title: Optional[str] = None,
    ) -> None:
        """
        Logs a visually distinct header message with separator lines.
        When Rich is available, displays as a formatted panel.

        Args:
            message: The header message to log
            level: Logging level (default: logging.INFO)
            silent: If True, don't output anything
            stacklevel: Stack level for logging
            use_rich: If True, use Rich panel formatting (when Rich is available).
                     If None, auto-detect (uses Rich if available).
                     If False, use text-based separator lines.
            title: Optional title for Rich panel (default: "Log Header")
        
        When Rich is available and use_rich=True (or None):
            - Displays as a formatted panel with colored borders
            - Border color matches log level (INFO=blue, WARNING=yellow, ERROR=red, etc.)
            - Better visual hierarchy and distinction
        
        When Rich is not available or use_rich=False:
            - Uses traditional separator lines (original behavior)
        """
        if silent:
            return

        # Determine if we should use Rich panel
        use_rich_panel = False
        if HAS_RICH and Panel is not None:
            if use_rich is None:
                # Auto-detect: use Rich if RichHandler is available
                use_rich_panel = _is_rich_handler_available()
            elif use_rich is True:
                use_rich_panel = True

        if use_rich_panel:
            # Use Rich Panel for beautiful header display
            try:
                console = Console(stderr=False)
                
                # Get border style based on log level
                border_style = LEVEL_COLORS.get(level, "blue")
                
                # Use message as-is (no emoji to avoid alignment issues)
                formatted_message = message
                
                # Use provided title or default
                panel_title = title if title is not None else "[bold]Log Header[/bold]"
                
                # Create and print panel
                panel = Panel(
                    formatted_message,
                    title=panel_title,
                    border_style=border_style,
                    expand=False,
                    padding=(0, 2),  # Small padding for readability
                )
                console.print(panel)
                
                # Also log text version to file handlers
                full_separator = f"{'=' * 142}"
                separator = f"{'=' * 100}"
                
                # Temporarily remove console handlers, log, then restore
                logger = logging.getLogger(_project_name)
                root_logger = logging.root
                
                console_handlers = []
                for handler in list(logger.handlers):
                    if isinstance(handler, (RichHandler, logging.StreamHandler)):
                        console_handlers.append((handler, logger))
                        logger.removeHandler(handler)
                for handler in list(root_logger.handlers):
                    if isinstance(handler, (RichHandler, logging.StreamHandler)):
                        if not any(h == handler for h, _ in console_handlers):
                            console_handlers.append((handler, root_logger))
                            root_logger.removeHandler(handler)
                
                # Log text version to file handlers
                Decologr.message(
                    f"\n{full_separator}", level=level, stacklevel=stacklevel, silent=False
                )
                Decologr.message(f"{message}", level=level, stacklevel=stacklevel, silent=False)
                Decologr.message(separator, level=level, stacklevel=stacklevel, silent=False)
                
                # Restore console handlers
                for handler, source_logger in console_handlers:
                    source_logger.addHandler(handler)
                
                return
                
            except Exception as e:
                # Fallback to text-based formatting if Rich panel fails
                Decologr.warning(f"Rich header formatting failed, using text format: {e}", stacklevel=stacklevel)
        
        # Fallback to text-based formatting (original behavior)
        full_separator = f"{'=' * 142}"
        separator = f"{'=' * 100}"

        Decologr.message(
            f"\n{full_separator}", level=level, stacklevel=stacklevel, silent=silent
        )
        Decologr.message(f"{message}", level=level, stacklevel=stacklevel, silent=silent)
        Decologr.message(separator, level=level, stacklevel=stacklevel, silent=silent)

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

        Decologr.message(
            f"Successes ({len(successes)}): {successes}", stacklevel=stacklevel
        )
        Decologr.message(f"Failures ({len(failures)}): {failures}", stacklevel=stacklevel)
        Decologr.message(f"Success Rate: {success_rate:.1f}%", stacklevel=stacklevel)
        Decologr.message("=" * 100, stacklevel=3)


def log_exception(exception: Exception, message: str, stacklevel: int = 4, use_rich_traceback: Optional[bool] = None) -> None:
    """
    Log an exception with a descriptive message.
    
    This function provides a convenient way to log exceptions, matching the
    signature used by mxlib.core.exception.log.log_exception for compatibility.
    
    Args:
        exception: The exception to log
        message: Descriptive message about the error context
        stacklevel: Stack level for logging (default: 4)
        use_rich_traceback: If True, use Rich traceback formatting (when Rich is available).
                           If None, auto-detect (uses Rich if available).
                           If False, use standard traceback formatting.
    
    Example:
        try:
            # some code
        except Exception as ex:
            log_exception(ex, "Error initializing scheduler database")
    """
    Decologr.error(message, exception=exception, stacklevel=stacklevel, use_rich_traceback=use_rich_traceback)

