"""
UI components for Transport widget.
"""

from PySide6.QtWidgets import QButtonGroup, QGroupBox, QHBoxLayout, QLabel, QPushButton

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.playback.state import MidiPlaybackState
from jdxi_editor.ui.editors.helpers.widgets import (
    create_jdxi_button_from_spec,
    create_jdxi_row,
)
from jdxi_editor.ui.widgets.editor.helper import create_group_with_layout
from jdxi_editor.ui.widgets.jdxi.midi_group import JDXiMidiGroup
from picomidi.ui.widget.transport.spec import TransportSpec


class TransportWidget(JDXiMidiGroup):
    """UI class for Transport Widget."""

    def __init__(self, parent: "MidiFilePlayer", midi_state: MidiPlaybackState = None):
        """constructor"""
        super().__init__(parent=parent, midi_state=midi_state)
        self.pause_label: QLabel | None = None
        self.play_button = QPushButton()
        self.stop_button = QPushButton()
        self.pause_button = QPushButton()
        self.setup_ui()

    def _build_group(self) -> QGroupBox:
        """init transport controls"""
        group, transport_layout = create_group_with_layout("Transport", vertical=False)
        transport_button_group = QButtonGroup(self)
        transport_button_group.setExclusive(True)

        for spec in self.specs["transport"].values():
            self._create_transport_control(
                spec, transport_layout, transport_button_group
            )

        return group

    def _build_button_specs(self) -> dict[str, TransportSpec]:
        pass

    def _build_transport_specs(self) -> dict[str, TransportSpec]:
        return {
            "play": TransportSpec(
                label="Play",
                icon=JDXi.UI.Icon.PLAY,
                tooltip="Play",
                slot=self.parent.midi_playback_start,
                grouped=True,
                name="play",
                text="Play",
            ),
            "stop": TransportSpec(
                label="Stop",
                icon=JDXi.UI.Icon.STOP,
                tooltip="Stop",
                slot=self.parent.midi_playback_stop,
                grouped=True,
                name="stop",
                text="Stop",
            ),
            "pause": TransportSpec(
                label="Pause",
                icon=JDXi.UI.Icon.PAUSE,
                tooltip="Pause",
                slot=self.parent.midi_playback_pause_toggle,
                grouped=False,
                name="pause",
                text="Pause",
            ),
        }

    def set_state(self, state: str):
        """set state"""
        self.play_button.blockSignals(True)
        self.stop_button.blockSignals(True)

        self.play_button.setChecked(state == "play")
        self.stop_button.setChecked(state == "stop")

        self.play_button.blockSignals(False)
        self.stop_button.blockSignals(False)

    def _create_transport_control(
        self,
        spec: TransportSpec,
        layout: QHBoxLayout,
        button_group: QButtonGroup | None,
    ) -> None:
        """Create a transport button + label row"""

        # ---- Button
        btn = create_jdxi_button_from_spec(spec, button_group)
        setattr(self, f"{spec.name}_button", btn)
        layout.addWidget(btn)

        # ---- Label row
        pixmap = JDXi.UI.Icon.get_icon_pixmap(
            spec.icon, color=JDXi.UI.Style.FOREGROUND, size=20
        )
        label_row, text_label = create_jdxi_row(spec.text, icon_pixmap=pixmap)
        setattr(self, f"{spec.name}_label", text_label)
        layout.addWidget(label_row)
