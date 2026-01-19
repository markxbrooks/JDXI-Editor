"""
SQLAlchemy ORM models for playlists and playlist items.

This module provides the PlayList and PlaylistItem models for managing
playlists and their associated programs in the JD-Xi Editor.
"""

from datetime import datetime
from typing import Any, Dict

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

# Import Base from base module to avoid circular imports
from jdxi_editor.core.db.base import Base


class PlayList(Base):
    """
    SQLAlchemy model for the playlists table.

    Represents a playlist containing multiple programs.
    """

    __tablename__ = "playlists"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Playlist identification
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationship to playlist items
    items = relationship(
        "PlaylistItem", back_populates="playlist", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<PlayList(id={self.id}, name='{self.name}')>"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model instance to a dictionary.

        :return: Dictionary representation of the playlist
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "program_count": len(self.items) if self.items else 0,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlayList":
        """
        Create a PlayList instance from a dictionary.

        :param data: Dictionary with playlist data
        :return: PlayList instance
        """
        # Handle timestamp strings
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        return cls(
            id=data.get("id"),
            name=data["name"],
            description=data.get("description"),
            created_at=created_at or datetime.utcnow(),
            updated_at=updated_at or datetime.utcnow(),
        )


class PlaylistItem(Base):
    """
    SQLAlchemy model for the playlist_items table.

    Represents a program within a playlist, including its position,
    MIDI file path, and cheat preset ID.
    """

    __tablename__ = "playlist_items"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    playlist_id = Column(
        Integer, ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False
    )
    program_id = Column(String, nullable=False)  # References programs.id

    # Item properties
    position = Column(Integer, nullable=False)
    midi_file_path = Column(Text)
    cheat_preset_id = Column(String)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship to playlist
    playlist = relationship("PlayList", back_populates="items")

    def __repr__(self):
        return f"<PlaylistItem(id={self.id}, playlist_id={self.playlist_id}, program_id='{self.program_id}', position={self.position})>"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model instance to a dictionary.

        :return: Dictionary representation of the playlist item
        """
        return {
            "id": self.id,
            "playlist_id": self.playlist_id,
            "program_id": self.program_id,
            "position": self.position,
            "midi_file_path": self.midi_file_path,
            "cheat_preset_id": self.cheat_preset_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlaylistItem":
        """
        Create a PlaylistItem instance from a dictionary.

        :param data: Dictionary with playlist item data
        :return: PlaylistItem instance
        """
        # Handle timestamp strings
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return cls(
            id=data.get("id"),
            playlist_id=data["playlist_id"],
            program_id=data["program_id"],
            position=data["position"],
            midi_file_path=data.get("midi_file_path"),
            cheat_preset_id=data.get("cheat_preset_id"),
            created_at=created_at or datetime.utcnow(),
        )
