"""
picoui.skin.registry
The skins an application offers, which one is in use, and who to tell when
it changes.

A registry holds skins by id, in the order they are offered. The active skin
is read lazily from a store (QSettings, if the application gives one) the
first time it is asked for. Changing it saves the choice and calls each
listener with the new skin; that is where an application restyles itself,
so the registry knows nothing about any one application's stylesheets.

Example:
    >>> from picoui.skin import JDXiSkin, SkinRegistry
    >>> class Red(JDXiSkin):
    ...     skin_id, label = "red", "Red"
    >>> registry = SkinRegistry([JDXiSkin(), Red()], default_id="default")
    >>> seen = []
    >>> registry.add_listener(lambda skin: seen.append(skin.skin_id))
    >>> registry.set_active("red").label
    'Red'
    >>> seen, registry.get("no-such-skin").skin_id
    (['red'], 'default')
"""

from __future__ import annotations

from typing import Callable, Dict, Iterable, List, Optional, Union

from picoui.skin.base import Skin

Listener = Callable[[Skin], None]


class QSettingsStore:
    """Keeps the chosen skin's id in QSettings. Never raises: a setting is a
    convenience, not a reason to fail."""

    def __init__(self, organization: str, application: str, key: str = "ui/skin") -> None:
        self.organization = organization
        self.application = application
        self.key = key

    def load(self) -> Optional[str]:
        try:
            from PySide6.QtCore import QSettings

            value = QSettings(self.organization, self.application).value(self.key)
        except Exception:
            return None
        return str(value) if value else None

    def save(self, skin_id: str) -> None:
        try:
            from PySide6.QtCore import QSettings

            settings = QSettings(self.organization, self.application)
            settings.setValue(self.key, skin_id)
            settings.sync()
        except Exception:
            pass


class SkinRegistry:
    """Skins by id, the active one, and listeners told when it changes."""

    def __init__(
        self,
        skins: Iterable[Skin] = (),
        default_id: Optional[str] = None,
        store: Optional[QSettingsStore] = None,
    ) -> None:
        """
        :param skins: the skins, in the order they are offered
        :param default_id: the fallback for unknown ids; the first skin if None
        :param store: where the choice is remembered; None remembers nothing
        """
        self.skins: Dict[str, Skin] = {}
        self.default_id = default_id
        self.store = store
        self._active: Optional[Skin] = None
        # The stored choice, while it names a skin not registered yet (one
        # loaded later, such as a user's skin from a file)
        self._wanted: Optional[str] = None
        self._listeners: List[Listener] = []
        for skin in skins:
            self.register(skin)

    # --- The skins ----------------------------------------------------------

    def register(self, skin: Skin) -> Skin:
        """
        Offer `skin` (replacing one with the same id); returns it.

        If the stored choice named this skin before it was registered, it
        becomes the active skin now, so a skin loaded after start-up (from
        a user's file) is still the one remembered. Listeners are not told:
        this happens while the application starts.
        """
        self.skins[skin.skin_id] = skin
        if self._active is not None and skin.skin_id in (self._active.skin_id, self._wanted):
            self._active = skin
            self._wanted = None
        return skin

    def ids(self) -> List[str]:
        return list(self.skins)

    @property
    def default(self) -> Skin:
        if self.default_id in self.skins:
            return self.skins[self.default_id]
        if not self.skins:
            self.register(Skin())
        return next(iter(self.skins.values()))

    def get(self, skin_id: Optional[str]) -> Skin:
        """The skin `skin_id` names, falling back to the default."""
        return self.skins.get(str(skin_id), self.default)

    def resolve(self, skin: Union[str, Skin, None]) -> Skin:
        """A skin, from a skin, its id, or None (the default)."""
        return skin if isinstance(skin, Skin) else self.get(skin)

    # --- The active skin ----------------------------------------------------

    def active(self) -> Skin:
        """The skin in use: the stored choice the first time, else the default."""
        if self._active is None:
            stored = self.store.load() if self.store else None
            self._active = self.get(stored)
            if stored and str(stored) not in self.skins:
                self._wanted = str(stored)
        return self._active

    def set_active(
        self, skin: Union[str, Skin], *, remember: bool = True, notify: bool = True
    ) -> Skin:
        """
        Use `skin` (or the skin with that id) from now on.

        :param skin: str, Skin
        :param remember: save the choice in the store
        :param notify: tell the listeners (e.g. restyle the application)
        :return: the skin now in use
        """
        self._active = self.resolve(skin)
        self._wanted = None
        if remember and self.store is not None:
            self.store.save(self._active.skin_id)
        if notify:
            for listener in list(self._listeners):
                listener(self._active)
        return self._active

    def add_listener(self, listener: Listener) -> None:
        """Call `listener(skin)` whenever the active skin changes."""
        if listener not in self._listeners:
            self._listeners.append(listener)

    def remove_listener(self, listener: Listener) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)


#: The registry widgets use when they are not given one
_default_registry: Optional[SkinRegistry] = None


def default_registry() -> SkinRegistry:
    """The application's registry (one with the plain base skin until set)."""
    global _default_registry
    if _default_registry is None:
        _default_registry = SkinRegistry([Skin()])
    return _default_registry


def set_default_registry(registry: SkinRegistry) -> SkinRegistry:
    """Make `registry` the one widgets follow when not given their own."""
    global _default_registry
    _default_registry = registry
    return registry
