"""
The JD-Xi faceplate.

instrument_panel.ui is the 1000 x 230 panel, with one empty host for each
group of controls at its place on the picture. This module fills the hosts
with the display, part buttons, sliders, and step buttons, and keeps each
host on its place in the picture as the panel is stretched.
"""

from pathlib import Path

from PySide6.QtCore import QEvent, QFile, QRect, Qt, QTimer
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.core.synth.type import JDXiSynth
from jdxi_editor.ui.image.instrument import draw_instrument_pixmap
from jdxi_editor.ui.windows.jdxi.containers import (
    add_digital_display,
    add_effects_container,
    add_favorite_button_container,
    add_octave_and_arp_buttons,
    add_program_container,
    add_sequencer_container,
    add_slider_container,
    add_title_container,
    add_tone_container,
    create_parts_container,
    create_program_buttons_row,
    create_tone_buttons_row,
)
from jdxi_editor.ui.windows.jdxi.containers.sequencer import STEP_PITCH, STEPS_INSET

_UI = Path(__file__).with_name("instrument_panel.ui")

#: the hosts in instrument_panel.ui, one per group of controls
HOSTS = (
    "title_host",
    "display_host",
    "octave_arp_host",
    "parts_host",
    "program_host",
    "tone_host",
    "sliders_host",
    "effects_host",
    "favorite_host",
    "sequencer_host",
)


def load_instrument_form() -> QWidget:
    """The empty faceplate from Qt Designer."""
    loader = QUiLoader()
    file = QFile(str(_UI))
    if not file.open(QFile.OpenModeFlag.ReadOnly):
        raise OSError(f"Could not open {_UI}")
    try:
        form = loader.load(file)
    finally:
        file.close()
    if form is None:
        raise RuntimeError(f"Could not load {_UI}")
    return form


def _host(form: QWidget, name: str) -> QWidget:
    widget = form.findChild(QWidget, name)
    if widget is None:
        raise RuntimeError(f"Faceplate is missing {name}")
    return widget


class InstrumentFaceplate(QWidget):
    """The panel: the instrument picture, with the hosts laid over it."""

    def __init__(self, form: QWidget):
        super().__init__()
        self.setObjectName("instrument_faceplate")
        dimensions = JDXi.UI.Dimensions.INSTRUMENT
        self._panel_height = dimensions.PANEL_HEIGHT
        self.setFixedHeight(self._panel_height)
        self.setMinimumWidth(dimensions.WIDTH)
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(True)
        self.image_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.image_label.setPixmap(draw_instrument_pixmap())
        self.form = form
        form.setParent(self)
        self.hosts = {name: _host(form, name) for name in HOSTS}
        #: each host's rectangle on the 1000 x 230 panel, as drawn in Designer
        self.designed = {name: QRect(host.geometry()) for name, host in self.hosts.items()}
        sequencer = self.hosts["sequencer_host"]
        self._step_grid = sequencer.findChild(QGridLayout, "step_grid")
        for host in self.hosts.values():
            host.installEventFilter(self)
        self.image_label.lower()

    def scaled(self, rect: QRect) -> QRect:
        """
        ``rect`` on the 1000 x 230 panel, where it falls on this one.

        :param rect: QRect in panel design coordinates
        :return: QRect in this widget's coordinates
        """
        dimensions = JDXi.UI.Dimensions.INSTRUMENT
        sx = self.width() / dimensions.WIDTH
        sy = self.height() / dimensions.PANEL_HEIGHT
        return QRect(
            round(rect.x() * sx),
            round(rect.y() * sy),
            round(rect.width() * sx),
            round(rect.height() * sy),
        )

    def apply_width(self, width: int) -> int:
        """
        Set the panel's depth for an instrument ``width`` px wide.

        Called by the window on resize rather than from resizeEvent here,
        where setting the height is undone by the resize that is still in
        progress.

        :param width: int the instrument's width in px
        :return: int the depth it was given
        """
        wanted = JDXi.UI.Dimensions.INSTRUMENT.panel_height_for(width)
        if wanted != self._panel_height:
            self._panel_height = wanted
            self.setFixedHeight(wanted)
        return wanted

    def resizeEvent(self, event):
        self.image_label.setGeometry(self.rect())
        self.image_label.lower()
        self._place_hosts()
        super().resizeEvent(event)

    def _place_hosts(self) -> None:
        self.form.setGeometry(self.rect())
        if self._step_grid is not None:
            # The steps spread with the picture, so each stays under its
            # stretch of the measure lines; floored, so the last step cannot
            # run past the panel
            sx = self.width() / JDXi.UI.Dimensions.INSTRUMENT.WIDTH
            self._step_grid.setHorizontalSpacing(
                int(STEP_PITCH * sx) - JDXi.UI.Dimensions.SEQUENCER.SQUARE_SIZE
            )
            self.hosts["sequencer_host"].layout().setContentsMargins(round(STEPS_INSET * sx), 0, 0, 0)
        for name, host in self.hosts.items():
            host.setGeometry(self.scaled(self.designed[name]))
            layout = host.layout()
            if layout is not None:
                layout.setGeometry(host.contentsRect())
            self._mask(host)

    @staticmethod
    def _mask(host: QWidget) -> None:
        # Hosts overlap, as the groups did on the old panel. Masked to their
        # controls, a host only takes the clicks that land on one of them,
        # and the group beneath stays usable.
        try:
            region = host.childrenRegion()
        except RuntimeError:
            return
        if not region.isEmpty():
            host.setMask(region)

    def eventFilter(self, watched, event):
        if event.type() in (QEvent.Type.LayoutRequest, QEvent.Type.Resize, QEvent.Type.Show):
            QTimer.singleShot(0, lambda host=watched: self._mask(host))
        return False


def build_faceplate(window) -> InstrumentFaceplate:
    """
    Build the faceplate and attach its controls to `window`.

    :param window: JDXiWindow
    :return: InstrumentFaceplate
    """
    form = load_instrument_form()
    helper = window.midi_helper

    window.digital_display = add_digital_display(
        _host(form, "display_host"),
        window,
        digital_font_family=window.digital_font_family,
    )
    add_title_container(_host(form, "title_host"))
    window.parts_container, window.part_buttons = create_parts_container(
        _host(form, "parts_host"),
        on_open_d1=lambda: window.show_editor("digital1"),
        on_open_d2=lambda: window.show_editor("digital2"),
        on_open_drums=lambda: window.show_editor("drums"),
        on_open_analog=lambda: window.show_editor("analog"),
        on_open_arp=lambda: window.show_editor("arpeggio"),
        on_select_synth=window._select_synth,
    )
    window.synth_buttons = {
        JDXiSynth.DIGITAL_SYNTH_1: window.part_buttons["digital1"],
        JDXiSynth.DIGITAL_SYNTH_2: window.part_buttons["digital2"],
        JDXiSynth.ANALOG_SYNTH: window.part_buttons["analog"],
        JDXiSynth.DRUM_KIT: window.part_buttons["drums"],
    }
    window.arp_button = window.part_buttons["arp"]

    (
        window.octave_down,
        window.octave_up,
        window.arpeggiator_button,
        window.key_hold_button,
    ) = add_octave_and_arp_buttons(_host(form, "octave_arp_host"), window._midi_send_octave)

    window.vocal_effects_button, window.effects_button = add_effects_container(
        _host(form, "effects_host"),
        lambda: window.show_editor("vocal_fx"),
        lambda: window.show_editor("effects"),
    )

    window.program_down_button, window.program_up_button = add_program_container(
        _host(form, "program_host"), create_program_buttons_row
    )
    window.tone_down_button, window.tone_up_button = add_tone_container(
        _host(form, "tone_host"),
        create_tone_buttons_row,
        window._preset_previous,
        window._preset_next,
    )
    window.sequencer_buttons = add_sequencer_container(
        _host(form, "sequencer_host"),
        midi_helper=helper,
        on_context_menu=window._show_favorite_context_menu,
        on_save_favorite=window._save_favorite,
    )
    window.favorite_button = add_favorite_button_container(_host(form, "favorite_host"))
    window.panel_sliders = add_slider_container(_host(form, "sliders_host"), helper)

    face = InstrumentFaceplate(form)
    window.image_label = face.image_label
    return face
