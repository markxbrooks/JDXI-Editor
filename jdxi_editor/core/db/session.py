"""
SQLAlchemy base and session management for JD-Xi Editor.

This module provides the declarative base and session management utilities
for SQLAlchemy ORM operations.
"""

from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from sqlalchemy import Index, create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from decologr import Decologr as log
from decologr import log_exception
from jdxi_editor.core.db.base import Base
from jdxi_editor.core.db.pragma import Pragma

# Import models to ensure they're registered with Base
from jdxi_editor.core.db.schema.playlists import PlayList, PlaylistItem  # noqa: E402


class DatabaseSession:
    """Manages SQLAlchemy database sessions and connections."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database session manager.

        :param db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # --- Default to user's home directory for JD-Xi Editor database
            from jdxi_editor.project import __package_name__

            json_folder = Path.home() / f".{__package_name__}"
            json_folder.mkdir(parents=True, exist_ok=True)
            db_path = json_folder / "user_programs.db"
        else:
            db_path = Path(db_path)

        # --- Ensure parent directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path

        # --- Create engine with SQLite-specific settings
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={
                "check_same_thread": False,
                "timeout": 30.0,
            },
            poolclass=StaticPool,
            echo=False,  # --- Set to True for SQL debugging
        )

        # --- Configure SQLite pragmas
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            """Set SQLite pragmas on connection."""
            cursor = dbapi_conn.cursor()
            pragmas = [
                Pragma.FOREIGN_KEYS_ON,
                Pragma.JOURNAL_MODE_WAL,
                Pragma.SYNCHRONOUS_NORMAL,
                Pragma.BUSY_TIMEOUT_30_SEC,
            ]
            for pragma in pragmas:
                cursor.execute(pragma)
            cursor.close()

        # --- Create session factory
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
        )

    def create_indexes(self):
        """Create database indexes for better query performance."""
        indexes = [
            Index("idx_playlist_items_playlist_id", PlaylistItem.playlist_id),
            Index("idx_playlist_items_program_id", PlaylistItem.program_id),
            Index(
                "idx_playlist_items_position",
                PlaylistItem.playlist_id,
                PlaylistItem.position,
            ),
        ]

        for index in indexes:
            try:
                index.create(self.engine, checkfirst=True)
            except Exception as ex:
                log.warning(f"Could not create index {index.name}: {ex}")

    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
        log.info(f"Database tables created at {self.db_path}")

    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions.

        Usage:
            with db_session.get_session() as session:
                job = session.query(JobQueue).filter_by(job_id="123").first()
        """
        session = self.SessionLocal()
        committed = False

        # --- Helper function to check if session is in a transaction
        # --- Compatible with both SQLAlchemy 1.x and 2.x
        def check_in_transaction():
            if hasattr(session, "in_transaction"):
                return session.in_transaction()
            return session.is_active

        try:
            yield session
            # --- Check if session is in a transaction before committing
            in_transaction = check_in_transaction()

            if in_transaction:
                try:
                    session.commit()
                    committed = True
                except SystemError as sys_err:
                    # --- Handle SQLite commit returning NULL (connection in bad state)
                    # --- This happens when the underlying SQLite connection is corrupted or closed
                    error_msg = str(sys_err)
                    if (
                        "returned NULL" in error_msg
                        or "without setting an exception" in error_msg
                    ):
                        log.warning(
                            "Database connection in invalid state during commit. "
                            "This may indicate database corruption, threading issues, or connection pool problems."
                        )
                        try:
                            # --- Try to rollback, but don't fail if that also fails
                            if check_in_transaction():
                                session.rollback()
                        except Exception as rollback_err:
                            log.warning(f"Rollback also failed: {rollback_err}")
                        # --- Re-raise as a more informative error
                        raise RuntimeError(
                            "Database connection error: commit failed due to invalid connection state. "
                            "The database connection may be corrupted or there may be a threading issue. "
                            "Try restarting the scheduler service."
                        ) from sys_err
                    raise
                except Exception as commit_err:
                    # --- For other commit errors, rollback and re-raise
                    if check_in_transaction():
                        try:
                            session.rollback()
                        except Exception:
                            pass
                    raise
        except Exception as ex:
            # --- Only rollback if we haven't committed and session is in a transaction
            if not committed:
                if check_in_transaction():
                    try:
                        session.rollback()
                    except SystemError as rollback_sys_err:
                        # --- Handle SystemError during rollback too
                        error_msg = str(rollback_sys_err)
                        if (
                            "returned NULL" in error_msg
                            or "without setting an exception" in error_msg
                        ):
                            log.warning(
                                "Database connection error during rollback - connection may be corrupted. "
                                "The session will be closed."
                            )
                        else:
                            log.warning(f"Error during rollback: {rollback_sys_err}")
                    except Exception as rollback_err:
                        # If rollback also fails, log but don't raise
                        log.warning(f"Error during rollback: {rollback_err}")
            log_exception(ex, "Database session error")
            raise
        finally:
            # --- Always close the session to prevent hanging
            try:
                session.close()
            except Exception as close_ex:
                log.warning(f"Error closing session: {close_ex}")

    def get_session_sync(self) -> Session:
        """
        Get a synchronous session (caller must close it).

        :return: SQLAlchemy session
        """
        return self.SessionLocal()
