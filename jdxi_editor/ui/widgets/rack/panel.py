"""
Rack panel
==========

A container that paints a faceplate behind whatever it is given, in the style
of a rack-mounted synth.

The panel holds no look of its own: a :class:`~jdxi_editor.ui.style.rack_skin.RackSkin`
paints it and says how much room that costs, and the content gets the rest.
Its default is the shiny black panel the editors already use, so wrapping
something changes nothing until another skin is chosen::

    panel = RackPanel(my_controls)              # looks as it does today
    panel = RackPanel(my_controls, skin="jdxi_rack")   # ears, screws, stripe

Passing no skin follows :func:`~jdxi_editor.ui.style.rack_skin.active_skin`,
so the panel changes with the application's setting; naming one pins it.
"""

from __future__ import annotations

from typing import Optional, Union

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter, QPaintEvent
from PySide6.QtWidgets import QVBoxLayout, QWidget

from jdxi_editor.ui.style.rack_skin import RackSkin, active_skin, skin_by_id


class RackPanel(QWidget):
    """A panel wearing a rack skin, with one widget of content inside it."""

    def __init__(
        self,
        content: Optional[QWidget] = None,
        skin: Optional[Union[str, RackSkin]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        :param content: Optional[QWidget] what the faceplate frames
        :param skin: Optional[str | RackSkin] a skin or its id; None follows
            the application's setting
        :param parent: Optional[QWidget] Qt parent
        """
        super().__init__(parent)
        self._pinned_skin: Optional[RackSkin] = None if skin is None else _as_skin(skin)
        self._content: Optional[QWidget] = None
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._apply_margins()
        if content is not None:
            self.set_content(content)

    @property
    def skin(self) -> RackSkin:
        """
        The skin this panel is drawn with.

        :return: RackSkin the pinned skin, or the application's
        """
        return self._pinned_skin if self._pinned_skin is not None else active_skin()

    def set_skin(self, skin: Optional[Union[str, RackSkin]]) -> None:
        """
        Pin this panel to ``skin``, or follow the application again.

        :param skin: Optional[str | RackSkin] a skin or its id; None to follow
            the application's setting
        :return: None
        """
        self._pinned_skin = None if skin is None else _as_skin(skin)
        self._apply_margins()
        self.update()

    def content(self) -> Optional[QWidget]:
        """
        The widget inside the faceplate.

        :return: Optional[QWidget]
        """
        return self._content

    def set_content(self, content: QWidget) -> None:
        """
        Put ``content`` in the faceplate, replacing anything already there.

        :param content: QWidget
        :return: None
        """
        if self._content is content:
            return
        if self._content is not None:
            self._layout.removeWidget(self._content)
            self._content.setParent(None)
        self._content = content
        self._layout.addWidget(content)

    def refresh_skin(self) -> None:
        """
        Take up the application's current skin.

        Only needed for a panel following the application when the skin
        changed while it was not visible.

        :return: None
        """
        self._apply_margins()
        self.update()

    def _apply_margins(self) -> None:
        """
        Give the chrome the room its skin asks for, and the rest to the content.

        :return: None
        """
        self._layout.setContentsMargins(self.skin.content_margins())

    def paintEvent(self, _event: QPaintEvent) -> None:
        """
        Paint the faceplate behind the content.

        :param _event: QPaintEvent
        :return: None
        """
        painter = QPainter(self)
        if not painter.isActive():
            return
        # Half a pixel in, so the 1px rim lands on the panel and is not
        # clipped by its own edge
        self.skin.paint(painter, QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5))


def _as_skin(skin: Union[str, RackSkin]) -> RackSkin:
    """
    A skin, from a skin or its id.

    :param skin: str | RackSkin
    :return: RackSkin
    """
    return skin_by_id(skin) if isinstance(skin, str) else skin
