"""
Contains settings and SQL statements for configuring SQLite3 database behavior.

This module provides the necessary SQL commands to enable certain features
and optimize SQLite3 database operations, particularly using PRAGMA statements.
The focus includes enabling foreign key constraints and configuring the database
for Write-Ahead Logging (WAL) mode. It also includes settings for synchronous
operation and timeout duration for database connections.
"""


class Pragma:
    """pragma settings for sqlite3 database"""

    FOREIGN_KEYS_ON: str = "PRAGMA foreign_keys = ON"
    JOURNAL_MODE_WAL: str = "PRAGMA journal_mode = WAL"
    SYNCHRONOUS_NORMAL: str = "PRAGMA synchronous = NORMAL"
    BUSY_TIMEOUT_30_SEC: str = "PRAGMA busy_timeout = 30000"
