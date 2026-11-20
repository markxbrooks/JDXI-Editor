"""
Skin Editor
===========

Make a skin of your own without writing a file by hand: start from any skin,
change its colours, sizes, meters and lanes, see it in a live preview, and
save it as a user skin (``~/.jdxi_editor/skins/<id>.toml``, see
:mod:`jdxi_editor.ui.style.user_skins`), which joins the JDXiSkin menu.

The window edits the skin file's tables directly, the same tables a file
holds. A field left alone is inherited from the skin it is based on, and is
not written; a field you change is written, and its reset button (↺) takes
it out again. Parts the form does not show -- a face's decorations, named
colours -- are kept as they are when an existing file is opened and saved.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from PySide6.QtCore import QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QFontDatabase, QLinearGradient, QPainter
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from picoui.skin import Skin, SkinFileError
from picoui.skin.loader import read_skin_file
from picoui.skin.spec import GradientFill
from picoui.skin.widgets import RackPanel
from picoui.skin.writer import dumps

from jdxi_editor.ui.style.rack_skin import REGISTRY, MeterStyle, active_skin
from jdxi_editor.ui.style.user_skins import (
    BUILT_IN_IDS,
    USER_SKIN_DIR,
    save_user_skin,
    skin_from_tables,
    skin_id_from_label,
    user_skin_path,
)

#: The palette fields the form offers, by table: (key, what it colours)
PALETTE_FIELDS: Dict[str, List[Tuple[str, str]]] = {
    "chassis": [
        ("body", "Body"),
        ("surface", "Control surface"),
        ("surface_alt", "Control surface, alternate"),
        ("border", "Borders"),
        ("accent", "Accent"),
    ],
    "foreground": [
        ("text", "Lettering"),
        ("text_secondary", "Quieter lettering"),
        ("rule", "Rules"),
    ],
    "lcd": [
        ("bg_edge", "Screen edge"),
        ("bg_mid", "Screen"),
        ("bg_glow", "Backlight"),
        ("text", "Characters"),
        ("text_dim", "Dim characters"),
    ],
}

#: The MIDI player's lane choices: label, and the [lanes] table (None inherits)
LANE_CHOICES: List[Tuple[str, Optional[Dict[str, Any]]]] = [
    ("Inherit", None),
    ("Plain lanes", {"cards": False}),
    ("Punched cards on walnut", {"cards": True, "backing": {"type": "wood", "stops": "walnut"}}),
    ("Punched cards on teak", {"cards": True, "backing": {"type": "wood", "stops": "teak"}}),
    ("Punched cards on honey walnut", {"cards": True, "backing": {"type": "wood", "stops": "mini_wood"}}),
    ("Punched cards on mahogany", {"cards": True, "backing": {"type": "wood", "stops": "juno_wood"}}),
    ("Punched cards on brushed aluminium", {"cards": True, "backing": {"type": "brushed", "stops": "aluminium", "grain": 4, "coverage": 0.35}}),
    ("Punched cards on gunmetal", {"cards": True, "backing": {"type": "brushed", "stops": "gunmetal", "grain": 10}}),
]

#: The sizes the form offers: key, label, largest value
SIZE_FIELDS = [("ear_width", "Cheek width", 40), ("bezel", "Bezel", 20), ("rail_height", "Rail height", 30)]


def _hex(color: Any) -> str:
    """ "#RRGGBB" from a QColor, an RGBA tuple or text."""
    if isinstance(color, QColor):
        return color.name().upper()
    if isinstance(color, tuple):
        return "#{:02X}{:02X}{:02X}".format(*color[:3])
    return QColor(str(color)).name().upper()


# --- Small widgets ------------------------------------------------------------


class ColorButton(QPushButton):
    """A swatch with its "#RRGGBB"; clicking it picks another colour."""

    colorChosen = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._color = "#000000"
        self.setMinimumWidth(110)
        self.clicked.connect(self._pick)
        self.set_color(self._color)

    def color(self) -> str:
        return self._color

    def set_color(self, color: str) -> None:
        """Show ``color`` without telling anyone."""
        self._color = _hex(color)
        ink = "#000000" if QColor(self._color).lightness() > 140 else "#FFFFFF"
        self.setText(self._color)
        self.setStyleSheet(
            f"QPushButton {{ background: {self._color}; color: {ink}; "
            "border: 1px solid #555; border-radius: 3px; padding: 3px 8px; "
            "font-family: monospace; }"
        )

    def _pick(self) -> None:
        chosen = QColorDialog.getColor(QColor(self._color), self, "Choose a colour")
        if chosen.isValid():
            self.set_color(chosen.name())
            self.colorChosen.emit(self._color)


class LcdSample(QWidget):
    """A few characters on a screen in the skin's display palette."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._lcd = None
        self.setMinimumHeight(48)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_lcd(self, lcd) -> None:
        self._lcd = lcd
        self.update()

    def paintEvent(self, _event) -> None:
        if self._lcd is None:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(self._lcd.bg_edge))
        gradient.setColorAt(0.5, QColor(self._lcd.bg_glow))
        gradient.setColorAt(1.0, QColor(self._lcd.bg_mid))
        painter.setPen(QColor(self._lcd.bg_edge))
        painter.setBrush(gradient)
        painter.drawRoundedRect(rect, 4, 4)
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(15)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(self._lcd.text))
        painter.drawText(rect.adjusted(12, 4, -12, -18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "001 JD-Xi Init")
        font.setPointSize(9)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QColor(self._lcd.text_dim))
        painter.drawText(rect.adjusted(12, 0, -12, -4), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom, "DIGITAL 1  ·  CH 1  ·  120 BPM")


class SkinPreview(QWidget):
    """A panel wearing the skin being edited, with lettering and a display."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(14, 12, 14, 18)
        self.title = QLabel("DIGITAL SYNTH 1")
        self.title.setFont(QFont(self.title.font().family(), 13, QFont.Weight.Bold))
        self.subtitle = QLabel("Oscillator · Filter · Amp")
        self.rule = QWidget()
        self.rule.setFixedHeight(1)
        self.lcd = LcdSample()
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addWidget(self.rule)
        layout.addSpacing(6)
        layout.addWidget(self.lcd)
        layout.addStretch(1)
        self.panel = RackPanel(content, skin=active_skin())
        self.panel.setMinimumSize(420, 240)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.addWidget(self.panel)
        self._body = QColor("#202020")

    def set_skin(self, skin: Skin) -> None:
        self.panel.set_skin(skin)
        foreground = skin.foreground
        self.title.setStyleSheet(f"color: {foreground.text}; background: transparent;")
        self.subtitle.setStyleSheet(f"color: {foreground.text_secondary}; background: transparent;")
        self.rule.setStyleSheet(f"background: {foreground.rule};")
        self.lcd.set_lcd(skin.lcd)
        self._body = QColor(skin.chassis.body)
        self.update()

    def paintEvent(self, _event) -> None:
        # The chassis body round the panel, as the editor's window shows it
        painter = QPainter(self)
        painter.fillRect(self.rect(), self._body)


# --- The window ---------------------------------------------------------------


class SkinEditorWindow(QMainWindow):
    """
    Edit a user skin's tables with a live preview, and save them to a file.

    :param parent: the main window
    :param wear: called with (skin, remember) to put a skin on the editor
    :param saved: called with the skin once it is saved and offered
    :param folder: where user skins are saved; :data:`USER_SKIN_DIR` if None
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        wear: Optional[Callable[[Skin, bool], None]] = None,
        saved: Optional[Callable[[Skin], None]] = None,
        folder: Optional[Path] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Skin Editor")
        self.setMinimumSize(980, 640)
        self._wear = wear
        self._saved = saved
        self._folder = USER_SKIN_DIR if folder is None else Path(folder)
        self._worn_before = active_skin()
        self._trying = False
        self._path: Optional[Path] = None  # the file opened, if any
        self._id_follows_label = True
        self._skin: Optional[Skin] = None
        self._updating = False
        self._data: Dict[str, Any] = {}
        self._rebuild = QTimer(self, singleShot=True, interval=60)
        self._rebuild.timeout.connect(self._build)
        self._build_ui()
        self.new_skin(active_skin().skin_id)

    # --- Layout -------------------------------------------------------------

    def _build_ui(self) -> None:
        self._color_buttons: Dict[Tuple[str, str], ColorButton] = {}
        self._resets: Dict[Tuple[str, str], QToolButton] = {}
        form = QWidget()
        self._form = QVBoxLayout(form)
        self._form.addWidget(self._identity_group())
        self._form.addWidget(self._sizes_group())
        for table, title in (("chassis", "Body and controls"), ("foreground", "Lettering"), ("lcd", "Display")):
            self._form.addWidget(self._palette_group(table, title))
        self._form.addWidget(self._face_group())
        self._form.addWidget(self._ear_group())
        self._form.addWidget(self._features_group())
        self._form.addStretch(1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(form)
        scroll.setMinimumWidth(430)

        self.preview = SkinPreview()
        self.toml = QPlainTextEdit(readOnly=True)
        self.toml.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        tabs = QTabWidget()
        tabs.addTab(self.preview, "Preview")
        tabs.addTab(self.toml, "File")

        splitter = QSplitter()
        splitter.addWidget(scroll)
        splitter.addWidget(tabs)
        splitter.setStretchFactor(1, 1)

        self.status = QLabel()
        self.status.setWordWrap(True)
        buttons = QHBoxLayout()
        for text, slot, tip in (
            ("New…", self._choose_new, "Start again from a skin"),
            ("Open…", self._open, "Open one of your skin files"),
            ("Try On", self._try_on, "Wear this skin in the editor without saving it"),
            ("Save", self._save, "Save to your skins folder and add it to the JDXiSkin menu"),
            ("Close", self.close, None),
        ):
            button = QPushButton(text)
            button.clicked.connect(slot)
            if tip:
                button.setToolTip(tip)
            buttons.addWidget(button)
            setattr(self, f"{text.strip('…').lower().replace(' ', '_')}_button", button)
        buttons.insertWidget(0, self.status, 1)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(splitter, 1)
        layout.addLayout(buttons)
        self.setCentralWidget(central)

    def _row(self, key: Tuple[str, str], widget: QWidget) -> QWidget:
        """A field and its reset button."""
        reset = QToolButton(text="↺")
        reset.setToolTip("Inherit this from the skin it is based on")
        reset.clicked.connect(lambda: self._reset(*key))
        self._resets[key] = reset
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget, 1)
        layout.addWidget(reset)
        return row

    def _identity_group(self) -> QGroupBox:
        group = QGroupBox("Skin")
        layout = QFormLayout(group)
        self.label_edit = QLineEdit()
        self.label_edit.textEdited.connect(self._label_edited)
        self.id_edit = QLineEdit()
        self.id_edit.setToolTip("The file name and the id the skin is remembered by")
        self.id_edit.textEdited.connect(self._id_edited)
        self.based_on = QComboBox()
        self.based_on.setToolTip("Everything you leave alone comes from this skin")
        self.based_on.currentIndexChanged.connect(self._based_on_changed)
        layout.addRow("Name", self.label_edit)
        layout.addRow("Id", self.id_edit)
        layout.addRow("Based on", self.based_on)
        return group

    def _sizes_group(self) -> QGroupBox:
        group = QGroupBox("Size")
        layout = QFormLayout(group)
        self._spins: Dict[str, QSpinBox] = {}
        for key, label, top in SIZE_FIELDS:
            spin = QSpinBox(minimum=0, maximum=top, suffix=" px")
            spin.valueChanged.connect(lambda value, k=key: self._edited("skin", k, value))
            self._spins[key] = spin
            layout.addRow(label, self._row(("skin", key), spin))
        return group

    def _palette_group(self, table: str, title: str) -> QGroupBox:
        group = QGroupBox(title)
        layout = QFormLayout(group)
        for key, label in PALETTE_FIELDS[table]:
            button = ColorButton()
            button.colorChosen.connect(lambda color, t=table, k=key: self._edited(t, k, color))
            self._color_buttons[(table, key)] = button
            layout.addRow(label, self._row((table, key), button))
        return group

    def _face_group(self) -> QGroupBox:
        group = QGroupBox("Faceplate")
        layout = QFormLayout(group)
        self.face_rim = ColorButton()
        self.face_rim.colorChosen.connect(lambda c: self._edited("face", "rim", c))
        self._color_buttons[("face", "rim")] = self.face_rim
        layout.addRow("Outline", self._row(("face", "rim"), self.face_rim))
        self.repaint_face = QCheckBox("Repaint the panel")
        self.repaint_face.setToolTip("Replace the panel's finish with a gradient of your own")
        self.repaint_face.toggled.connect(self._repaint_face_toggled)
        layout.addRow(self.repaint_face)
        self.face_stops = [ColorButton() for _ in range(3)]
        for button, label in zip(self.face_stops, ("Top", "Middle", "Bottom")):
            button.colorChosen.connect(lambda _c: self._write_face_material())
            layout.addRow(label, button)
        return group

    def _ear_group(self) -> QGroupBox:
        group = QGroupBox("Cheeks")
        layout = QFormLayout(group)
        self.ear_rim = ColorButton()
        self.ear_rim.colorChosen.connect(lambda c: self._edited("ear", "rim", c))
        self._color_buttons[("ear", "rim")] = self.ear_rim
        self.ear_screw = ColorButton()
        self.ear_screw.colorChosen.connect(lambda c: self._edited("ear", "screw", c))
        self._color_buttons[("ear", "screw")] = self.ear_screw
        layout.addRow("Outline", self._row(("ear", "rim"), self.ear_rim))
        layout.addRow("Screws", self._row(("ear", "screw"), self.ear_screw))
        self.repaint_ear = QCheckBox("Repaint the cheeks")
        self.repaint_ear.setToolTip("Replace the cheeks' material with a gradient across them")
        self.repaint_ear.toggled.connect(self._repaint_ear_toggled)
        layout.addRow(self.repaint_ear)
        self.ear_stops = [ColorButton() for _ in range(2)]
        for button, label in zip(self.ear_stops, ("Outer edge", "Inner edge")):
            button.colorChosen.connect(lambda _c: self._write_ear_material())
            layout.addRow(label, button)
        return group

    def _features_group(self) -> QGroupBox:
        group = QGroupBox("Audio Monitor and MIDI player")
        layout = QFormLayout(group)
        self.meter = QComboBox()
        self.meter.addItem("Inherit", None)
        for style, text in (
            (MeterStyle.BARS, "Bars"),
            (MeterStyle.NEEDLES, "Needle dials"),
            (MeterStyle.VINTAGE_VU, "Vintage VU meters"),
        ):
            self.meter.addItem(text, style.value)
        self.meter.currentIndexChanged.connect(self._meter_changed)
        self.lanes = QComboBox()
        for text, table in LANE_CHOICES:
            self.lanes.addItem(text, table)
        self.lanes.currentIndexChanged.connect(self._lanes_changed)
        layout.addRow("Meters", self.meter)
        layout.addRow("MIDI lanes", self.lanes)
        return group

    # --- The tables ---------------------------------------------------------

    def _table(self, name: str) -> Dict[str, Any]:
        return self._data.setdefault(name, {})

    def _edited(self, table: str, key: str, value: Any) -> None:
        if self._updating:
            return
        self._table(table)[key] = value
        self._changed()

    def _reset(self, table: str, key: str) -> None:
        values = self._data.get(table, {})
        values.pop(key, None)
        if not values and table != "skin":
            self._data.pop(table, None)
        self._changed()

    def _changed(self) -> None:
        self._rebuild.start()

    def tables(self) -> Dict[str, Any]:
        """A copy of the skin file's tables, as they would be saved."""
        return copy.deepcopy(self._data)

    def new_skin(self, based_on: str) -> None:
        """Start a new skin from ``based_on``, changing nothing yet."""
        base = REGISTRY.get(based_on)
        label = f"My {base.label}"
        self._path = None
        self._id_follows_label = True
        self._data = {"skin": {"id": self._free_id(skin_id_from_label(label)), "label": label, "based_on": base.skin_id}}
        self._build(refresh_form=True)

    def open_file(self, path: Path) -> None:
        """Edit the skin in ``path``."""
        self._data = read_skin_file(path)
        self._path = Path(path)
        self._id_follows_label = False
        self._build(refresh_form=True)

    def _free_id(self, skin_id: str) -> str:
        """``skin_id``, numbered if a skin or file already has it."""
        candidate, number = skin_id, 2
        while candidate in REGISTRY.skins or user_skin_path(candidate, self._folder).exists():
            candidate, number = f"{skin_id}_{number}", number + 1
        return candidate

    # --- Edits from the form ------------------------------------------------

    def _label_edited(self, text: str) -> None:
        self._table("skin")["label"] = text
        if self._id_follows_label:
            self._table("skin")["id"] = skin_id_from_label(text)
        self._changed()

    def _id_edited(self, text: str) -> None:
        self._id_follows_label = False
        self._table("skin")["id"] = text.strip()
        self._changed()

    def _based_on_changed(self, _index: int) -> None:
        if self._updating:
            return
        based_on = self.based_on.currentData()
        if based_on:
            self._table("skin")["based_on"] = based_on
        else:
            self._table("skin").pop("based_on", None)
        self._changed()

    def _meter_changed(self, _index: int) -> None:
        if self._updating:
            return
        value = self.meter.currentData()
        if value is None:
            self._table("skin").pop("meter", None)
        else:
            self._table("skin")["meter"] = value
        self._changed()

    def _lanes_changed(self, _index: int) -> None:
        if self._updating:
            return
        table = self.lanes.currentData()
        if table is None:
            self._data.pop("lanes", None)
        else:
            self._data["lanes"] = copy.deepcopy(table)
        self._changed()

    def _repaint_face_toggled(self, on: bool) -> None:
        if self._updating:
            return
        if on:
            self._write_face_material()
        else:
            self._reset("face", "material")

    def _write_face_material(self) -> None:
        if self._updating or not self.repaint_face.isChecked():
            return
        top, middle, bottom = (button.color() for button in self.face_stops)
        self._table("face")["material"] = {"type": "gradient", "stops": [[0.0, top], [0.5, middle], [1.0, bottom]]}
        self._changed()

    def _repaint_ear_toggled(self, on: bool) -> None:
        if self._updating:
            return
        if on:
            self._write_ear_material()
        else:
            self._reset("ear", "material")

    def _write_ear_material(self) -> None:
        if self._updating or not self.repaint_ear.isChecked():
            return
        outer, inner = (button.color() for button in self.ear_stops)
        self._table("ear")["material"] = {
            "type": "gradient", "direction": "horizontal", "stops": [[0.0, outer], [1.0, inner]],
        }
        self._changed()

    # --- Building the skin, and showing it ------------------------------------

    def _build(self, refresh_form: bool = False) -> None:
        """Make the skin from the tables; show it, or say what is wrong."""
        self.toml.setPlainText(dumps(self._data))
        problem = self._id_problem()
        try:
            skin = skin_from_tables(self._data)
        except SkinFileError as error:
            self._skin = None
            self._say(str(error), error=True)
            if refresh_form:
                self._refresh_form(None)
            return
        self._skin = skin
        self.preview.set_skin(skin)
        self._refresh_form(skin)
        if problem:
            self._say(problem, error=True)
        else:
            changed = sum(len(v) for k, v in self._data.items() if k != "skin" and isinstance(v, dict))
            changed += len([k for k in self._data.get("skin", {}) if k not in ("id", "label", "based_on")])
            self._say(f"{changed} setting{'s' if changed != 1 else ''} changed from the skin it is based on.")

    def _id_problem(self) -> Optional[str]:
        skin_id = str(self._data.get("skin", {}).get("id", ""))
        if not skin_id:
            return "Give the skin an id."
        if skin_id != skin_id_from_label(skin_id):
            return "An id uses lower-case letters, digits and _ only, such as my_tr_909."
        if skin_id in BUILT_IN_IDS:
            return f"{skin_id!r} is a built-in skin's id; choose another."
        return None

    def _say(self, text: str, error: bool = False) -> None:
        self.status.setText(text)
        self.status.setStyleSheet("color: #E04435;" if error else "")

    def _refresh_form(self, skin: Optional[Skin]) -> None:
        """Show the skin's values: changed ones bold, inherited ones plain."""
        self._updating = True
        try:
            head = self._data.get("skin", {})
            # Only when different: setting a line edit's text moves its cursor
            for edit, text in ((self.label_edit, head.get("label", "")), (self.id_edit, head.get("id", ""))):
                if edit.text() != str(text):
                    edit.setText(str(text))
            self._fill_based_on(head.get("based_on"))
            for (table, key), reset in self._resets.items():
                reset.setEnabled(key in self._data.get(table, {}))
            if skin is None:
                return
            for key, spin in self._spins.items():
                spin.setValue(int(getattr(skin, key)))
            for (table, key), button in self._color_buttons.items():
                value = self._shown_color(skin, table, key)
                button.setEnabled(value is not None)
                if value is not None:
                    button.set_color(value)
            face_material = getattr(skin.face, "material", None) if skin.face is not None else None
            self.face_rim.setEnabled(face_material is not None or "material" in self._data.get("face", {}))
            self.face_rim.setToolTip("" if self.face_rim.isEnabled() else "A glossy panel keeps its own outline; repaint the panel to set one")
            self.repaint_face.setChecked("material" in self._data.get("face", {}))
            self._fill_stops(self.face_stops, face_material, skin.chassis.body, self.repaint_face.isChecked())
            ear_material = skin.ear.material if skin.ear is not None else None
            has_ear = skin.ear is not None
            for button in (self.ear_rim, self.ear_screw):
                button.setEnabled(has_ear)
            self.repaint_ear.setChecked("material" in self._data.get("ear", {}))
            self.repaint_ear.setEnabled(skin.ear_width > 0)
            self._fill_stops(self.ear_stops, ear_material, skin.chassis.body, self.repaint_ear.isChecked())
            self.meter.setCurrentIndex(max(0, self.meter.findData(head.get("meter"))))
            lanes = self._data.get("lanes")
            index = next((i for i, (_t, table) in enumerate(LANE_CHOICES) if table == lanes), 0)
            self.lanes.setCurrentIndex(index)
            self.meter.setItemText(0, f"Inherit ({skin.meter.value.replace('_', ' ')})")
        finally:
            self._updating = False

    def _fill_based_on(self, based_on: Optional[str]) -> None:
        self.based_on.clear()
        self.based_on.addItem("Nothing: a complete skin", None)
        editing = self._data.get("skin", {}).get("id")
        for skin_id, skin in REGISTRY.skins.items():
            if skin_id != editing:
                self.based_on.addItem(skin.label, skin_id)
        self.based_on.setCurrentIndex(max(0, self.based_on.findData(based_on)))

    @staticmethod
    def _shown_color(skin: Skin, table: str, key: str) -> Optional[str]:
        if table in PALETTE_FIELDS:
            return getattr(getattr(skin, table), key)
        part = getattr(skin, table, None)
        value = getattr(part, key, None) if part is not None else None
        return None if value is None else _hex(value)

    @staticmethod
    def _fill_stops(buttons: List[ColorButton], material, fallback: str, checked: bool) -> None:
        """The repaint colours: the current gradient's, else the body's shades."""
        if isinstance(material, GradientFill):
            stops = material.stops.stops
            picks = [stops[0], stops[len(stops) // 2], stops[-1]] if len(buttons) == 3 else [stops[0], stops[-1]]
            colors = [_hex(stop.color) for stop in picks]
        else:
            body = QColor(fallback)
            shades = [body.lighter(115), body, body.darker(125)] if len(buttons) == 3 else [body.darker(115), body.lighter(110)]
            colors = [_hex(shade) for shade in shades]
        for button, color in zip(buttons, colors):
            button.set_color(color)
            button.setEnabled(checked)

    # --- Buttons --------------------------------------------------------------

    def _choose_new(self) -> None:
        from PySide6.QtWidgets import QInputDialog

        labels = [skin.label for skin in REGISTRY.skins.values()]
        ids = list(REGISTRY.skins)
        current = labels[ids.index(active_skin().skin_id)] if active_skin().skin_id in ids else labels[0]
        label, ok = QInputDialog.getItem(self, "New skin", "Start from:", labels, labels.index(current), False)
        if ok:
            self.new_skin(ids[labels.index(label)])

    def _open(self) -> None:
        self._folder.mkdir(parents=True, exist_ok=True)
        path, _filter = QFileDialog.getOpenFileName(self, "Open a skin", str(self._folder), "Skin files (*.toml)")
        if path:
            try:
                self.open_file(Path(path))
            except SkinFileError as error:
                QMessageBox.warning(self, "Skin Editor", str(error))

    def _try_on(self) -> None:
        if self._skin is None:
            return
        self._trying = True
        if self._wear is not None:
            self._wear(self._skin, False)

    def save(self) -> Optional[Path]:
        """Save the skin, offer it, and wear it; returns the file, or None."""
        problem = self._id_problem()
        if problem or self._skin is None:
            QMessageBox.warning(self, "Skin Editor", problem or self.status.text())
            return None
        path = user_skin_path(self._data["skin"]["id"], self._folder)
        if path.exists() and path != self._path:
            answer = QMessageBox.question(self, "Skin Editor", f"{path.name} already exists. Replace it?")
            if answer != QMessageBox.StandardButton.Yes:
                return None
        path = save_user_skin(self._data, self._folder)
        self._path = path
        skin = skin_from_tables(self._data)
        REGISTRY.register(skin)
        self._worn_before = skin
        self._trying = False
        self._say(f"Saved {path.name}; it is in the JDXiSkin menu.")
        if self._saved is not None:
            self._saved(skin)
        return path

    def _save(self) -> None:
        self.save()

    def closeEvent(self, event) -> None:
        # A skin tried on but not saved comes off again
        if self._trying and self._wear is not None:
            self._wear(self._worn_before, False)
        super().closeEvent(event)
