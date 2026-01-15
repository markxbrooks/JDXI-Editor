"""
Textual-based log viewer component for displaying logs in a beautiful, formatted way.

This module provides a Textual widget that can be integrated into editors like JDXI
to display decologr log files with proper formatting, colors, and structure.
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import DataTable, Footer, Header, Input, Label, Log, Static
    from textual.binding import Binding
    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False
    App = None
    ComposeResult = None
    Container = None
    Horizontal = None
    Vertical = None
    DataTable = None
    Footer = None
    Header = None
    Input = None
    Label = None
    Log = None
    Static = None
    Binding = None

# Import LEVEL_COLORS from decologr.logger to ensure consistency
try:
    from decologr.logger import LEVEL_COLORS
except ImportError:
    # Fallback if import fails
    LEVEL_COLORS = {
        logging.DEBUG: "dim white",
        logging.INFO: "blue",
        logging.WARNING: "yellow",
        logging.ERROR: "red",
        logging.CRITICAL: "bold red on white",
    }

LEVEL_NAMES = {
    logging.DEBUG: "DEBUG",
    logging.INFO: "INFO",
    logging.WARNING: "WARNING",
    logging.ERROR: "ERROR",
    logging.CRITICAL: "CRITICAL",
}


def parse_log_line(line: str) -> Optional[Tuple[int, str, int, str, str]]:
    """
    Parse a log line in decologr format.
    
    Format: "%(filename)-20s| %(lineno)-5s| %(levelname)-8s| %(message)-24s"
    Example: "logger.py          |    42| INFO    | Starting application..."
    
    Returns:
        Tuple of (level, filename, lineno, levelname, message) or None if parse fails
    """
    # Pattern: filename (20 chars) | lineno (5 chars) | levelname (8 chars) | message
    pattern = r"^(.{1,20})\s*\|\s*(\d+)\s*\|\s*(\w+)\s*\|\s*(.*)$"
    match = re.match(pattern, line.strip())
    
    if not match:
        return None
    
    filename, lineno_str, levelname, message = match.groups()
    filename = filename.strip()
    lineno = int(lineno_str)
    
    # Map levelname to logging level
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    level = level_map.get(levelname.upper(), logging.INFO)
    
    return (level, filename, lineno, levelname, message)


class LogViewerWidget(Static):
    """
    A Textual widget for displaying log files with formatting and filtering.
    
    This widget can be embedded in editors like JDXI to display logs beautifully.
    """
    
    def __init__(
        self,
        log_file: Optional[Path] = None,
        max_lines: int = 10000,
        auto_scroll: bool = True,
        **kwargs
    ):
        """
        Initialize the log viewer widget.
        
        Args:
            log_file: Path to log file to display
            max_lines: Maximum number of lines to keep in memory
            auto_scroll: Whether to auto-scroll to bottom on new logs
        """
        super().__init__(**kwargs)
        self.log_file = log_file
        self.max_lines = max_lines
        self.auto_scroll = auto_scroll
        self.log_lines: List[Tuple[int, str, int, str, str]] = []
        self.filtered_lines: List[Tuple[int, str, int, str, str]] = []
        self.current_filter_level: Optional[int] = None
        self.search_text: str = ""
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        if not HAS_TEXTUAL:
            yield Static("Textual is not installed. Install with: pip install decologr[textual]")
            return
        
        with Vertical():
            with Horizontal(classes="toolbar"):
                yield Label("Log Viewer", classes="title")
                yield Input(placeholder="Search...", id="search-input")
            yield DataTable(id="log-table")
    
    def on_mount(self) -> None:
        """Called when widget is mounted."""
        if not HAS_TEXTUAL:
            return
        
        table = self.query_one("#log-table", DataTable)
        table.add_columns("Time", "Level", "File", "Line", "Message")
        table.cursor_type = "row"
        
        if self.log_file and self.log_file.exists():
            self.load_log_file(self.log_file)
    
    def load_log_file(self, log_file: Path) -> None:
        """
        Load and parse a log file.
        
        Args:
            log_file: Path to log file
        """
        self.log_file = log_file
        self.log_lines = []
        
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    parsed = parse_log_line(line)
                    if parsed:
                        self.log_lines.append(parsed)
            
            # Limit to max_lines (keep most recent)
            if len(self.log_lines) > self.max_lines:
                self.log_lines = self.log_lines[-self.max_lines:]
            
            self.apply_filters()
            self.refresh_display()
            
        except Exception as e:
            if HAS_TEXTUAL:
                self.notify(f"Error loading log file: {e}", severity="error")
    
    def apply_filters(self) -> None:
        """Apply current filters and search to log lines."""
        self.filtered_lines = self.log_lines
        
        # Filter by level
        if self.current_filter_level is not None:
            self.filtered_lines = [
                line for line in self.filtered_lines
                if line[0] >= self.current_filter_level
            ]
        
        # Filter by search text
        if self.search_text:
            search_lower = self.search_text.lower()
            self.filtered_lines = [
                line for line in self.filtered_lines
                if search_lower in line[4].lower() or search_lower in line[1].lower()
            ]
    
    def refresh_display(self) -> None:
        """Refresh the display with current filtered lines."""
        if not HAS_TEXTUAL:
            return
        
        table = self.query_one("#log-table", DataTable)
        table.clear()
        
        for level, filename, lineno, levelname, message in self.filtered_lines:
            # Format timestamp (simplified - could parse from log if available)
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Get color for level from Decologr's LEVEL_COLORS
            level_color = LEVEL_COLORS.get(level, "white")
            
            # Apply color to level name
            level_display = f"[{level_color}]{levelname}[/{level_color}]"
            
            # Truncate long messages
            display_message = message[:200] + "..." if len(message) > 200 else message
            
            # Apply color to message based on level
            colored_message = f"[{level_color}]{display_message}[/{level_color}]"
            
            # Add row with colored content
            row_key = f"{filename}:{lineno}"
            table.add_row(
                timestamp,
                level_display,
                filename,
                str(lineno),
                colored_message,
                key=row_key,
            )
            
            # Apply row styling based on log level for better visibility
            # Use a lighter background tint for different levels
            row_style_map = {
                logging.DEBUG: "dim",
                logging.INFO: "",
                logging.WARNING: "on yellow1",
                logging.ERROR: "on red1",
                logging.CRITICAL: "on red",
            }
            row_style = row_style_map.get(level, "")
            if row_style:
                try:
                    # Apply style to the row if Textual supports it
                    # Note: DataTable row styling may vary by Textual version
                    pass  # Row-level styling can be added if Textual supports it
                except Exception:
                    pass  # Gracefully handle if styling not supported
        
        # Auto-scroll to bottom
        if self.auto_scroll and self.filtered_lines:
            table.scroll_to_row(len(self.filtered_lines) - 1)
    
    def on_input_changed(self, event) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self.search_text = event.value
            self.apply_filters()
            self.refresh_display()
    
    def filter_by_level(self, level: Optional[int]) -> None:
        """
        Filter logs by minimum level.
        
        Args:
            level: Minimum log level (None to show all)
        """
        self.current_filter_level = level
        self.apply_filters()
        self.refresh_display()
    
    def clear_search(self) -> None:
        """Clear search filter."""
        if HAS_TEXTUAL:
            search_input = self.query_one("#search-input", Input)
            search_input.value = ""
        self.search_text = ""
        self.apply_filters()
        self.refresh_display()


class LogViewerApp(App):
    """
    Standalone Textual app for viewing log files.
    
    Can be run as: python -m decologr.viewer <log_file>
    """
    
    CSS = """
    .toolbar {
        height: 3;
        border: solid $primary;
    }
    
    .title {
        width: 20;
        text-style: bold;
    }
    
    #log-table {
        height: 100%;
    }
    
    #search-input {
        width: 1fr;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("f", "filter", "Filter"),
        Binding("c", "clear", "Clear Search"),
        Binding("r", "refresh", "Refresh"),
    ]
    
    def __init__(self, log_file: Optional[Path] = None, **kwargs):
        super().__init__(**kwargs)
        self.log_file = log_file
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        if not HAS_TEXTUAL:
            yield Static("Textual is not installed. Install with: pip install decologr[textual]")
            return
        
        yield Header()
        yield LogViewerWidget(log_file=self.log_file, id="viewer")
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when app is mounted."""
        if self.log_file:
            viewer = self.query_one("#viewer", LogViewerWidget)
            viewer.load_log_file(self.log_file)
    
    def action_filter(self) -> None:
        """Show filter menu."""
        # Could implement a filter menu here
        self.notify("Filter by level: Use INFO, WARNING, ERROR, etc.", severity="info")
    
    def action_clear(self) -> None:
        """Clear search."""
        viewer = self.query_one("#viewer", LogViewerWidget)
        viewer.clear_search()
    
    def action_refresh(self) -> None:
        """Refresh log display."""
        viewer = self.query_one("#viewer", LogViewerWidget)
        if viewer.log_file:
            viewer.load_log_file(viewer.log_file)


def create_log_viewer_widget(log_file: Optional[Path] = None) -> LogViewerWidget:
    """
    Create a LogViewerWidget instance for embedding in editors.
    
    Args:
        log_file: Optional path to log file to load
    
    Returns:
        LogViewerWidget instance
    
    Example:
        ```python
        from decologr.viewer import create_log_viewer_widget
        from pathlib import Path
        
        widget = create_log_viewer_widget(Path("~/.decologr/logs/myapp.log"))
        # Embed widget in your editor UI
        ```
    """
    if not HAS_TEXTUAL:
        raise ImportError(
            "Textual is not installed. Install with: pip install decologr[textual]"
        )
    
    return LogViewerWidget(log_file=log_file)


def run_log_viewer(log_file: Path) -> None:
    """
    Run the standalone log viewer app.
    
    Args:
        log_file: Path to log file to view
    
    Example:
        ```python
        from decologr.viewer import run_log_viewer
        from pathlib import Path
        
        run_log_viewer(Path("~/.decologr/logs/myapp.log"))
        ```
    """
    if not HAS_TEXTUAL:
        raise ImportError(
            "Textual is not installed. Install with: pip install decologr[textual]"
        )
    
    app = LogViewerApp(log_file=log_file)
    app.run()


def get_logger_for_jdxi():
    """
    Get the Logger class for JDXI integration.
    
    This function provides backward compatibility for JDXI editor
    which may expect a 'Logger' class name.
    
    Returns:
        The Decologr class (aliased as Logger for compatibility)
    """
    from decologr.logger import Decologr
    return Decologr


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        log_file = Path(sys.argv[1])
    else:
        # Default to most recent log file
        log_dir = Path.home() / ".decologr" / "logs"
        if log_dir.exists():
            log_files = sorted(log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
            log_file = log_files[0] if log_files else None
        else:
            log_file = None
    
    if log_file and log_file.exists():
        run_log_viewer(log_file)
    else:
        print(f"Usage: {sys.argv[0]} <log_file>")
        print("Or ensure ~/.decologr/logs/ exists with log files")
