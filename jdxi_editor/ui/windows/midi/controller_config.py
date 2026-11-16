"""
MIDI controller configuration
=============================

A window for setting up a hardware controller (an Arturia MiniLab 3 or
similar) that drives the open synth editor's filter, in the same shape as
ElMo's MIDI Control tab:

- **Connection** — which ports the controller is heard on, and whether it is
  connected.
- **Monitor** — every message arriving from it, so the CC number a knob sends
  can simply be read off.
- **Mappings** — which CC drives which filter control, with **Learn** to take
  the number from the next knob that moves. Changes are saved to QSettings and
  applied to the running :class:`~jdxi_editor.ui.editors.filter_remote.FilterRemote`
  straight away, so a knob works the moment it is learnt.
- **Transport** — which buttons play, pause, stop, record, rewind and fast
  forward the MIDI File player. **Learn** adds the next button pressed (a note
  or a CC); an action can have several, e.g. the VMX8's note and CC modes.
  Saved per controller, and picked up by the player straight away.

The CC numbers a MiniLab 3 sends depend on the program loaded on the device,
so the built-in map is only a starting point; Learn is the reliable way to get
them right.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Callable, Any

from decologr import Decologr as log
from PySide6.QtCore import Qt, QTimer, QMargins
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.io.controller_map import (
    CONTROLLER_PROFILES,
    MINILAB3,
    ControllerProfile,
    FilterControl,
    TransportAction,
    TransportSpec,
    profile_by_id,
)
from jdxi_editor.midi.io.controller_settings import (
    clear_transport_specs,
    default_filter_map,
    load_filter_map,
    load_transport_specs,
    save_filter_map,
    save_transport_specs,
)
from jdxi_editor.midi.playback.transport_input import (
    notify_transport_bindings_changed,
)
from jdxi_editor.ui.style import JDXiUIStyle
from picoui.helpers.layout import create_layout_with_items
from picoui.specs.widgets import ButtonSpec
from picoui.widget.helper import create_label, create_text_edit, create_button_from_spec

#: How often the connection status is refreshed
STATUS_INTERVAL_MS = 1000

#: Lines kept in the monitor before the oldest are dropped
MONITOR_MAX_LINES = 500

#: Entry in the port list meaning "every controller port, found automatically"
AUTOMATIC_PORTS = "All controller ports (automatic)"


@dataclass(frozen=True)
class ControlLabelSpec:
    """
    How the Mappings table shows one control.

    :param control: FilterControl the control
    :param label: str human-readable name
    """

    control: FilterControl
    label: str


#: One row per control, in the order of the MiniLab 3 defaults
CONTROL_SPECS: list[ControlLabelSpec] = [
    ControlLabelSpec(FilterControl.CUTOFF, "Cutoff"),
    ControlLabelSpec(FilterControl.RESONANCE, "Resonance"),
    ControlLabelSpec(FilterControl.KEYFOLLOW, "Cutoff key follow"),
    ControlLabelSpec(FilterControl.ENV_DEPTH, "Envelope depth"),
    ControlLabelSpec(FilterControl.ENV_VELOCITY, "Envelope velocity sensitivity"),
    ControlLabelSpec(FilterControl.ENV_ATTACK, "Filter envelope attack"),
    ControlLabelSpec(FilterControl.ENV_DECAY, "Filter envelope decay"),
    ControlLabelSpec(FilterControl.ENV_SUSTAIN, "Filter envelope sustain"),
    ControlLabelSpec(FilterControl.ENV_RELEASE, "Filter envelope release"),
    ControlLabelSpec(FilterControl.EFFECT1_LEVEL, "Effect 1 level"),
    ControlLabelSpec(FilterControl.EFFECT2_LEVEL, "Effect 2 level"),
    ControlLabelSpec(FilterControl.DELAY_LEVEL, "Delay level"),
    ControlLabelSpec(FilterControl.REVERB_LEVEL, "Reverb level"),
]

#: Human-readable name for each control
CONTROL_LABELS: Dict[FilterControl, str] = {
    spec.control: spec.label for spec in CONTROL_SPECS
}

#: Human-readable name for each transport action, in table order
TRANSPORT_LABELS: Dict[TransportAction, str] = {
    TransportAction.PLAY: "Play",
    TransportAction.PAUSE: "Pause",
    TransportAction.STOP: "Stop",
    TransportAction.RECORD: "Record",
    TransportAction.REWIND: "Rewind (hold)",
    TransportAction.FAST_FORWARD: "Fast forward (hold)",
}

#: Which MiniLab 3 control sends each one by default (from midi_controllers.json)
CONTROL_SOURCES: Dict[FilterControl, str] = dict(MINILAB3.sources)


class MidiControllerDialog(QMainWindow):
    """Set up the hardware controller that drives the filter."""

    def __init__(
            self,
            external_controller=None,
            filter_remote=None,
            parent: Optional[QWidget] = None,
    ) -> None:
        """
        :param external_controller: ExternalControllerInput the controller input
        :param filter_remote: FilterRemote applying CCs to the open editor
        :param parent: Optional[QWidget] parent widget
        """
        super().__init__(parent)
        self.preset_combo: QComboBox | None = None
        self.port_combo: QComboBox | None = None
        self.setWindowTitle("MIDI Controller")
        self.setMinimumSize(640, 560)
        self.external_controller = external_controller
        self.filter_remote = filter_remote
        #: controller whose mappings are being edited; starts as the connected one
        self.profile: ControllerProfile = self.connected_profile()
        #: CC -> FilterControl being edited
        self.cc_map: Dict[int, FilterControl] = (
            dict(filter_remote.cc_map)
            if filter_remote is not None
            else load_filter_map(profile=self.profile)
        )
        # Dark editor chrome for this window only, as in the MIDI Config dialog.
        # Not qdarktheme (apply_dark_theme / apply_theme("auto")): that restyles
        # the whole application and replaces the editor's own stylesheet.
        JDXi.UI.Theme.apply_editor_style(self)
        #: the control waiting for the next CC, while learning
        self._learning: Optional[FilterControl] = None
        #: transport buttons of the controller being edited
        self.transport_specs: list[TransportSpec] = list(
            load_transport_specs(profile=self.profile)
        )
        #: the transport action waiting for the next button press, while learning
        self._learning_transport: Optional[TransportAction] = None

        central = QWidget()
        self.setCentralWidget(central)

        title = create_label(label="MIDI Controller", object_name="TitleLabel", margin=2, style_sheet=JDXiUIStyle.LABEL)
        self._create_tab_widget()
        if self.external_controller is not None:
            self.external_controller.message_received.connect(self._on_message)
            self.external_controller.ports_changed.connect(
                lambda _ports: self.refresh_ports()
            )
        _layout = create_layout_with_items(parent=central,
                                           items=[title, self.tabs],
                                           vertical=True,
                                           start_stretch=False,
                                           end_stretch=False,
                                           spacing=2,
                                           margins=QMargins(2, 2, 2, 2))
        self.refresh_ports()
        self.update_status()
        self._status_timer: QTimer | None = None
        self._timer_init()

    def _timer_init(self):
        self._status_timer = QTimer(self)
        self._status_timer.setInterval(STATUS_INTERVAL_MS)
        self._status_timer.timeout.connect(self.update_status)
        self._status_timer.start()

    def _create_tab_widget(self):
        self.tabs = QTabWidget()
        tab_dict = self.build_tabs_dict()
        for tab_func, label in tab_dict.items():
            self.tabs.addTab(tab_func(), label)

    def build_tabs_dict(self) -> dict[Callable[[...], Any], str]:
        tab_dict: dict[Callable, str] = {
            self._connection_tab: "Connection",
            self._monitor_tab: "Monitor",
            self._mappings_tab: "Mappings",
            self._transport_tab: "Transport",
        }
        return tab_dict

    # ------------------------------------------------------------------
    # Tabs
    # ------------------------------------------------------------------
    def _connection_tab(self) -> QWidget:
        """
        The tab showing which ports are listened to.

        :return: QWidget
        """
        connection, information_group, tab = self._create_connection_tab_widgets()

        create_layout_with_items(parent=information_group, vertical=True, items=[self.information_text])
        _layout = create_layout_with_items(parent=tab,
                                           items=[connection, information_group],
                                           vertical=True,
                                           start_stretch=False,
                                           end_stretch=False)
        return tab

    def _create_connection_tab_widgets(self) -> tuple[QGroupBox, QGroupBox, QWidget]:
        """
        _create_connection_tab_widgets

        :return: tuple[QGroupBox, QWidget, QGroupBox]
        """
        tab = QWidget()
        connection = QGroupBox("MIDI Connection")
        self.status_label = QLabel("Not connected")
        information_group = QGroupBox("MIDI Information")

        self.create_preset_combo()
        self.create_port_combo()

        action_items = self._create_action_item_buttons()

        self.refresh_button = action_items[0]
        self.connect_button = action_items[1]
        self.disconnect_button = action_items[2]

        actions = create_layout_with_items(items=action_items,
                                           start_stretch=False,
                                           end_stretch=False)

        _form = self._create_midi_controller_form(actions, connection)
        # update_status() writes here. The text edit must be added to the
        # group's own layout: a second layout on the group is rejected by Qt,
        # leaving the text edit parentless and never shown.
        self.information_text = create_text_edit(readonly=True)
        return connection, information_group, tab

    def create_port_combo(self):
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(260)
        self.port_combo.setToolTip(
            "Automatic listens to every port the controller exposes, which is "
            "what you want unless you are using a different device."
        )

    def create_preset_combo(self):
        self.preset_combo = QComboBox()
        self._preset_combo_populate()
        self._preset_combo_set_current_index()
        self._preset_combo_current_index_changed_connect()
        self.preset_combo.setToolTip(
            "The controller whose mappings the Mappings tab shows and edits; "
            "the one plugged in is selected when this window opens. Each "
            "controller keeps its own learnt mappings."
        )

    def _preset_combo_current_index_changed_connect(self):
        self.preset_combo.currentIndexChanged.connect(
            lambda _index: self.select_profile(self.preset_combo.currentData())
        )

    def _preset_combo_set_current_index(self):
        self.preset_combo.setCurrentIndex(
            max(0, self.preset_combo.findData(self.profile.profile_id))
        )

    def _preset_combo_populate(self):
        for profile in CONTROLLER_PROFILES:
            self.preset_combo.addItem(profile.label, profile.profile_id)

    def _create_action_item_buttons(self) -> list[Any]:
        """_create_action_item_buttons"""
        actions_specs = self.create_action_button_specs()
        action_items = []
        for spec in actions_specs:
            item = create_button_from_spec(spec)
            action_items.append(item)
        return action_items

    def create_action_button_specs(self) -> list[ButtonSpec]:
        """create_action_button_specs"""
        refresh_button_spec = ButtonSpec(label="Refresh Ports", slot=self.refresh_ports)
        connect_button_spec = ButtonSpec(label="Connect", slot=self.connect_controller)
        disconnect_button_spec = ButtonSpec(label="Disconnect", slot=self.disconnect_controller)
        actions_specs = [
            refresh_button_spec,
            connect_button_spec,
            disconnect_button_spec
        ]
        return actions_specs

    def _create_midi_controller_form(self, actions: QHBoxLayout | QVBoxLayout, connection: QGroupBox):
        form = QFormLayout(connection)
        form.addRow("Controller preset:", self.preset_combo)
        form.addRow("MIDI Port:", self.port_combo)
        form.addRow("Actions:", actions)
        form.addRow("Status:", self.status_label)
        return form

    def _monitor_tab(self) -> QWidget:
        """
        The tab logging what the controller sends.

        :return: QWidget
        """
        tab = QWidget()

        hint = QLabel(
            "Every message received from the controller. Move a knob or fader "
            "to see the port, channel and CC number it sends."
        )
        hint.setWordWrap(True)

        self.monitor_text = create_text_edit(readonly=True)

        clear = QPushButton("Clear")
        clear.clicked.connect(self.monitor_text.clear)
        self.last_cc_label = QLabel("Last CC: none yet")
        bar = create_layout_with_items(vertical=False, items=[clear, self.last_cc_label],
                                       start_stretch=False,
                                       middle_stretch=True,
                                       end_stretch=False)

        _layout = create_layout_with_items(parent=tab,
                                           items=[hint,
                                                  self.monitor_text, bar],
                                           vertical=True,
                                           start_stretch=False,
                                           end_stretch=False)
        return tab

    def _mappings_tab(self) -> QWidget:
        """
        The tab assigning a CC number to each filter control.

        :return: QWidget
        """
        tab = QWidget()
        self.mappings_table = QTableWidget()
        self.mappings_table.setColumnCount(4)
        self.mappings_table.setHorizontalHeaderLabels(
            ["Filter control", "Usually", "CC", ""]
        )
        header = self.mappings_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.mappings_table.verticalHeader().setVisible(False)
        hint = QLabel(
            "Press Learn, then move the knob or fader you want for that "
            "control. Mappings are saved as you set them."
        )
        hint.setWordWrap(True)

        self.cancel_learn_button = QPushButton("Cancel Learn")
        self.cancel_learn_button.clicked.connect(self.cancel_learn)
        self.cancel_learn_button.setEnabled(False)

        reset = QPushButton("Reset to Defaults")
        reset.clicked.connect(self.reset_mappings)

        bar = create_layout_with_items(vertical=False, items=[self.cancel_learn_button, reset])

        _layout = create_layout_with_items(parent=tab,
                                           vertical=True,
                                           items=[self.mappings_table, hint, bar],
                                           start_stretch=False,
                                           end_stretch=False,
                                           middle_stretch=False)
        self._build_mappings_table()
        return tab

    def _build_mappings_table(self) -> None:
        """
        Fill the mappings table from the current map.

        :return: None
        """
        self.learn_buttons: Dict[FilterControl, QPushButton] = {}
        controls = list(FilterControl)
        self.mappings_table.setRowCount(len(controls))
        for row, control in enumerate(controls):

            name = QTableWidgetItem(CONTROL_LABELS.get(control, control.name))
            name.setFlags(name.flags() & ~Qt.ItemIsEditable)
            self.mappings_table.setItem(row, 0, name)

            source = QTableWidgetItem(self._source_text(control))
            source.setFlags(source.flags() & ~Qt.ItemIsEditable)
            self.mappings_table.setItem(row, 1, source)

            cc_item = QTableWidgetItem(self._cc_text(control))
            cc_item.setFlags(cc_item.flags() & ~Qt.ItemIsEditable)
            cc_item.setTextAlignment(Qt.AlignCenter)
            self.mappings_table.setItem(row, 2, cc_item)

            button = QPushButton("Learn")
            button.clicked.connect(
                lambda _checked=False, c=control: self.start_learn(c)
            )
            self.learn_buttons[control] = button
            self.mappings_table.setCellWidget(row, 3, button)

    def _transport_tab(self) -> QWidget:
        """
        The tab assigning controller buttons to the MIDI File player's transport.

        :return: QWidget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.transport_table = QTableWidget()
        self.transport_table.setColumnCount(4)
        self.transport_table.setHorizontalHeaderLabels(["Action", "Buttons", "", ""])
        header = self.transport_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.transport_table.verticalHeader().setVisible(False)
        layout.addWidget(self.transport_table)

        hint = QLabel(
            "Press Learn, then press the controller button for that action; it "
            "is added to the action's buttons (a note or a CC). Clear removes "
            "them. The MIDI File player uses changes straight away."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.last_transport_label = QLabel("Last button: none yet")
        layout.addWidget(self.last_transport_label)

        bar = QHBoxLayout()
        self.cancel_transport_learn_button = QPushButton("Cancel Learn")
        self.cancel_transport_learn_button.clicked.connect(self.cancel_transport_learn)
        self.cancel_transport_learn_button.setEnabled(False)
        bar.addWidget(self.cancel_transport_learn_button)
        bar.addStretch()
        reset = QPushButton("Reset to Defaults")
        reset.clicked.connect(self.reset_transport)
        bar.addWidget(reset)
        layout.addLayout(bar)

        self._build_transport_table()
        return tab

    def _build_transport_table(self) -> None:
        """
        One row per transport action, with its buttons, Learn and Clear.

        :return: None
        """
        self.transport_learn_buttons: Dict[TransportAction, QPushButton] = {}
        actions = list(TRANSPORT_LABELS)
        self.transport_table.setRowCount(len(actions))
        for row, action in enumerate(actions):
            name = QTableWidgetItem(TRANSPORT_LABELS[action])
            name.setFlags(name.flags() & ~Qt.ItemIsEditable)
            self.transport_table.setItem(row, 0, name)

            buttons = QTableWidgetItem(self._transport_text(action))
            buttons.setFlags(buttons.flags() & ~Qt.ItemIsEditable)
            self.transport_table.setItem(row, 1, buttons)

            learn = QPushButton("Learn")
            learn.clicked.connect(
                lambda _checked=False, a=action: self.start_transport_learn(a)
            )
            self.transport_learn_buttons[action] = learn
            self.transport_table.setCellWidget(row, 2, learn)

            clear = QPushButton("Clear")
            clear.clicked.connect(
                lambda _checked=False, a=action: self.clear_transport_action(a)
            )
            self.transport_table.setCellWidget(row, 3, clear)

    def _transport_text(self, action: TransportAction) -> str:
        """
        The buttons that trigger ``action``, as shown in the table.

        :param action: TransportAction
        :return: str e.g. "Note 94, CC 52", or "not set"
        """
        labels = [spec.label for spec in self.transport_specs if spec.action is action]
        return ", ".join(labels) if labels else "not set"

    def _refresh_transport_column(self) -> None:
        """
        Redraw the Buttons column.

        :return: None
        """
        for row, action in enumerate(TRANSPORT_LABELS):
            item = self.transport_table.item(row, 1)
            if item is not None:
                item.setText(self._transport_text(action))

    def _source_text(self, control: FilterControl) -> str:
        """
        The hardware control that sends ``control`` by default, for the table.

        Taken from the profile's ``source`` entries in ``midi_controllers.json``;
        blank where the physical control is not known (as for the VMX8, whose
        map is translated, not measured).

        :param control: FilterControl
        :return: str e.g. "Knob 1", or ""
        """
        return self.profile.sources.get(control, "")

    def connected_profile(self) -> ControllerProfile:
        """
        Profile of the controller plugged in, or the MiniLab 3 if none is.

        :return: ControllerProfile
        """
        profile = getattr(self.external_controller, "profile", None)
        return profile if isinstance(profile, ControllerProfile) else MINILAB3

    def select_profile(self, profile_id: Optional[str]) -> None:
        """
        Show and edit the mappings of another controller.

        :param profile_id: Optional[str] ControllerProfile id
        :return: None
        """
        self.cancel_learn()
        self.cancel_transport_learn()
        self.profile = profile_by_id(profile_id)
        self.cc_map = load_filter_map(profile=self.profile)
        self.transport_specs = list(load_transport_specs(profile=self.profile))
        self._refresh_transport_column()
        if self._is_live_profile() and self.filter_remote is not None:
            self.filter_remote.cc_map = dict(self.cc_map)
        for row, control in enumerate(FilterControl):
            item = self.mappings_table.item(row, 1)
            if item is not None:
                item.setText(self._source_text(control))
        self._refresh_cc_column()
        self.update_status()

    def _is_live_profile(self) -> bool:
        """
        Whether the profile being edited is the one the running remote uses.

        :return: bool
        """
        return self.profile.profile_id == self.connected_profile().profile_id

    def _cc_text(self, control: FilterControl) -> str:
        """
        The CC number assigned to ``control``, as shown in the table.

        :param control: FilterControl
        :return: str
        """
        cc = self.cc_for(control)
        return "not set" if cc is None else str(cc)

    def cc_for(self, control: FilterControl) -> Optional[int]:
        """
        The CC number mapped to ``control``.

        :param control: FilterControl
        :return: Optional[int]
        """
        return next((cc for cc, c in self.cc_map.items() if c is control), None)

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------
    def refresh_ports(self) -> None:
        """
        Reload the list of MIDI input ports, keeping the current choice.

        :return: None
        """
        if self.external_controller is None:
            return
        chosen = self.port_combo.currentText()
        self.port_combo.blockSignals(True)
        self.port_combo.clear()
        self.port_combo.addItem(AUTOMATIC_PORTS)
        for port in self.external_controller.available_ports():
            self.port_combo.addItem(port)
        index = self.port_combo.findText(chosen)
        self.port_combo.setCurrentIndex(max(0, index))
        self.port_combo.blockSignals(False)
        self.update_status()

    def connect_controller(self) -> None:
        """
        Listen to the chosen port, or find the controller's ports automatically.

        :return: None
        """
        if self.external_controller is None:
            return
        chosen = self.port_combo.currentText()
        if chosen == AUTOMATIC_PORTS:
            self.external_controller.auto_connect()
        else:
            self.external_controller.connect_port(chosen)
        self.update_status()

    def disconnect_controller(self) -> None:
        """
        Stop listening to the controller.

        :return: None
        """
        if self.external_controller is None:
            return
        self.external_controller.close()
        self.update_status()

    def update_status(self) -> None:
        """
        Show whether the controller is connected, and on which ports.

        :return: None
        """
        controller = self.external_controller
        connected = controller is not None and controller.is_open
        ports = controller.port_names if controller is not None else []
        self.status_label.setText("Connected" if connected else "Not connected")
        self.status_label.setStyleSheet(
            "color: #43a047; font-weight: bold;"
            if connected
            else "color: #e53935; font-weight: bold;"
        )
        self.connect_button.setEnabled(controller is not None)
        self.disconnect_button.setEnabled(connected)

        available_ports = controller.available_ports() if controller is not None else []
        self.information_text_update(available_ports, ports)

    def information_text_update(self, available_ports: list[Any] | Any, ports: list[Any] | Any):
        """
        information_text_update

        :param available_ports:
        :param ports:
        :return:
        """
        self.information_text.setPlainText(
            "\n".join(
                [
                    f"Available ports: {len(available_ports)}",
                    f"Listening to: {', '.join(ports) if ports else 'nothing'}",
                    f"Mapped controls: {len(self.cc_map)}",
                    f"Filter controls: {len(list(FilterControl))}",
                ]
            )
        )

    # ------------------------------------------------------------------
    # Monitor and learn
    # ------------------------------------------------------------------
    def _on_message(self, port_name: str, message: object) -> None:
        """
        Log a message from the controller, and use it if learning.

        :param port_name: str the port it arrived on
        :param message: mido.Message
        :return: None
        """
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self._append_monitor_line(f"{timestamp} [{port_name}] {message}")
        self._show_transport_press(message)
        if self._learning_transport is not None:
            spec = self._spec_from_press(self._learning_transport, message)
            if spec is not None:
                self.assign_transport(spec)
            return
        if getattr(message, "type", None) != "control_change":
            return
        self.last_cc_label.setText(
            f"Last CC: {message.control} = {message.value} "
            f"(channel {message.channel + 1})"
        )
        if self._learning is not None:
            self.assign_cc(self._learning, message.control)

    def _append_monitor_line(self, line: str) -> None:
        """
        Add a line to the monitor, dropping the oldest once it is full.

        :param line: str
        :return: None
        """
        self.monitor_text.append(line)
        document = self.monitor_text.document()
        while document.blockCount() > MONITOR_MAX_LINES:
            cursor = self.monitor_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.select(cursor.SelectionType.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()

    def start_learn(self, control: FilterControl) -> None:
        """
        Take the next CC received as the mapping for ``control``.

        :param control: FilterControl
        :return: None
        """
        self.cancel_learn()
        self.cancel_transport_learn()
        self._learning = control
        button = self.learn_buttons.get(control)
        if button is not None:
            button.setText("Move it...")
        self.cancel_learn_button.setEnabled(True)
        self.tabs.setCurrentIndex(self.tabs.indexOf(self.mappings_table.parentWidget()))

    def cancel_learn(self) -> None:
        """
        Stop waiting for a CC.

        :return: None
        """
        if self._learning is not None:
            button = self.learn_buttons.get(self._learning)
            if button is not None:
                button.setText("Learn")
        self._learning = None
        self.cancel_learn_button.setEnabled(False)

    def assign_cc(self, control: FilterControl, cc: int) -> None:
        """
        Map ``cc`` to ``control``, replacing any other control using it.

        A CC can only drive one thing, otherwise one knob would move two
        sliders at once.

        :param control: FilterControl
        :param cc: int CC number 0-127
        :return: None
        """
        self.cc_map = {
            number: mapped
            for number, mapped in self.cc_map.items()
            if mapped is not control and number != cc
        }
        self.cc_map[cc] = control
        self.cancel_learn()
        self._refresh_cc_column()
        self.apply_mappings()
        log.message(
            f"Mapped CC{cc} to {control.name}", scope=self.__class__.__name__
        )

    def reset_mappings(self) -> None:
        """
        Go back to the selected controller's built-in map.

        :return: None
        """
        self.cancel_learn()
        self.cc_map = default_filter_map(self.profile)
        self._refresh_cc_column()
        self.apply_mappings()

    def apply_mappings(self) -> None:
        """
        Save the map and, if it is the connected controller's, hand it to the
        running filter remote.

        :return: None
        """
        save_filter_map(self.cc_map, profile=self.profile)
        if self.filter_remote is not None and self._is_live_profile():
            self.filter_remote.cc_map = dict(self.cc_map)
        self.update_status()

    def _refresh_cc_column(self) -> None:
        """
        Redraw the CC numbers in the table.

        :return: None
        """
        for row, control in enumerate(FilterControl):
            item = self.mappings_table.item(row, 2)
            if item is not None:
                item.setText(self._cc_text(control))

    # ------------------------------------------------------------------
    # Transport
    # ------------------------------------------------------------------
    @staticmethod
    def _spec_from_press(action: TransportAction, message: object) -> Optional[TransportSpec]:
        """
        The transport button ``message`` presses, bound to ``action``.

        :param action: TransportAction
        :param message: mido.Message
        :return: Optional[TransportSpec] None if ``message`` is not a button press
            (a release, or neither a note-on nor a CC)
        """
        kind = getattr(message, "type", None)
        if kind == "note_on" and message.velocity > 0:
            return TransportSpec(action, "note", message.channel, message.note)
        if kind == "control_change" and message.value >= 64:
            return TransportSpec(action, "cc", message.channel, message.control)
        return None

    def _show_transport_press(self, message: object) -> None:
        """
        Name the transport action a button press triggers, if any.

        :param message: mido.Message
        :return: None
        """
        spec = next((s for s in self.transport_specs if s.matches(message)), None)
        if spec is not None:
            self.last_transport_label.setText(
                f"Last button: {TRANSPORT_LABELS[spec.action]} ({spec.label})"
            )

    def start_transport_learn(self, action: TransportAction) -> None:
        """
        Add the next button pressed as a trigger for ``action``.

        :param action: TransportAction
        :return: None
        """
        self.cancel_learn()
        self.cancel_transport_learn()
        self._learning_transport = action
        button = self.transport_learn_buttons.get(action)
        if button is not None:
            button.setText("Press it...")
        self.cancel_transport_learn_button.setEnabled(True)

    def cancel_transport_learn(self) -> None:
        """
        Stop waiting for a transport button.

        :return: None
        """
        if self._learning_transport is not None:
            button = self.transport_learn_buttons.get(self._learning_transport)
            if button is not None:
                button.setText("Learn")
        self._learning_transport = None
        self.cancel_transport_learn_button.setEnabled(False)

    def assign_transport(self, spec: TransportSpec) -> None:
        """
        Add ``spec`` to its action's buttons, taking it from any other action.

        A button can only do one thing, so it is removed from the others.

        :param spec: TransportSpec
        :return: None
        """
        same_button = (spec.kind, spec.channel, spec.number)
        self.transport_specs = [
            s for s in self.transport_specs
            if (s.kind, s.channel, s.number) != same_button
        ] + [spec]
        self.cancel_transport_learn()
        self.apply_transport()
        log.message(
            f"Transport {spec.action.name} <- {spec.label}",
            scope=self.__class__.__name__,
        )

    def clear_transport_action(self, action: TransportAction) -> None:
        """
        Remove every button bound to ``action``.

        :param action: TransportAction
        :return: None
        """
        self.cancel_transport_learn()
        self.transport_specs = [s for s in self.transport_specs if s.action is not action]
        self.apply_transport()

    def reset_transport(self) -> None:
        """
        Go back to the selected controller's built-in transport buttons.

        :return: None
        """
        self.cancel_transport_learn()
        clear_transport_specs(profile=self.profile)
        self.transport_specs = list(self.profile.transport)
        self._refresh_transport_column()
        notify_transport_bindings_changed()

    def apply_transport(self) -> None:
        """
        Save the transport buttons and tell the MIDI File player.

        :return: None
        """
        save_transport_specs(self.transport_specs, profile=self.profile)
        self._refresh_transport_column()
        notify_transport_bindings_changed()

    def closeEvent(self, event) -> None:
        """
        Stop the status timer and any learn in progress.

        :param event: QCloseEvent
        :return: None
        """
        self.cancel_learn()
        self.cancel_transport_learn()
        self._status_timer.stop()
        event.accept()
