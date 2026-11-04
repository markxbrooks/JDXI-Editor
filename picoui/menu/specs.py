from dataclasses import dataclass


@dataclass
class Separator:
    """Insert a separator when building menus or toolbars from layout."""


@dataclass
class SubMenu:
    """Nested menu with a recursive item list (same entry types as top-level)."""

    title: str
    items: list


@dataclass
class NamedMenu:
    """Insert a pre-built ``QMenu`` stored on the host as ``attr``."""

    attr: str


@dataclass
class RecentFilesMenu(NamedMenu):
    """Named menu at ``recent_files_menu`` (filled by the host)."""

    attr: str = "recent_files_menu"


@dataclass
class RecentDensityMapsMenu(NamedMenu):
    """Named menu at ``recent_density_maps_menu`` (filled by the host)."""

    attr: str = "recent_density_maps_menu"
