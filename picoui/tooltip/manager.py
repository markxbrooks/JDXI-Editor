"""
Tooltip definitions for UI elements.

Centralized tooltip text to ensure consistency across the application.
"""


class TooltipManager:
    """Centralized tooltip text manager for UI elements."""
    # Menu actions
    ACTION_HELP = "Open the documentation in a browser"
    ACTION_EDIT_PREFERENCES = (
        "Open preferences dialog to configure application settings"
    )
    ACTION_VIEW_LOG_FILE = "Open the application log file viewer"
    ACTION_SELECT_FOLDER = "Select working folder containing datasets"
    ACTION_ABOUT = "Show application information and version"
    ACTION_QUIT = "Exit the application"

    # Table view buttons
    BUTTON_INSERT_ROW = "Add a new empty row to the table"
    BUTTON_DELETE_ROW = "Delete the selected row(s) from the table"

    PREF_CLEAR_ON_SEARCH_CHECKBOX = (
        "Clear the protein editor when performing a new search"
    )
    PREF_LOG_LEVEL_COMBO = (
        "Set the minimum logging level. "
        "DEBUG shows all messages, ERROR shows only errors."
    )

    # Search fields
    SEARCH_FIELD = "Enter text to filter table rows. Searches across all columns."
    FILTER_COLUMN_FIELD = (
        "Enter text to filter a specific column. "
        "Select the column from the dropdown first."
    )

    # Tabs
    TAB_DOCUMENTATION = "Application documentation and help"

    @staticmethod
    def get_tooltip(key: str) -> str:
        """
        Get tooltip text by key.

        :param key: Tooltip key (attribute name)
        :return: Tooltip text or empty string if not found
        """
        return getattr(TooltipManager, key, "")