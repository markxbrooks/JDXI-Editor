"""
SQLite database module for storing JD-Xi user programs.

This module provides a more robust storage solution than JSON files,
with proper transactions, better querying, and reduced race conditions.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List, Optional

from decologr import Decologr as log
from jdxi_editor.jdxi.program.program import JDXiProgram


class ProgramDatabase:
    """SQLite database for storing user programs."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the database.

        :param db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            from jdxi_editor.project import __package_name__

            json_folder = Path.home() / f".{__package_name__}"
            json_folder.mkdir(parents=True, exist_ok=True)
            db_path = json_folder / "user_programs.db"

        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        """Initialize the database schema if it doesn't exist."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS programs (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    genre TEXT,
                    pc INTEGER,
                    msb INTEGER,
                    lsb INTEGER,
                    tempo INTEGER,
                    measure_length INTEGER,
                    scale TEXT,
                    analog TEXT,
                    digital_1 TEXT,
                    digital_2 TEXT,
                    drums TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create index on PC for faster lookups
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_programs_pc ON programs(pc)
            """
            )

            # Create playlists table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS playlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create playlist_items table (many-to-many relationship between playlists and programs)
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS playlist_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    playlist_id INTEGER NOT NULL,
                    program_id TEXT NOT NULL,
                    position INTEGER NOT NULL,
                    midi_file_path TEXT,
                    cheat_preset_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                    FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE CASCADE,
                    UNIQUE(playlist_id, program_id, position)
                )
            """
            )

            # Add midi_file_path column if it doesn't exist (migration for existing databases)
            try:
                conn.execute(
                    "ALTER TABLE playlist_items ADD COLUMN midi_file_path TEXT"
                )
            except sqlite3.OperationalError:
                # Column already exists, ignore
                pass

            # Add cheat_preset_id column if it doesn't exist (migration for existing databases)
            try:
                conn.execute(
                    "ALTER TABLE playlist_items ADD COLUMN cheat_preset_id TEXT"
                )
            except sqlite3.OperationalError:
                # Column already exists, ignore
                pass

            # Create indexes for playlist_items
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_playlist_items_playlist_id ON playlist_items(playlist_id)
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_playlist_items_program_id ON playlist_items(program_id)
            """
            )

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper error handling."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            log.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def add_or_replace_program(self, program: JDXiProgram) -> bool:
        """
        Add or replace a program in the database.

        :param program: JDXiProgram to add or replace
        :return: True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                # Remove any existing entries with same ID only
                # Note: We don't delete by PC because PC values can overlap between banks
                # (e.g., E01 and F01 might have the same PC value)
                conn.execute(
                    """
                    DELETE FROM programs 
                    WHERE id = ?
                """,
                    (program.id,),
                )

                # Insert new program
                conn.execute(
                    """
                    INSERT INTO programs (
                        id, name, genre, pc, msb, lsb, tempo,
                        measure_length, scale, analog, digital_1, digital_2, drums
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        program.id,
                        program.name,
                        program.genre,
                        program.pc,
                        program.msb,
                        program.lsb,
                        program.tempo,
                        program.measure_length,
                        program.scale,
                        program.analog,
                        program.digital_1,
                        program.digital_2,
                        program.drums,
                    ),
                )

                conn.commit()
                log.message(
                    f"✅ Saved program to database: {program.id} - {program.name}"
                )
                return True
        except Exception as e:
            log.error(f"❌ Failed to save program {program.id}: {e}")
            return False

    def get_program_by_id(self, program_id: str) -> Optional[JDXiProgram]:
        """
        Get a program by its ID.

        :param program_id: Program ID (e.g., "E01", "F32")
        :return: JDXiProgram if found, None otherwise
        """
        try:
            with self._get_connection() as conn:
                row = conn.execute(
                    "SELECT * FROM programs WHERE id = ?", (program_id,)
                ).fetchone()

                if row:
                    return self._row_to_program(row)
                return None
        except Exception as e:
            log.error(f"Error getting program {program_id}: {e}")
            return None

    def get_all_programs(self) -> List[JDXiProgram]:
        """
        Get all programs from the database.

        :return: List of JDXiProgram objects
        """
        try:
            with self._get_connection() as conn:
                rows = conn.execute("SELECT * FROM programs ORDER BY id").fetchall()
                return [self._row_to_program(row) for row in rows]
        except Exception as e:
            log.error(f"Error loading all programs: {e}")
            return []

    def get_programs_by_bank(self, bank: str) -> List[JDXiProgram]:
        """
        Get all programs for a specific bank.

        :param bank: Bank letter (e.g., "E", "F", "G", "H")
        :return: List of JDXiProgram objects
        """
        try:
            with self._get_connection() as conn:
                # Use UPPER() to make the query case-insensitive
                pattern = f"{bank.upper()}%"
                rows = conn.execute(
                    "SELECT * FROM programs WHERE UPPER(id) LIKE UPPER(?) ORDER BY id",
                    (pattern,),
                ).fetchall()
                programs = [self._row_to_program(row) for row in rows]
                log.info(f"📊 Bank {bank}: Found {len(programs)} programs in database")
                return programs
        except Exception as e:
            log.error(f"Error loading programs for bank {bank}: {e}")
            import traceback

            log.error(traceback.format_exc())
            return []

    def delete_program(self, program_id: str) -> bool:
        """
        Delete a program from the database.

        :param program_id: Program ID to delete
        :return: True if deleted, False otherwise
        """
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM programs WHERE id = ?", (program_id,))
                conn.commit()
                return True
        except Exception as e:
            log.error(f"Error deleting program {program_id}: {e}")
            return False

    def _row_to_program(self, row: sqlite3.Row) -> JDXiProgram:
        """Convert a database row to a JDXiProgram object."""
        return JDXiProgram(
            id=row["id"],
            name=row["name"],
            genre=row["genre"],
            pc=row["pc"],
            msb=row["msb"],
            lsb=row["lsb"],
            tempo=row["tempo"],
            measure_length=row["measure_length"],
            scale=row["scale"],
            analog=row["analog"],
            digital_1=row["digital_1"],
            digital_2=row["digital_2"],
            drums=row["drums"],
        )

    # Playlist management methods
    def create_playlist(self, name: str, description: str = None) -> Optional[int]:
        """
        Create a new playlist.

        :param name: Playlist name (must be unique)
        :param description: Optional description
        :return: Playlist ID if successful, None otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO playlists (name, description)
                    VALUES (?, ?)
                """,
                    (name, description),
                )
                conn.commit()
                playlist_id = cursor.lastrowid
                log.info(f"✅ Created playlist: {name} (ID: {playlist_id})")
                return playlist_id
        except sqlite3.IntegrityError as e:
            log.error(f"❌ Playlist '{name}' already exists: {e}")
            return None
        except Exception as e:
            log.error(f"❌ Failed to create playlist '{name}': {e}")
            return None

    def get_all_playlists(self) -> List[Dict]:
        """
        Get all playlists.

        :return: List of playlist dictionaries
        """
        try:
            with self._get_connection() as conn:
                rows = conn.execute(
                    """
                    SELECT id, name, description, created_at, updated_at
                    FROM playlists
                    ORDER BY name
                """
                ).fetchall()
                return [
                    {
                        "id": row["id"],
                        "name": row["name"],
                        "description": row["description"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],
                        "program_count": self._get_playlist_program_count(row["id"]),
                    }
                    for row in rows
                ]
        except Exception as e:
            log.error(f"Error loading playlists: {e}")
            return []

    def _get_playlist_program_count(self, playlist_id: int) -> int:
        """Get the number of programs in a playlist."""
        try:
            with self._get_connection() as conn:
                count = conn.execute(
                    """
                    SELECT COUNT(*) FROM playlist_items WHERE playlist_id = ?
                """,
                    (playlist_id,),
                ).fetchone()[0]
                return count
        except Exception as e:
            log.error(f"Error getting playlist program count: {e}")
            return 0

    def get_playlist_by_id(self, playlist_id: int) -> Optional[Dict]:
        """
        Get a playlist by ID.

        :param playlist_id: Playlist ID
        :return: Playlist dictionary if found, None otherwise
        """
        try:
            with self._get_connection() as conn:
                row = conn.execute(
                    """
                    SELECT id, name, description, created_at, updated_at
                    FROM playlists
                    WHERE id = ?
                """,
                    (playlist_id,),
                ).fetchone()
                if row:
                    return {
                        "id": row["id"],
                        "name": row["name"],
                        "description": row["description"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],
                    }
                return None
        except Exception as e:
            log.error(f"Error getting playlist {playlist_id}: {e}")
            return None

    def update_playlist(
        self, playlist_id: int, name: str = None, description: str = None
    ) -> bool:
        """
        Update a playlist.

        :param playlist_id: Playlist ID
        :param name: New name (optional)
        :param description: New description (optional)
        :return: True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                updates = []
                params = []
                if name is not None:
                    updates.append("name = ?")
                    params.append(name)
                if description is not None:
                    updates.append("description = ?")
                    params.append(description)

                if not updates:
                    return False

                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(playlist_id)

                conn.execute(
                    f"""
                    UPDATE playlists
                    SET {', '.join(updates)}
                    WHERE id = ?
                """,
                    params,
                )
                conn.commit()
                log.info(f"✅ Updated playlist {playlist_id}")
                return True
        except Exception as e:
            log.error(f"❌ Failed to update playlist {playlist_id}: {e}")
            return False

    def delete_playlist(self, playlist_id: int) -> bool:
        """
        Delete a playlist and all its items.

        :param playlist_id: Playlist ID
        :return: True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))
                conn.commit()
                log.info(f"✅ Deleted playlist {playlist_id}")
                return True
        except Exception as e:
            log.error(f"❌ Failed to delete playlist {playlist_id}: {e}")
            return False

    def add_program_to_playlist(
        self, playlist_id: int, program_id: str, position: int = None
    ) -> bool:
        """
        Add a program to a playlist.

        :param playlist_id: Playlist ID
        :param program_id: Program ID (e.g., "E01")
        :param position: Position in playlist (optional, will append if not provided)
        :return: True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                # If position not provided, get the next position
                if position is None:
                    max_pos = conn.execute(
                        """
                        SELECT MAX(position) FROM playlist_items WHERE playlist_id = ?
                    """,
                        (playlist_id,),
                    ).fetchone()[0]
                    position = (max_pos or 0) + 1

                conn.execute(
                    """
                    INSERT INTO playlist_items (playlist_id, program_id, position)
                    VALUES (?, ?, ?)
                """,
                    (playlist_id, program_id, position),
                )
                conn.commit()
                log.info(
                    f"✅ Added program {program_id} to playlist {playlist_id} at position {position}"
                )
                return True
        except sqlite3.IntegrityError:
            log.warning(
                f"⚠️ Program {program_id} already in playlist {playlist_id} at position {position}"
            )
            return False
        except Exception as e:
            log.error(
                f"❌ Failed to add program {program_id} to playlist {playlist_id}: {e}"
            )
            return False

    def remove_program_from_playlist(self, playlist_id: int, program_id: str) -> bool:
        """
        Remove a program from a playlist.

        :param playlist_id: Playlist ID
        :param program_id: Program ID
        :return: True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    DELETE FROM playlist_items
                    WHERE playlist_id = ? AND program_id = ?
                """,
                    (playlist_id, program_id),
                )
                conn.commit()
                log.info(f"✅ Removed program {program_id} from playlist {playlist_id}")
                return True
        except Exception as e:
            log.error(
                f"❌ Failed to remove program {program_id} from playlist {playlist_id}: {e}"
            )
            return False

    def get_playlist_programs(self, playlist_id: int) -> List[Dict]:
        """
        Get all programs in a playlist with their MIDI file paths, ordered by position.

        :param playlist_id: Playlist ID
        :return: List of dictionaries with 'program' (JDXiProgram) and 'midi_file_path' (str)
        """
        try:
            with self._get_connection() as conn:
                rows = conn.execute(
                    """
                    SELECT pi.program_id, pi.position, pi.midi_file_path, pi.cheat_preset_id
                    FROM playlist_items pi
                    WHERE pi.playlist_id = ?
                    ORDER BY pi.position
                """,
                    (playlist_id,),
                ).fetchall()

                result = []
                for row in rows:
                    program = self.get_program_by_id(row["program_id"])
                    if program:
                        # sqlite3.Row doesn't have .get(), use dictionary access
                        # NULL values in SQLite become None in Python
                        result.append(
                            {
                                "program": program,
                                "midi_file_path": row["midi_file_path"],
                                "cheat_preset_id": row[
                                    "cheat_preset_id"
                                ],  # Will be None if NULL in DB
                            }
                        )
                return result
        except Exception as e:
            log.error(f"Error loading programs for playlist {playlist_id}: {e}")
            return []

    def update_playlist_item_midi_file(
        self, playlist_id: int, program_id: str, midi_file_path: str
    ) -> bool:
        """
        Update the MIDI file path for a playlist item.

        :param playlist_id: Playlist ID
        :param program_id: Program ID
        :param midi_file_path: Path to MIDI file (or None to clear)
        :return: True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    UPDATE playlist_items
                    SET midi_file_path = ?
                    WHERE playlist_id = ? AND program_id = ?
                """,
                    (
                        midi_file_path if midi_file_path else None,
                        playlist_id,
                        program_id,
                    ),
                )
                conn.commit()
                log.info(
                    f"✅ Updated MIDI file for playlist {playlist_id}, program {program_id}"
                )
                return True
        except Exception as e:
            log.error(
                f"❌ Failed to update MIDI file for playlist {playlist_id}, program {program_id}: {e}"
            )
            return False

    def update_playlist_item_cheat_preset(
        self, playlist_id: int, program_id: str, cheat_preset_id: Optional[str] = None
    ) -> bool:
        """
        Update the cheat preset ID for a playlist item.

        :param playlist_id: Playlist ID
        :param program_id: Program ID
        :param cheat_preset_id: Cheat preset ID (e.g., "113") or None to clear
        :return: True if updated, False otherwise
        """
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    UPDATE playlist_items
                    SET cheat_preset_id = ?
                    WHERE playlist_id = ? AND program_id = ?
                """,
                    (
                        cheat_preset_id if cheat_preset_id else None,
                        playlist_id,
                        program_id,
                    ),
                )
                conn.commit()
                log.info(
                    f"✅ Updated cheat preset for playlist {playlist_id}, program {program_id}: {cheat_preset_id}"
                )
                return True
        except Exception as e:
            log.error(
                f"❌ Failed to update cheat preset for playlist {playlist_id}, program {program_id}: {e}"
            )
            return False

    def migrate_from_json(self, json_file: Path) -> int:
        """
        Migrate programs from JSON file to SQLite database.

        :param json_file: Path to JSON file
        :return: Number of programs migrated
        """
        import json

        if not json_file.exists():
            log.warning(f"JSON file not found: {json_file}")
            return 0

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            migrated = 0
            for program_dict in data:
                try:
                    program = JDXiProgram.from_dict(program_dict)
                    if self.add_or_replace_program(program):
                        migrated += 1
                except Exception as e:
                    log.error(
                        f"Error migrating program {program_dict.get('id', 'unknown')}: {e}"
                    )

            log.message(f"✅ Migrated {migrated} programs from JSON to SQLite")
            return migrated
        except Exception as e:
            log.error(f"Error migrating from JSON: {e}")
            return 0


# Global database instance
_db_instance: Optional[ProgramDatabase] = None


def get_database() -> ProgramDatabase:
    """Get the global database instance."""
    global _db_instance
    if _db_instance is None:
        from jdxi_editor.project import __package_name__

        _db_instance = ProgramDatabase()
        # Migrate from JSON only if:
        # 1. JSON file exists AND
        # 2. Database is empty (hasn't been migrated yet)
        json_file = Path.home() / f".{__package_name__}" / "user_programs.json"
        if json_file.exists():
            # Check if database already has programs
            existing_programs = _db_instance.get_all_programs()
            if len(existing_programs) == 0:
                # Database is empty, safe to migrate
                migrated_count = _db_instance.migrate_from_json(json_file)
                if migrated_count > 0:
                    log.message(
                        f"✅ Migrated {migrated_count} programs from JSON to database on first run"
                    )
            else:
                # Database already has programs, skip migration to avoid overwriting
                log.message(
                    f"⚠️  Database already contains {len(existing_programs)} programs. Skipping JSON migration to prevent data loss."
                )
    return _db_instance
