"""
Recent MIDI Files Manager

Manages a list of recently opened MIDI files, persisting them to disk.
"""

import json
from pathlib import Path
from typing import List

from decologr import Decologr as log
from jdxi_editor.project import __package_name__


class RecentFilesManager:
    """Manages recent MIDI files list with persistence."""

    MAX_RECENT_FILES = 10

    def __init__(self):
        """Initialize the recent files manager."""
        self.config_dir = Path.home() / f".{__package_name__}"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.recent_files_path = self.config_dir / "recent_midi_files.json"
        self._recent_files: List[str] = []
        self._load_recent_files()

    def _load_recent_files(self) -> None:
        """Load recent files from disk."""
        try:
            if self.recent_files_path.exists():
                with open(self.recent_files_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._recent_files = data.get("recent_files", [])
                    # Filter out files that no longer exist
                    self._recent_files = [
                        f for f in self._recent_files if Path(f).exists()
                    ]
                    self._save_recent_files()
            else:
                self._recent_files = []
        except Exception as ex:
            log.error(f"Error loading recent files: {ex}")
            self._recent_files = []

    def _save_recent_files(self) -> None:
        """Save recent files to disk."""
        try:
            data = {"recent_files": self._recent_files}
            with open(self.recent_files_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as ex:
            log.error(f"Error saving recent files: {ex}")

    def add_file(self, file_path: str) -> None:
        """
        Add a file to the recent files list.

        :param file_path: Path to the MIDI file
        """
        if not file_path:
            return

        file_path = str(Path(file_path).resolve())

        # Remove if already exists
        if file_path in self._recent_files:
            self._recent_files.remove(file_path)

        # Add to beginning
        self._recent_files.insert(0, file_path)

        # Limit to max files
        if len(self._recent_files) > self.MAX_RECENT_FILES:
            self._recent_files = self._recent_files[: self.MAX_RECENT_FILES]

        self._save_recent_files()
        log.debug(f"Added to recent files: {file_path}")

    def get_recent_files(self) -> List[str]:
        """
        Get the list of recent files.

        :return: List of file paths
        """
        # Filter out files that no longer exist
        self._recent_files = [f for f in self._recent_files if Path(f).exists()]
        if len(self._recent_files) != len(self._recent_files):
            self._save_recent_files()
        return self._recent_files.copy()

    def clear_recent_files(self) -> None:
        """Clear all recent files."""
        self._recent_files = []
        self._save_recent_files()
        log.debug("Cleared recent files")
