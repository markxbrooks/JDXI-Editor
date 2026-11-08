"""
Action registry and declarative menu/toolbar builders.

Mixin for ``QMainWindow`` / ``QWidget`` hosts. Apps declare ``ActionSpec``s,
register them by key, then populate menus and toolbars from layout lists.
"""

from __future__ import annotations

from typing import Iterable

from picoui.icons import IconRegistry
from picoui.menu.specs import NamedMenu, Separator, SubMenu
from picoui.specs.widgets import ActionSpec
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QToolBar, QWidget


class ActionHost:
    """Mixin that owns ``self.actions`` and builds menus/toolbars from layouts."""

    actions: dict[str, QAction]

    def _ensure_actions(self) -> dict[str, QAction]:
        actions = getattr(self, "actions", None)
        if actions is None:
            self.actions = {}
        return self.actions

    def register_action(self, key: str, spec: ActionSpec) -> QAction:
        """Create a ``QAction`` from ``spec`` and store it as ``self.actions[key]``."""
        action = self.action_from_spec(spec)
        self._ensure_actions()[key] = action
        return action

    def action_from_spec(self, spec: ActionSpec) -> QAction:
        """Build a ``QAction`` from an ``ActionSpec``."""
        parent = self if isinstance(self, QWidget) else None
        qicon = getattr(spec, "qicon", None)
        if qicon is not None:
            action = QAction(qicon, spec.text, parent)
        elif spec.icon:
            icon = IconRegistry.get_icon_safe(spec.icon)
            action = QAction(icon if icon is not None else QIcon(), spec.text, parent)
        else:
            action = QAction(spec.text, parent)
        if spec.shortcut is not None:
            action.setShortcut(spec.shortcut)
        if spec.status:
            action.setStatusTip(spec.status)
        if spec.shortcut_context is not None:
            action.setShortcutContext(spec.shortcut_context)
        if spec.checkable:
            action.setCheckable(True)
            if spec.checked is not None:
                action.setChecked(spec.checked)
        if spec.enabled is not None:
            action.setEnabled(spec.enabled)
        if spec.triggered is not None:
            action.triggered.connect(spec.triggered)
        if spec.toggled is not None:
            action.toggled.connect(spec.toggled)
        return action

    def attach_menu_to_action(self, action_key: str, layout: Iterable) -> QMenu:
        """Build a ``QMenu`` from ``layout`` and attach it to a registered action."""
        parent = self if isinstance(self, QWidget) else None
        menu = QMenu(parent)
        self.build_menu(menu, layout)
        self._ensure_actions()[action_key].setMenu(menu)
        return menu

    def _check_condition(self, name: str) -> bool:
        """Override to gate ``("conditional", name, keys)`` layout entries."""
        return True

    def _add_toolbar_widget(self, toolbar: QToolBar, slot: str) -> None:
        """Override to inject widgets for ``("widget", slot)`` toolbar entries."""
        raise ValueError(f"Unknown toolbar widget slot: {slot!r}")

    def _handle_menu_tuple(self, menu: QMenu, kind: str, data: tuple) -> bool:
        """Handle app-specific menu tuple kinds. Return True if consumed."""
        return False

    def _handle_toolbar_tuple(self, toolbar: QToolBar, kind: str, data: tuple) -> bool:
        """Handle app-specific toolbar tuple kinds. Return True if consumed."""
        return False

    def build_menu(self, menu: QMenu, layout: Iterable) -> None:
        """Populate ``menu`` from a declarative layout."""
        actions = self._ensure_actions()
        for item in layout:
            if isinstance(item, Separator):
                menu.addSeparator()
            elif isinstance(item, NamedMenu):
                named = getattr(self, item.attr, None)
                if named is None:
                    raise AttributeError(
                        f"{type(self).__name__} has no menu attribute {item.attr!r}"
                    )
                menu.addMenu(named)
            elif isinstance(item, SubMenu):
                parent = self if isinstance(self, QWidget) else None
                submenu = QMenu(item.title, parent)
                menu.addMenu(submenu)
                self.build_menu(submenu, item.items)
            elif isinstance(item, tuple):
                kind, *data = item
                if kind == "actions":
                    for key in data[0]:
                        menu.addAction(actions[key])
                elif kind == "conditional":
                    condition, keys = data[0], data[1]
                    if self._check_condition(condition):
                        for key in keys:
                            menu.addAction(actions[key])
                elif self._handle_menu_tuple(menu, kind, tuple(data)):
                    continue
                else:
                    raise ValueError(f"Unknown menu layout tuple kind: {kind!r}")
            else:
                raise TypeError(f"Unknown menu layout item: {item!r}")

    def build_toolbar(self, toolbar: QToolBar, layout: list) -> None:
        """Populate ``toolbar`` from a declarative layout."""
        actions = self._ensure_actions()
        for item in layout:
            if isinstance(item, Separator):
                toolbar.addSeparator()
            elif isinstance(item, tuple):
                kind, *data = item
                if kind == "actions":
                    for key in data[0]:
                        toolbar.addAction(actions[key])
                elif kind == "conditional":
                    condition, keys = data[0], data[1]
                    if self._check_condition(condition):
                        for key in keys:
                            toolbar.addAction(actions[key])
                elif kind == "widget":
                    self._add_toolbar_widget(toolbar, data[0])
                elif self._handle_toolbar_tuple(toolbar, kind, tuple(data)):
                    continue
                else:
                    raise ValueError(f"Unknown toolbar layout tuple kind: {kind!r}")
            else:
                raise TypeError(f"Unknown toolbar layout item: {item!r}")
