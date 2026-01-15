"""
decologr - Decorative Logger

A logging utility with emoji decorations and structured message formatting.
"""

from decologr.logger import (
    Decologr,
    cleanup_logging,
    setup_logging,
    set_project_name,
    get_project_name,
    log_exception,
)

# Backward compatibility alias for JDXI and other code expecting "Logger"
Logger = Decologr

# Optional Textual viewer components
try:
    from decologr.viewer import (
        LogViewerWidget,
        LogViewerApp,
        create_log_viewer_widget,
        run_log_viewer,
    )
    __all__ = [
        "Decologr",
        "Logger",  # Backward compatibility alias
        "cleanup_logging",
        "setup_logging",
        "set_project_name",
        "get_project_name",
        "log_exception",
        "LogViewerWidget",
        "LogViewerApp",
        "create_log_viewer_widget",
        "run_log_viewer",
    ]
except ImportError:
    __all__ = [
        "Decologr",
        "Logger",  # Backward compatibility alias
        "cleanup_logging",
        "setup_logging",
        "set_project_name",
        "get_project_name",
        "log_exception",
    ]
except TypeError:
    __all__ = [
        "Decologr",
        "Logger",  # Backward compatibility alias
        "cleanup_logging",
        "setup_logging",
        "set_project_name",
        "get_project_name",
        "log_exception",
    ]


