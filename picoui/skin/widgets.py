"""
picoui.skin.widgets
Widgets that wear a skin.

- :class:`RackPanel` paints a skin's faceplate (and ears and rail) behind one
  widget of content, giving the content whatever room the skin leaves.
- :class:`RackEars` adds only the skin's ears at each end of a strip, for
  where a full faceplate would be a second one behind another.

Both follow a :class:`~picoui.skin.registry.SkinRegistry` -- the default one
unless given another -- and a panel can be pinned to one skin instead::

    panel = RackPanel(controls)               # follows the active skin
    panel = RackPanel(controls, skin="ms20")  # always this one

Call ``refresh_skin()`` (panels) or ``apply_skin()`` (ears) from a registry
listener when the active skin changes.
"""

from __future__ import annotations

from typing import Optional, Union

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter, QPaintEvent
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from picoui.skin.base import Skin
from picoui.skin.registry import SkinRegistry, default_registry


class RackPanel(QWidget):
    """A panel wearing a skin, with one widget of content inside it."""

    def __init__(
        self,
        content: Optional[QWidget] = None,
        skin: Optional[Union[str, Skin]] = None,
        parent: Optional[QWidget] = None,
        registry: Optional[SkinRegistry] = None,
    ) -> None:
        """
        :param content: what the faceplate frames
        :param skin: a skin or its id; None follows the registry's active skin
        :param parent: Qt parent
        :param registry: the skins to follow; None for the default registry
        """
        super().__init__(parent)
        self._registry = registry
        self._pinned_skin: Optional[Skin] = None if skin is None else self.registry.resolve(skin)
        self._content: Optional[QWidget] = None
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._apply_margins()
        if content is not None:
            self.set_content(content)

    @property
    def registry(self) -> SkinRegistry:
        return self._registry or default_registry()

    @property
    def skin(self) -> Skin:
        """The pinned skin, or the registry's active one."""
        return self._pinned_skin if self._pinned_skin is not None else self.registry.active()

    def set_skin(self, skin: Optional[Union[str, Skin]]) -> None:
        """Pin this panel to `skin`, or (None) follow the registry again."""
        self._pinned_skin = None if skin is None else self.registry.resolve(skin)
        self._apply_margins()
        self.update()

    def content(self) -> Optional[QWidget]:
        return self._content

    def set_content(self, content: QWidget) -> None:
        """Put `content` in the faceplate, replacing anything already there."""
        if self._content is content:
            return
        if self._content is not None:
            self._layout.removeWidget(self._content)
            self._content.setParent(None)
        self._content = content
        self._layout.addWidget(content)

    def refresh_skin(self) -> None:
        """Take up the registry's current skin (after it changed)."""
        self._apply_margins()
        self.update()

    def _apply_margins(self) -> None:
        self._layout.setContentsMargins(self.skin.content_margins())

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        if not painter.isActive():
            return
        # Half a pixel in, so the 1px rim lands on the panel and is not
        # clipped by its own edge
        self.skin.paint(painter, QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5))


class RackEars(QWidget):
    """A strip with the skin's ears at each end and content between them."""

    def __init__(
        self,
        content: QWidget,
        parent: Optional[QWidget] = None,
        registry: Optional[SkinRegistry] = None,
    ) -> None:
        super().__init__(parent)
        self._registry = registry
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.addWidget(content)
        self.apply_skin()

    @property
    def registry(self) -> SkinRegistry:
        return self._registry or default_registry()

    def apply_skin(self) -> None:
        """Leave room for the ears the active skin draws, and repaint."""
        ears = self.registry.active().ear_width
        self.layout().setContentsMargins(ears, 0, ears, 0)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        skin = self.registry.active()
        if not skin.ear_width:
            return
        painter = QPainter(self)
        if not painter.isActive():
            return
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        skin.paint_ears(painter, QRectF(self.rect()))
