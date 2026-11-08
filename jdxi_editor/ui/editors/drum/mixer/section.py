"""
Drum Kit Mixer widget.

Provides 37 vertical sliders for controlling the master level and
all 36 drum partial levels. Uses ChannelStrip (slider + label + icon + mute)
for consistency with the program mixer.
"""

from typing import Callable, Dict, Optional

from decologr import Decologr as log
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
)

from jdxi_editor.midi.data.address.address import (
    JDXiSysExAddress,
    JDXiSysExAddressStartMSB,
    JDXiSysExOffsetProgramLMB,
    JDXiSysExOffsetTemporaryToneUMB,
)
from jdxi_editor.midi.data.drum.data import DRUM_PARTIAL_NAMES
from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParam
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.common import JDXi, QVBoxLayout, QWidget
from jdxi_editor.ui.editors.drum.mixer.lane import MixerLane
from jdxi_editor.ui.editors.drum.mixer.spec import DRUM_MIXER_LANE_ROWS
from jdxi_editor.ui.editors.program.channel_strip import ChannelStrip
from jdxi_editor.ui.editors.helpers.widgets import create_panel
from jdxi_editor.ui.style.editor_style import mark_sheen
from jdxi_editor.ui.widgets.digital.title import DigitalTitle
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.slider import Slider
from picomidi.sysex.parameter.address import AddressParameter

# Kit layout: lane names from DRUM_MIXER_LANE_ROWS
KIT_CENTRE_ROWS = (("Hi-Hat", "Cymbals"), ("Snare", "Toms"), ("Kick",))
KIT_LEFT = ("Percussion", 2)  # (lane, strip columns): stands as tall as the kit
KIT_RIGHT = ("Other", 1)
KIT_SPACING = 12
SLIDER_HEIGHT = 130
STRIP_WIDTH = 52
MASTER_STRIP_WIDTH = 64
ICON_SIZE = 20


class DrumKitMixerSection(SectionBaseWidget):
    """
    Drum Kit Mixer widget with 37 vertical sliders:
    - 1 Master slider (Kit Level)
    - 36 Partial sliders (one for each drum partial)
    address: JDXiSysExAddress,
    """

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        create_parameter_slider: Callable = None,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize the Drum Kit Mixer.

        :param midi_helper: Optional MIDI helper for sending messages
        :param parent: Optional parent widget
        """
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.mixer_sliders: Dict[str, Slider] = {}
        self.partial_addresses: Dict[int, JDXiSysExAddress] = {}
        self._create_parameter_slider = create_parameter_slider
        # Base address for drum kit common area
        # Base address for drum kit common area (stored for reference, not currently used)
        # Match the address used by the editor (TEMPORARY_TONE, not TEMPORARY_PROGRAM)
        self.base_address = JDXiSysExAddress(
            JDXiSysExAddressStartMSB.TEMPORARY_TONE,
            JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT,
            JDXiSysExOffsetProgramLMB.COMMON,
            0x00,
        )

        self.setup_ui()

    def _setup_ui(self):
        """So as to not provide a Tab widget"""
        pass

    def setup_ui(self) -> None:
        """
        Lay the strips out like a drum kit: hats and cymbals at the top,
        snares and toms in the middle, kicks at the bottom, percussion and
        other sounds at the sides, and the kit's master level on the left.
        """
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        self.title_label = DigitalTitle("Drum Kit Mixer")

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        kit_widget = QWidget()
        outer = QHBoxLayout(kit_widget)
        outer.setContentsMargins(0, 0, 0, 0)
        kit = QGridLayout()
        kit.setHorizontalSpacing(KIT_SPACING)
        kit.setVerticalSpacing(KIT_SPACING)
        outer.addLayout(kit)

        lanes = {lane.name: lane.partials for row in DRUM_MIXER_LANE_ROWS for lane in row}
        rows = len(KIT_CENTRE_ROWS)

        master_lane = self._create_lane_group("Kit")
        master_lane.add_strip(self._build_master_strip())
        kit.addWidget(master_lane, 0, 0, rows, 1, Qt.AlignmentFlag.AlignVCenter)

        for column, (name, columns) in ((1, KIT_LEFT), (3, KIT_RIGHT)):
            lane = self._create_lane_group(name, columns=columns)
            self._add_partial_strips(lane, lanes[name])
            kit.addWidget(lane, 0, column, rows, 1)

        for row, names in enumerate(KIT_CENTRE_ROWS):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(KIT_SPACING)
            row_layout.addStretch(1)
            for name in names:
                lane = self._create_lane_group(name)
                self._add_partial_strips(lane, lanes[name])
                row_layout.addWidget(lane, 0, Qt.AlignmentFlag.AlignTop)
            row_layout.addStretch(1)
            kit.addLayout(row_layout, row, 2)

        # Display and strips on one glossy black panel, as large as its
        # contents and centred; the families inside it draw as flat sections.
        # The scroll area around it only scrolls in a window smaller than the kit.
        self.panel = create_panel(self.title_label, kit_widget)
        self.panel.setContentsMargins(12, 12, 12, 12)
        self.panel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        mark_sheen(self.panel)
        page = QWidget()
        page_layout = QHBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(self.panel, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        scroll_area.setWidget(page)
        main_layout.addWidget(scroll_area)

    def _add_partial_strips(self, lane: MixerLane, partials: list[str]) -> None:
        for partial in partials:
            strip = self._build_partial_strip(partial, DRUM_PARTIAL_NAMES.index(partial))
            if strip:
                lane.add_strip(strip)

    def _send_drum_midi(
        self, param: AddressParameter, value: int, address: JDXiSysExAddress
    ) -> bool:
        """Callback for ChannelStrip mute/send. Composes and sends SysEx."""
        if not self.midi_helper:
            return False
        try:
            from jdxi_editor.midi.sysex.composer import JDXiSysExComposer

            composer = JDXiSysExComposer()
            if param == DrumPartialParam.PARTIAL_OUTPUT_LEVEL:
                address = JDXiSysExAddress(address.msb, address.umb, address.lmb, 0x00)
            message = composer.compose_message(
                address=address, param=param, value=value
            )
            self.midi_helper.send_midi_message(message)
            return True
        except Exception as ex:
            log.error(f"Error sending drum MIDI: {ex}")
            return False

    def _build_partial_strip(
        self, partial_name: str, partial_index: int
    ) -> Optional[ChannelStrip]:
        if not (1 <= partial_index <= 36):
            log.warning(
                f"Invalid partial index: {partial_index}", scope=self.__class__.__name__
            )
            return None

        from jdxi_editor.midi.data.address.address import JDXiSysExOffsetDrumKitLMB

        lmb_attr = f"DRUM_KIT_PART_{partial_index}"
        if not hasattr(JDXiSysExOffsetDrumKitLMB, lmb_attr):
            log.warning(f"No LMB found for partial {partial_index}")
            return None

        lmb_value = getattr(JDXiSysExOffsetDrumKitLMB, lmb_attr)
        address = JDXiSysExAddress(
            JDXiSysExAddressStartMSB.TEMPORARY_TONE,
            JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT,
            JDXiSysExOffsetProgramLMB(lmb_value),
            0x00,
        )
        self.partial_addresses[partial_index] = address
        slider = Slider(
            partial_name,
            min_value=0,
            max_value=127,
            initial_value=127,
            midi_helper=self.midi_helper,
            vertical=True,
            show_value_label=True,
            tooltip=f"Level for {partial_name} (0 to 127)",
        )
        slider.valueChanged.connect(
            lambda v, addr=address, pidx=partial_index: self._on_partial_level_changed(
                v, addr, pidx
            )
        )
        self.mixer_sliders[partial_name] = slider

        self._compact(slider)
        strip = ChannelStrip(
            title=partial_name,
            slider=slider,
            value_label=self._name_label(partial_name),
            icon=self._icon_label(self._partial_icon_name(partial_name)),
            param=DrumPartialParam.PARTIAL_OUTPUT_LEVEL,
            address=address,
            send_midi_callback=self._send_drum_midi,
        )
        strip.setFixedWidth(STRIP_WIDTH)
        strip.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        return strip

    def _build_master_strip(self) -> ChannelStrip:
        address = JDXiSysExAddress(
            JDXiSysExAddressStartMSB.TEMPORARY_TONE,
            JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT,
            JDXiSysExOffsetProgramLMB.COMMON,
            0x00,
        )

        slider = Slider(
            "Master",
            min_value=0,
            max_value=127,
            initial_value=127,
            midi_helper=self.midi_helper,
            vertical=True,
            show_value_label=True,
            tooltip="Master level for the entire drum kit",
        )
        slider.valueChanged.connect(
            lambda v, addr=address: self._on_master_level_changed(v, addr)
        )
        self.mixer_sliders["Master"] = slider

        self._compact(slider)
        strip = ChannelStrip(
            title="Master",
            slider=slider,
            value_label=self._name_label("MASTER"),
            icon=self._icon_label(JDXi.UI.Icon.KEYBOARD),
            param=DrumCommonParam.KIT_LEVEL,
            address=address,
            send_midi_callback=self._send_drum_midi,
        )
        strip.setFixedWidth(MASTER_STRIP_WIDTH)
        strip.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        return strip

    @staticmethod
    def _compact(slider: Slider) -> None:
        """Mixer strips name the part once, under the slider, and stand short enough for three rows."""
        slider.label.hide()
        slider.setFixedHeight(SLIDER_HEIGHT)
        slider.value_label.setMinimumWidth(0)  # "127" fits a narrow strip
        slider.value_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    @staticmethod
    def _name_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        label.setStyleSheet(
            f"color: {JDXi.UI.Style.ACCENT}; font-size: 11px; font-weight: bold;"
        )
        return label

    @staticmethod
    def _partial_icon_name(partial_name: str) -> str:
        if partial_name in ("CYM1", "CYM2", "CYM3", "CHH", "PHH", "OHH"):
            return JDXi.UI.Icon.CYMBAL
        if partial_name in ("BD1", "BD2", "BD3"):
            return JDXi.UI.Icon.KICK_DRUM_2
        return JDXi.UI.Icon.DRUM

    @staticmethod
    def _icon_label(icon_name: str) -> QLabel:
        label = QLabel()
        icon = JDXi.UI.Icon.get_icon(icon_name, color=JDXi.UI.Style.FOREGROUND)
        if icon and not icon.isNull():
            label.setPixmap(icon.pixmap(ICON_SIZE, ICON_SIZE))
        return label

    def _create_lane_group(self, title: str, columns: int = 0) -> MixerLane:
        return MixerLane(title, self, columns=columns)

    def _on_master_level_changed(self, value: int, address: JDXiSysExAddress) -> None:
        """Handle master level change."""
        if not self.midi_helper:
            return

        try:
            from jdxi_editor.midi.sysex.composer import JDXiSysExComposer

            composer = JDXiSysExComposer()
            message = composer.compose_message(
                address=address, param=DrumCommonParam.KIT_LEVEL, value=value
            )
            self.midi_helper.send_midi_message(message)
            log.message(f"Master level changed to {value}")
        except Exception as ex:
            log.error(f"Error setting master level: {ex}")

    def _on_partial_level_changed(
        self, value: int, address: JDXiSysExAddress, partial_index: int
    ) -> None:
        """Handle partial level change."""
        if not self.midi_helper:
            return

        try:
            from jdxi_editor.midi.sysex.composer import JDXiSysExComposer

            composer = JDXiSysExComposer()
            # PARTIAL_OUTPUT_LEVEL address offset is 0x16 within the partial's address space
            # This matches what the Partial Tabs use (not PARTIAL_LEVEL which is 0x0E)
            # Note: compose_message will automatically add the parameter's offset (0x16) via apply_address_offset
            # So we set LSB to 0x00 and let compose_message add the offset
            partial_address = JDXiSysExAddress(
                address.msb,
                address.umb,
                address.lmb,
                0x00,  # Base LSB - compose_message will add PARTIAL_OUTPUT_LEVEL offset (0x16)
            )

            message = composer.compose_message(
                address=partial_address,
                param=DrumPartialParam.PARTIAL_OUTPUT_LEVEL,
                value=value,
            )
            self.midi_helper.send_midi_message(message)
            log.message(f"Partial {partial_index} level changed to {value}")
        except Exception as ex:
            log.error(f"Error setting partial {partial_index} level: {ex}")
