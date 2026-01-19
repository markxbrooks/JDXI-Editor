"""
This module provides a utility class `DatabaseConnection` that offers a
structured approach for handling SQLite database interactions. It includes
features such as ensuring database directories exist, managing SQLite
connections, and executing multiple SQL statements transactionally.

Classes:
    DatabaseConnection: A wrapper for managing SQLite database connections.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import List

from jdxi_editor.core.db.pragma import Pragma


class DatabaseConnection:
    """A wrapper class for managing SQLite database connections."""

    def __init__(self, db_path: Path):
        """
        Initialize the DatabaseConnection class.

        :param db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._ensure_parent_directory_exists()

    def _ensure_parent_directory_exists(self):
        """Ensure the parent directory of the database file exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """
        Get a SQLite connection with proper settings.
        """
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        conn.execute(Pragma.FOREIGN_KEYS_ON)  # Enable foreign key support
        return conn

    @contextmanager
    def get_connection_context(self):
        """
        Context manager for SQLite connection with autocommit and pragmas.
        """
        conn = self.get_connection()
        try:
            # --- Apply additional settings
            pragmas = [
                Pragma.FOREIGN_KEYS_ON,
                Pragma.JOURNAL_MODE_WAL,
                Pragma.SYNCHRONOUS_NORMAL,
                Pragma.BUSY_TIMEOUT_30_SEC,
            ]
            for pragma in pragmas:
                conn.execute(pragma)
            yield conn
        finally:
            conn.close()

    def execute_multiple(self, sql_statements: List[str]):
        """
        Execute multiple SQL statements within a transaction.

        :param sql_statements: List of SQL statements to execute.
        """
        with self.get_connection_context() as conn:
            try:
                cursor = conn.cursor()
                for sql in sql_statements:
                    cursor.execute(sql)
                conn.commit()
            except Exception as ex:
                conn.rollback()
                raise RuntimeError(f"Error executing SQL: {ex}")
