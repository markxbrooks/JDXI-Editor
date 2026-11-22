"""
SQLAlchemy base and session management for JD-Xi Editor.

This module provides the declarative base and session management utilities
for SQLAlchemy ORM operations.
"""

from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from decologr import Decologr as log
from decologr import log_exception
from sqlalchemy import Index, create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from jdxi_editor.core.db.base import Base
from jdxi_editor.core.db.pragma import Pragma

# --- Import models to ensure they're registered with Base
from jdxi_editor.core.db.schema.playlists import PlaylistItem  # noqa: E402


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

        # --- Create name with SQLite-specific settings
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
        """Create database indexes for better query performance.

        An Index attaches itself to the table definition, which is shared by
        every session in the process. Building new ones on each call left
        duplicates there, and the next session's create_tables() on a new
        database failed with "index ... already exists". Existing ones are
        reused instead."""
        attached = {ix.name: ix for ix in PlaylistItem.__table__.indexes}
        specs = [
            ("idx_playlist_items_playlist_id", (PlaylistItem.playlist_id,)),
            ("idx_playlist_items_program_id", (PlaylistItem.program_id,)),
            ("idx_playlist_items_position", (PlaylistItem.playlist_id, PlaylistItem.position)),
        ]
        indexes = [attached.get(name) or Index(name, *columns) for name, columns in specs]

        for index in indexes:
            try:
                index.create(self.engine, checkfirst=True)
            except Exception as ex:
                log.warning(f"Could not create index {index.name}: {ex}")

    def create_tables(self):
        """Create all database tables, and add columns that newer versions
        introduced to tables made by older ones."""
        Base.metadata.create_all(bind=self.engine)
        self.add_missing_columns()
        self.allow_songs_without_program()
        log.info(f"Database tables created at {self.db_path}")

    def add_missing_columns(self) -> list:
        """Upgrade an older database in place: add each optional (nullable)
        column of the models that its tables lack. create_all() makes missing
        tables but never changes existing ones. Returns "table.column" for
        each column added."""
        from sqlalchemy import inspect, text

        added = []
        inspector = inspect(self.engine)
        existing_tables = set(inspector.get_table_names())
        with self.engine.begin() as conn:
            for table in Base.metadata.sorted_tables:
                if table.name not in existing_tables:
                    continue
                have = {c["name"] for c in inspector.get_columns(table.name)}
                for column in table.columns:
                    if column.name in have or not column.nullable or column.primary_key:
                        continue
                    col_type = column.type.compile(dialect=self.engine.dialect)
                    conn.execute(
                        text(f'ALTER TABLE "{table.name}" ADD COLUMN "{column.name}" {col_type}')
                    )
                    added.append(f"{table.name}.{column.name}")
        for name in added:
            log.info(f"Database upgraded: added column {name}")
        return added

    def allow_songs_without_program(self) -> bool:
        """
        Let a playlist song have no program.

        SQLite cannot relax ``NOT NULL`` in place, so a table whose
        ``program_id`` is still required is rebuilt. The foreign key stays:
        a null program matches nothing, and deleting a program still removes
        only the songs that use it.

        :return: bool True when the table was rebuilt
        """
        from sqlalchemy import inspect

        inspector = inspect(self.engine)
        inspector.clear_cache()
        if "playlist_items" not in set(inspector.get_table_names()):
            return False
        columns = {column["name"]: column for column in inspector.get_columns("playlist_items")}
        program = columns.get("program_id")
        if program is None or program.get("nullable"):
            return False
        names = [
            "id",
            "playlist_id",
            "program_id",
            "position",
            "midi_file_path",
            "cheat_preset_id",
            "artwork_path",
            "created_at",
        ]
        present = [name for name in names if name in columns]
        listed = ", ".join(present)
        raw = self.engine.raw_connection()
        try:
            cursor = raw.cursor()
            raw.rollback()
            foreign_keys = list(cursor.execute("PRAGMA foreign_key_list(playlist_items)"))
            cursor.execute("PRAGMA foreign_keys=OFF")
            grouped = {}
            for fk_id, seq, table, source, target, _on_update, on_delete, _match in foreign_keys:
                grouped.setdefault(fk_id, {"table": table, "on_delete": on_delete, "cols": []})
                grouped[fk_id]["cols"].append((seq, source, target))
            clauses = []
            for fk in grouped.values():
                cols = sorted(fk["cols"])
                sources = ", ".join(source for _seq, source, _target in cols)
                targets = ", ".join(target for _seq, _source, target in cols)
                clause = f"FOREIGN KEY ({sources}) REFERENCES {fk['table']}({targets})"
                if fk["on_delete"] and fk["on_delete"].upper() != "NO ACTION":
                    clause += f" ON DELETE {fk['on_delete']}"
                clauses.append(clause)
            clauses.append("UNIQUE(playlist_id, program_id, position)")
            constraints = ",\n".join(clauses)
            try:
                cursor.execute(
                    f"""
                    CREATE TABLE playlist_items_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        playlist_id INTEGER NOT NULL,
                        program_id TEXT,
                        position INTEGER NOT NULL,
                        midi_file_path TEXT,
                        cheat_preset_id TEXT,
                        artwork_path TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        {constraints}
                    )
                    """
                )
                cursor.execute(
                    f"INSERT INTO playlist_items_new ({listed}) "
                    f"SELECT {listed} FROM playlist_items"
                )
                cursor.execute("DROP TABLE playlist_items")
                cursor.execute("ALTER TABLE playlist_items_new RENAME TO playlist_items")
                raw.commit()
            except Exception:
                raw.rollback()
                raise
            finally:
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
        finally:
            raw.close()
        log.info("Database upgraded: playlist songs may have no program")
        return True

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
