"""
Song artwork for the playlist.

A track's cover is the image set on it, if that file still exists. Otherwise
it is found beside the track's MIDI file: an image with the same name
(``blue_monday.jpg`` for ``blue_monday.mid``), else a folder image
(``cover``, ``folder``, ``front`` or ``album``), as music players do.
"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif")
FOLDER_IMAGE_NAMES = ("cover", "folder", "front", "album")
IMAGE_FILE_FILTER = (
    "Images (" + " ".join(f"*{s}" for s in IMAGE_SUFFIXES) + ");;All Files (*)"
)

_pixmap_cache: dict = {}


def find_artwork(midi_file_path: Optional[str]) -> Optional[str]:
    """An image beside the MIDI file: same name first, then a folder image."""
    if not midi_file_path:
        return None
    midi = Path(midi_file_path)
    folder = midi.parent
    if not folder.is_dir():
        return None
    try:
        images = {
            p.name.lower(): p
            for p in folder.iterdir()
            if p.suffix.lower() in IMAGE_SUFFIXES and p.is_file()
        }
    except OSError:
        return None
    for stem in (midi.stem.lower(), *FOLDER_IMAGE_NAMES):
        for suffix in IMAGE_SUFFIXES:
            hit = images.get(stem + suffix)
            if hit is not None:
                return str(hit)
    return None


def track_artwork(artwork_path: Optional[str], midi_file_path: Optional[str]) -> Optional[str]:
    """The cover to show for a track: the one set on it, else one found."""
    if artwork_path and Path(artwork_path).is_file():
        return artwork_path
    return find_artwork(midi_file_path)


def artwork_pixmap(path: Optional[str], size: int) -> Optional[QPixmap]:
    """`path` scaled to fit a `size` square (None if it cannot be read)."""
    if not path:
        return None
    try:
        mtime = Path(path).stat().st_mtime
    except OSError:
        return None
    key = (path, mtime, size)
    if key not in _pixmap_cache:
        pixmap = QPixmap(path)
        _pixmap_cache[key] = (
            None
            if pixmap.isNull()
            else pixmap.scaled(
                size,
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
    return _pixmap_cache[key]
