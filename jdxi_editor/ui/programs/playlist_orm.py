"""
SQLAlchemy ORM-based access layer for playlists.

This module provides ORM-based methods for accessing playlists and playlist items
using SQLAlchemy, replacing the direct SQLite queries in database.py.
"""

from pathlib import Path
from typing import Dict, List, Optional

from decologr import Decologr as log
from jdxi_editor.core.db.schema.playlists import PlayList, PlaylistItem
from jdxi_editor.core.db.session import DatabaseSession


class PlaylistORM:
    """ORM-based access layer for playlists."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the PlaylistORM.

        :param db_path: Path to SQLite database file. If None, uses default location.
        """
        self.db_session = DatabaseSession(db_path)
        # Ensure tables exist
        self.db_session.create_tables()
        self.db_session.create_indexes()

    def create_playlist(
        self, name: str, description: Optional[str] = None
    ) -> Optional[int]:
        """
        Create a new playlist.

        :param name: Playlist name (must be unique)
        :param description: Optional description
        :return: Playlist ID if successful, None otherwise
        """
        try:
            with self.db_session.get_session() as session:
                playlist = PlayList(name=name, description=description)
                session.add(playlist)
                session.flush()  # Get the ID before commit
                playlist_id = playlist.id
                log.info(f"✅ Created playlist: {name} (ID: {playlist_id})")
                return playlist_id
        except Exception as e:
            log.error(f"❌ Failed to create playlist '{name}': {e}")
            import traceback

            log.error(traceback.format_exc())
            return None

    def get_all_playlists(self) -> List[Dict]:
        """
        Get all playlists.

        :return: List of playlist dictionaries
        """
        try:
            with self.db_session.get_session() as session:
                playlists = session.query(PlayList).order_by(PlayList.name).all()
                return [playlist.to_dict() for playlist in playlists]
        except Exception as e:
            log.error(f"Error loading playlists: {e}")
            import traceback

            log.error(traceback.format_exc())
            return []

    def get_playlist_by_id(self, playlist_id: int) -> Optional[Dict]:
        """
        Get a playlist by ID.

        :param playlist_id: Playlist ID
        :return: Playlist dictionary if found, None otherwise
        """
        try:
            with self.db_session.get_session() as session:
                playlist = session.query(PlayList).filter_by(id=playlist_id).first()
                if playlist:
                    return playlist.to_dict()
                return None
        except Exception as e:
            log.error(f"Error getting playlist {playlist_id}: {e}")
            return None

    def update_playlist(
        self,
        playlist_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> bool:
        """
        Update a playlist.

        :param playlist_id: Playlist ID
        :param name: New name (optional)
        :param description: New description (optional)
        :return: True if successful, False otherwise
        """
        try:
            with self.db_session.get_session() as session:
                playlist = session.query(PlayList).filter_by(id=playlist_id).first()
                if not playlist:
                    log.error(f"Playlist {playlist_id} not found")
                    return False

                if name is not None:
                    playlist.name = name
                if description is not None:
                    playlist.description = description

                log.info(f"✅ Updated playlist {playlist_id}")
                return True
        except Exception as e:
            log.error(f"❌ Failed to update playlist {playlist_id}: {e}")
            import traceback

            log.error(traceback.format_exc())
            return False

    def delete_playlist(self, playlist_id: int) -> bool:
        """
        Delete a playlist and all its items.

        :param playlist_id: Playlist ID
        :return: True if successful, False otherwise
        """
        try:
            with self.db_session.get_session() as session:
                playlist = session.query(PlayList).filter_by(id=playlist_id).first()
                if playlist:
                    session.delete(playlist)
                    log.info(f"✅ Deleted playlist {playlist_id}")
                    return True
                return False
        except Exception as e:
            log.error(f"❌ Failed to delete playlist {playlist_id}: {e}")
            import traceback

            log.error(traceback.format_exc())
            return False

    def add_program_to_playlist(
        self, playlist_id: int, program_id: str, position: Optional[int] = None
    ) -> bool:
        """
        Add a program to a playlist.

        :param playlist_id: Playlist ID
        :param program_id: Program ID (e.g., "E01")
        :param position: Position in playlist (optional, will append if not provided)
        :return: True if successful, False otherwise
        """
        try:
            with self.db_session.get_session() as session:
                # Check if playlist exists
                playlist = session.query(PlayList).filter_by(id=playlist_id).first()
                if not playlist:
                    log.error(f"Playlist {playlist_id} not found")
                    return False

                # If position not provided, get the next position
                if position is None:
                    max_item = (
                        session.query(PlaylistItem)
                        .filter_by(playlist_id=playlist_id)
                        .order_by(PlaylistItem.position.desc())
                        .first()
                    )
                    position = (max_item.position + 1) if max_item else 1

                # Check if program already exists at this position
                existing = (
                    session.query(PlaylistItem)
                    .filter_by(
                        playlist_id=playlist_id,
                        program_id=program_id,
                        position=position,
                    )
                    .first()
                )
                if existing:
                    log.warning(
                        f"⚠️ Program {program_id} already in playlist {playlist_id} at position {position}"
                    )
                    return False

                # Create new playlist item
                item = PlaylistItem(
                    playlist_id=playlist_id, program_id=program_id, position=position
                )
                session.add(item)
                log.info(
                    f"✅ Added program {program_id} to playlist {playlist_id} at position {position}"
                )
                return True
        except Exception as e:
            log.error(
                f"❌ Failed to add program {program_id} to playlist {playlist_id}: {e}"
            )
            import traceback

            log.error(traceback.format_exc())
            return False

    def remove_program_from_playlist(self, playlist_id: int, program_id: str) -> bool:
        """
        Remove a program from a playlist.

        :param playlist_id: Playlist ID
        :param program_id: Program ID
        :return: True if successful, False otherwise
        """
        try:
            with self.db_session.get_session() as session:
                item = (
                    session.query(PlaylistItem)
                    .filter_by(playlist_id=playlist_id, program_id=program_id)
                    .first()
                )
                if item:
                    session.delete(item)
                    log.info(
                        f"✅ Removed program {program_id} from playlist {playlist_id}"
                    )
                    return True
                return False
        except Exception as e:
            log.error(
                f"❌ Failed to remove program {program_id} from playlist {playlist_id}: {e}"
            )
            import traceback

            log.error(traceback.format_exc())
            return False

    def get_playlist_programs(
        self, playlist_id: int, get_program_func: Optional[callable] = None
    ) -> List[Dict]:
        """
        Get all programs in a playlist with their MIDI file paths, ordered by position.

        :param playlist_id: Playlist ID
        :param get_program_func: Optional function to get JDXiProgram by ID (for compatibility)
        :return: List of dictionaries with 'program' (JDXiProgram) and 'midi_file_path' (str)
        """
        try:
            with self.db_session.get_session() as session:
                items = (
                    session.query(PlaylistItem)
                    .filter_by(playlist_id=playlist_id)
                    .order_by(PlaylistItem.position)
                    .all()
                )

                result = []
                for item in items:
                    # Get program if function provided
                    program = None
                    if get_program_func:
                        program = get_program_func(item.program_id)

                    result.append(
                        {
                            "program": program,
                            "midi_file_path": item.midi_file_path,
                            "cheat_preset_id": item.cheat_preset_id,
                        }
                    )
                return result
        except Exception as e:
            log.error(f"Error loading programs for playlist {playlist_id}: {e}")
            import traceback

            log.error(traceback.format_exc())
            return []

    def update_playlist_item_midi_file(
        self, playlist_id: int, program_id: str, midi_file_path: Optional[str]
    ) -> bool:
        """
        Update the MIDI file path for a playlist item.

        :param playlist_id: Playlist ID
        :param program_id: Program ID
        :param midi_file_path: Path to MIDI file (or None to clear)
        :return: True if successful, False otherwise
        """
        try:
            with self.db_session.get_session() as session:
                item = (
                    session.query(PlaylistItem)
                    .filter_by(playlist_id=playlist_id, program_id=program_id)
                    .first()
                )
                if item:
                    item.midi_file_path = midi_file_path
                    log.info(
                        f"✅ Updated MIDI file for playlist {playlist_id}, program {program_id}"
                    )
                    return True
                return False
        except Exception as e:
            log.error(
                f"❌ Failed to update MIDI file for playlist {playlist_id}, program {program_id}: {e}"
            )
            import traceback

            log.error(traceback.format_exc())
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
            with self.db_session.get_session() as session:
                item = (
                    session.query(PlaylistItem)
                    .filter_by(playlist_id=playlist_id, program_id=program_id)
                    .first()
                )
                if item:
                    item.cheat_preset_id = cheat_preset_id
                    log.info(
                        f"✅ Updated cheat preset for playlist {playlist_id}, program {program_id}: {cheat_preset_id}"
                    )
                    return True
                return False
        except Exception as e:
            log.error(
                f"❌ Failed to update cheat preset for playlist {playlist_id}, program {program_id}: {e}"
            )
            import traceback

            log.error(traceback.format_exc())
            return False
