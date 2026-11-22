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
                log.info(
                    f"✅ Created playlist: {name} (ID: {playlist_id})",
                    scope="PlaylistORM",
                )
                return playlist_id
        except Exception as e:
            log.error(f"❌Failed to create playlist '{name}': {e}", scope="PlaylistORM")
            import traceback

            log.error(traceback.format_exc())
            return None

    def duplicate_playlist(self, playlist_id: int, new_name: str) -> Optional[int]:
        """
        Copy a playlist under a new name, with its description and every item
        (program, MIDI file, cheat preset) in the same order.

        :param playlist_id: Playlist to copy
        :param new_name: Name of the copy (playlist names are unique)
        :return: The new playlist's ID, or None if it could not be created
        """
        try:
            with self.db_session.get_session() as session:
                source = session.query(PlayList).filter_by(id=playlist_id).first()
                if not source:
                    log.error(scope="PlaylistORM", message=f"Playlist {playlist_id} not found")
                    return None
                copy = PlayList(name=new_name, description=source.description)
                session.add(copy)
                session.flush()
                items = (
                    session.query(PlaylistItem)
                    .filter_by(playlist_id=playlist_id)
                    .order_by(PlaylistItem.position)
                    .all()
                )
                for position, item in enumerate(items, start=1):
                    session.add(
                        PlaylistItem(
                            playlist_id=copy.id,
                            program_id=item.program_id,
                            position=position,
                            midi_file_path=item.midi_file_path,
                            cheat_preset_id=item.cheat_preset_id,
                            artwork_path=item.artwork_path,
                        )
                    )
                new_id = copy.id
                log.info(scope="PlaylistORM", message=f"✅ Duplicated playlist {playlist_id} as '{new_name}' ({new_id})")
                return new_id
        except Exception as e:
            log.error(scope="PlaylistORM", message=f"❌ Failed to duplicate playlist {playlist_id}: {e}")
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
            log.error(scope="PlaylistORM", message=f"Error loading playlists: {e}")
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
            log.error(
                scope="PlaylistORM",
                message=f"Error getting playlist {playlist_id}: {e}",
            )
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
                    log.error(
                        scope="PlaylistORM", message=f"Playlist {playlist_id} not found"
                    )
                    return False

                if name is not None:
                    playlist.name = name
                if description is not None:
                    playlist.description = description

                log.info(f"✅ Updated playlist {playlist_id}", scope="PlaylistORM")
                return True
        except Exception as e:
            log.error(
                f"❌Failed to update playlist {playlist_id}: {e}", scope="PlaylistORM"
            )
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
                    log.info(f"✅Deleted playlist {playlist_id}", scope="PlaylistORM")
                    return True
                return False
        except Exception as e:
            log.error(
                f"❌Failed to delete playlist {playlist_id}: {e}", scope="PlaylistORM"
            )
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
                    log.error(
                        scope="PlaylistORM", message=f"Playlist {playlist_id} not found"
                    )
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
                        f"⚠️Program {program_id} already in playlist {playlist_id} at position {position}",
                        scope="PlaylistORM",
                    )
                    return False

                # Create new playlist item
                item = PlaylistItem(
                    playlist_id=playlist_id, program_id=program_id, position=position
                )
                session.add(item)
                log.info(
                    f"✅ Added program {program_id} to playlist {playlist_id} at position {position}",
                    scope="PlaylistORM",
                )
                return True
        except Exception as e:
            log.error(
                f"❌Failed to add program {program_id} to playlist {playlist_id}: {e}",
                scope="PlaylistORM",
            )
            import traceback

            log.error(traceback.format_exc())
            return False

    def add_song_to_playlist(
        self, playlist_id: int, midi_file_path: str, position: Optional[int] = None
    ) -> bool:
        """
        Append a song that is only a MIDI file.

        :param playlist_id: Playlist ID
        :param midi_file_path: Path of the MIDI file
        :param position: Position in the playlist (appended when omitted)
        :return: True if the song was added
        """
        try:
            with self.db_session.get_session() as session:
                playlist = session.query(PlayList).filter_by(id=playlist_id).first()
                if not playlist:
                    log.error(scope="PlaylistORM", message=f"Playlist {playlist_id} not found")
                    return False
                if position is None:
                    position = self._next_position(session, playlist_id)
                item = PlaylistItem(
                    playlist_id=playlist_id,
                    program_id=None,
                    position=position,
                    midi_file_path=midi_file_path,
                )
                session.add(item)
                log.info(
                    f"✅ Added song {midi_file_path} to playlist {playlist_id} at position {position}",
                    scope="PlaylistORM",
                )
                return True
        except Exception as e:
            log.error(
                f"❌Failed to add song to playlist {playlist_id}: {e}",
                scope="PlaylistORM",
            )
            return False

    def set_item_program(self, item_id: int, program_id: Optional[str]) -> bool:
        """
        Set or clear the JD-Xi program on one song.

        :param item_id: Playlist item ID
        :param program_id: Program ID, or None to clear it
        :return: True if the song was updated
        """
        try:
            with self.db_session.get_session() as session:
                item = session.query(PlaylistItem).filter_by(id=item_id).first()
                if not item:
                    return False
                item.program_id = program_id or None
                log.info(
                    f"✅ Song {item_id} program is {item.program_id or 'cleared'}",
                    scope="PlaylistORM",
                )
                return True
        except Exception as e:
            log.error(f"❌Failed to set program on song {item_id}: {e}", scope="PlaylistORM")
            return False

    @staticmethod
    def _next_position(session, playlist_id: int) -> int:
        """The position after the last song in the playlist (1 when it is empty)."""
        max_item = (
            session.query(PlaylistItem)
            .filter_by(playlist_id=playlist_id)
            .order_by(PlaylistItem.position.desc())
            .first()
        )
        return (max_item.position + 1) if max_item else 1

    @staticmethod
    def _find_item(session, playlist_id: int, program_id: Optional[str], item_id: Optional[int]):
        """The playlist item to act on. A program can be in a playlist more than
        once (one entry per MIDI file), so `item_id` picks the exact entry; without
        it, the first entry for the program is used (older callers)."""
        query = session.query(PlaylistItem).filter_by(playlist_id=playlist_id)
        if item_id is not None:
            return query.filter_by(id=item_id).first()
        return query.filter_by(program_id=program_id).order_by(PlaylistItem.position).first()

    def remove_program_from_playlist(
        self, playlist_id: int, program_id: str, item_id: Optional[int] = None
    ) -> bool:
        """
        Remove a program from a playlist.

        :param playlist_id: Playlist ID
        :param program_id: Program ID
        :param item_id: Playlist item ID, to remove one specific entry when the
            program is in the playlist more than once
        :return: True if successful, False otherwise
        """
        try:
            with self.db_session.get_session() as session:
                item = self._find_item(session, playlist_id, program_id, item_id)
                if item:
                    session.delete(item)
                    log.info(
                        f"✅ Removed program {program_id} from playlist {playlist_id}",
                        scope="PlaylistORM",
                    )
                    return True
                return False
        except Exception as e:
            log.error(
                f"❌Failed to remove program {program_id} from playlist {playlist_id}: {e}",
                scope="PlaylistORM",
            )
            import traceback

            log.error(traceback.format_exc())
            return False

    def reorder_playlist(self, playlist_id: int, item_ids: List[int]) -> bool:
        """
        Save a new order for a playlist: `item_ids` lists every item of the
        playlist, first to last, and positions become 1..N in that order.
        Playback follows these positions, so the order shown and the order
        played stay the same.

        Positions are rewritten in two passes (first to temporary negative
        values) so that swapping two entries never clashes with a uniqueness
        rule on (playlist, program, position) in older databases.

        :param playlist_id: Playlist ID
        :param item_ids: Playlist item IDs in their new order
        :return: True if saved; False if the list isn't exactly the playlist's items
        """
        try:
            with self.db_session.get_session() as session:
                items = session.query(PlaylistItem).filter_by(playlist_id=playlist_id).all()
                by_id = {item.id: item for item in items}
                if len(item_ids) != len(by_id) or set(item_ids) != set(by_id):
                    log.warning(
                        scope="PlaylistORM",
                        message=f"Reorder of playlist {playlist_id} ignored: the item list does not match its items",
                    )
                    return False
                for temp, item in enumerate(items, start=1):
                    item.position = -temp
                session.flush()
                for position, item_id in enumerate(item_ids, start=1):
                    by_id[item_id].position = position
                log.info(scope="PlaylistORM", message=f"✅ Reordered playlist {playlist_id}")
                return True
        except Exception as e:
            log.error(scope="PlaylistORM", message=f"❌ Failed to reorder playlist {playlist_id}: {e}")
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
                            "item_id": item.id,
                            "position": item.position,
                            "program_id": item.program_id,
                            "program": program,
                            "midi_file_path": item.midi_file_path,
                            "cheat_preset_id": item.cheat_preset_id,
                            "artwork_path": item.artwork_path,
                        }
                    )
                return result
        except Exception as e:
            log.error(
                scope="PlaylistORM",
                message=f"Error loading programs for playlist {playlist_id}: {e}",
            )
            import traceback

            log.error(traceback.format_exc())
            return []

    def update_playlist_item_midi_file(
        self,
        playlist_id: int,
        program_id: Optional[str],
        midi_file_path: Optional[str],
        item_id: Optional[int] = None,
    ) -> bool:
        """
        Update the MIDI file path for a playlist item.

        :param playlist_id: Playlist ID
        :param program_id: Program ID
        :param midi_file_path: Path to MIDI file (or None to clear)
        :param item_id: Playlist item ID (the exact entry when the program is
            used more than once)
        :return: True if successful, False otherwise
        """
        try:
            with self.db_session.get_session() as session:
                item = self._find_item(session, playlist_id, program_id, item_id)
                if item:
                    item.midi_file_path = midi_file_path
                    log.info(
                        f"✅ Updated MIDI file for playlist {playlist_id}, program {program_id}",
                        scope="PlaylistORM",
                    )
                    return True
                return False
        except Exception as e:
            log.error(
                f"❌Failed to update MIDI file for playlist {playlist_id}, program {program_id}: {e}",
                scope="PlaylistORM",
            )
            import traceback

            log.error(traceback.format_exc())
            return False

    def update_playlist_item_artwork(
        self, playlist_id: int, item_id: int, artwork_path: Optional[str] = None
    ) -> bool:
        """
        Set the cover image of one playlist entry.

        :param playlist_id: Playlist ID
        :param item_id: Playlist item ID
        :param artwork_path: Image file path, or None to clear
        :return: True if the entry was found and updated
        """
        try:
            with self.db_session.get_session() as session:
                item = (
                    session.query(PlaylistItem)
                    .filter_by(id=item_id, playlist_id=playlist_id)
                    .first()
                )
                if not item:
                    return False
                item.artwork_path = artwork_path or None
                log.info(
                    f"✅ Updated artwork for playlist {playlist_id}, item {item_id}",
                    scope="PlaylistORM",
                )
                return True
        except Exception as e:
            log.error(
                f"❌ Failed to update artwork for playlist {playlist_id}, item {item_id}: {e}",
                scope="PlaylistORM",
            )
            return False

    def update_playlist_item_cheat_preset(
        self,
        playlist_id: int,
        program_id: Optional[str],
        cheat_preset_id: Optional[str] = None,
        item_id: Optional[int] = None,
    ) -> bool:
        """
        Update the cheat preset ID for a playlist item.

        :param playlist_id: Playlist ID
        :param program_id: Program ID
        :param cheat_preset_id: Cheat preset ID (e.g., "113") or None to clear
        :param item_id: Playlist item ID (the exact entry when the program is
            used more than once)
        :return: True if updated, False otherwise
        """
        try:
            with self.db_session.get_session() as session:
                item = self._find_item(session, playlist_id, program_id, item_id)
                if item:
                    item.cheat_preset_id = cheat_preset_id
                    log.info(
                        f"✅ Updated cheat preset for playlist {playlist_id}, program {program_id}: {cheat_preset_id}",
                        scope="PlaylistORM",
                    )
                    return True
                return False
        except Exception as e:
            log.error(
                f"❌ Failed to update cheat preset for playlist {playlist_id}, program {program_id}: {e}",
                scope="PlaylistORM",
            )
            import traceback

            log.error(traceback.format_exc())
            return False
