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

The CC numbers a MiniLab 3 sends depend on the program loaded on the device,
so the built-in map is only a starting point; Learn is the reliable way to get
them right.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from decologr import Decologr as log
from PySide6.QtCore import Qt, QTimer
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
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.io.controller_map import FilterControl
from jdxi_editor.midi.io.controller_settings import (
    default_filter_map,
    load_filter_map,
    save_filter_map,
)

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
    :param source: str MiniLab 3 control that sends it by default, or "" if none
    """

    control: FilterControl
    label: str
    source: str = ""


#: One row per control, in the order of the MiniLab 3 defaults
CONTROL_SPECS: list[ControlLabelSpec] = [
    ControlLabelSpec(FilterControl.CUTOFF, "Cutoff", source="Knob 1"),
    ControlLabelSpec(FilterControl.RESONANCE, "Resonance", source="Knob 2"),
    ControlLabelSpec(FilterControl.KEYFOLLOW, "Cutoff key follow", source="Knob 3"),
    ControlLabelSpec(FilterControl.ENV_DEPTH, "Envelope depth", source="Knob 4"),
    ControlLabelSpec(FilterControl.ENV_VELOCITY, "Envelope velocity sensitivity"),
    ControlLabelSpec(FilterControl.ENV_ATTACK, "Filter envelope attack", source="Fader 1"),
    ControlLabelSpec(FilterControl.ENV_DECAY, "Filter envelope decay", source="Fader 2"),
    ControlLabelSpec(FilterControl.ENV_SUSTAIN, "Filter envelope sustain", source="Fader 3"),
    ControlLabelSpec(FilterControl.ENV_RELEASE, "Filter envelope release", source="Fader 4"),
    ControlLabelSpec(FilterControl.EFFECT1_LEVEL, "Effect 1 level", source="Knob 5"),
    ControlLabelSpec(FilterControl.EFFECT2_LEVEL, "Effect 2 level", source="Knob 6"),
    ControlLabelSpec(FilterControl.DELAY_LEVEL, "Delay level", source="Knob 7"),
    ControlLabelSpec(FilterControl.REVERB_LEVEL, "Reverb level", source="Knob 8"),
]

#: Human-readable name for each control
CONTROL_LABELS: Dict[FilterControl, str] = {
    spec.control: spec.label for spec in CONTROL_SPECS
}

#: Which hardware control usually sends it, for the table
CONTROL_SOURCES: Dict[FilterControl, str] = {
    spec.control: spec.source for spec in CONTROL_SPECS if spec.source
}


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
        self.setWindowTitle("MIDI Controller")
        self.setMinimumSize(640, 560)
        self.external_controller = external_controller
        self.filter_remote = filter_remote
        #: CC -> FilterControl being edited
        self.cc_map: Dict[int, FilterControl] = (
            dict(filter_remote.cc_map) if filter_remote is not None else load_filter_map()
        )
        # Dark editor chrome for this window only, as in the MIDI Config dialog.
        # Not qdarktheme (apply_dark_theme / apply_theme("auto")): that restyles
        # the whole application and replaces the editor's own stylesheet.
        JDXi.UI.Theme.apply_editor_style(self)
        #: the control waiting for the next CC, while learning
        self._learning: Optional[FilterControl] = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        title = QLabel("MIDI Controller")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.tabs.addTab(self._connection_tab(), "Connection")
        self.tabs.addTab(self._monitor_tab(), "Monitor")
        self.tabs.addTab(self._mappings_tab(), "Mappings")

        if self.external_controller is not None:
            self.external_controller.message_received.connect(self._on_message)
            self.external_controller.ports_changed.connect(
                lambda _ports: self.refresh_ports()
            )

        self.refresh_ports()
        self.update_status()
        self._status_timer = QTimer(self)
        self._status_timer.setInterval(STATUS_INTERVAL_MS)
        self._status_timer.timeout.connect(self.update_status)
        self._status_timer.start()

    # ------------------------------------------------------------------
    # Tabs
    # ------------------------------------------------------------------
    def _connection_tab(self) -> QWidget:
        """
        The tab showing which ports are listened to.

        :return: QWidget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        connection = QGroupBox("MIDI Connection")
        form = QFormLayout(connection)

        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Arturia MiniLab 3", "minilab3")
        self.preset_combo.setToolTip(
            "The CC numbers this controller is expected to send. "
            "Learn them on the Mappings tab if your device sends others."
        )
        form.addRow("Controller preset:", self.preset_combo)

        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(260)
        self.port_combo.setToolTip(
            "Automatic listens to every port the controller exposes, which is "
            "what you want unless you are using a different device."
        )
        form.addRow("MIDI Port:", self.port_combo)

        actions = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh Ports")
        self.refresh_button.clicked.connect(self.refresh_ports)
        actions.addWidget(self.refresh_button)
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_controller)
        actions.addWidget(self.connect_button)
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self.disconnect_controller)
        actions.addWidget(self.disconnect_button)
        form.addRow("Actions:", actions)

        self.status_label = QLabel("Not connected")
        form.addRow("Status:", self.status_label)
        layout.addWidget(connection)

        information = QGroupBox("MIDI Information")
        information_layout = QVBoxLayout(information)
        self.information_text = QTextEdit()
        self.information_text.setReadOnly(True)
        information_layout.addWidget(self.information_text)
        layout.addWidget(information)
        return tab

    def _monitor_tab(self) -> QWidget:
        """
        The tab logging what the controller sends.

        :return: QWidget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        hint = QLabel(
            "Every message received from the controller. Move a knob or fader "
            "to see the port, channel and CC number it sends."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.monitor_text = QTextEdit()
        self.monitor_text.setReadOnly(True)
        self.monitor_text.setLineWrapMode(QTextEdit.NoWrap)
        layout.addWidget(self.monitor_text)

        bar = QHBoxLayout()
        clear = QPushButton("Clear")
        clear.clicked.connect(self.monitor_text.clear)
        bar.addWidget(clear)
        bar.addStretch()
        self.last_cc_label = QLabel("Last CC: none yet")
        bar.addWidget(self.last_cc_label)
        layout.addLayout(bar)
        return tab

    def _mappings_tab(self) -> QWidget:
        """
        The tab assigning a CC number to each filter control.

        :return: QWidget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

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
        layout.addWidget(self.mappings_table)

        hint = QLabel(
            "Press Learn, then move the knob or fader you want for that "
            "control. Mappings are saved as you set them."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        bar = QHBoxLayout()
        self.cancel_learn_button = QPushButton("Cancel Learn")
        self.cancel_learn_button.clicked.connect(self.cancel_learn)
        self.cancel_learn_button.setEnabled(False)
        bar.addWidget(self.cancel_learn_button)
        bar.addStretch()
        reset = QPushButton("Reset to Defaults")
        reset.clicked.connect(self.reset_mappings)
        bar.addWidget(reset)
        layout.addLayout(bar)

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

            source = QTableWidgetItem(CONTROL_SOURCES.get(control, ""))
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

        available = controller.available_ports() if controller is not None else []
        self.information_text.setPlainText(
            "\n".join(
                [
                    f"Available ports: {len(available)}",
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
        Go back to the built-in MiniLab 3 map.

        :return: None
        """
        self.cancel_learn()
        self.cc_map = default_filter_map()
        self._refresh_cc_column()
        self.apply_mappings()

    def apply_mappings(self) -> None:
        """
        Save the map and hand it to the running filter remote.

        :return: None
        """
        save_filter_map(self.cc_map)
        if self.filter_remote is not None:
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

    def closeEvent(self, event) -> None:
        """
        Stop the status timer and any learn in progress.

        :param event: QCloseEvent
        :return: None
        """
        self.cancel_learn()
        self._status_timer.stop()
        event.accept()
