"""
System Settings Widget

Provides UI controls for System Common and System Controller parameters:
- Master Tune, Master Key Shift, Master Level
- Program Control Channel
- Receive/Transmit Program Change and Bank Select
- Keyboard Velocity, Velocity Curve, Velocity Curve Offset
"""

from typing import Callable, Dict, Optional

from decologr import Decologr as log
from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtCore import Qt
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QFormLayout, QGroupBox, QScrollArea, QWidget

from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.midi.data.parameter.system.common import SystemCommonParam
from jdxi_editor.midi.data.parameter.system.controller import SystemControllerParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests
from jdxi_editor.midi.sysex.sections import SysExSection
from jdxi_editor.ui.common import JDXi, QVBoxLayout
from jdxi_editor.ui.editors.digital.utils import filter_sysex_keys
from jdxi_editor.ui.editors.synth.base import SynthBase
from jdxi_editor.ui.widgets.editor.helper import create_group_with_layout

# System Common: 02 00 00 xx
SYSTEM_COMMON_ADDRESS = JDXiSysExAddress(0x02, 0x00, 0x00, 0x00)
# System Controller: 02 00 03 xx
SYSTEM_CONTROLLER_ADDRESS = JDXiSysExAddress(0x02, 0x00, 0x03, 0x00)


class SystemSettingsWidget(SynthBase):
    """Widget for System Common and System Controller parameters."""

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        send_midi_callback: Optional[Callable] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(midi_helper=midi_helper, parent=parent)
        self.send_midi_callback = send_midi_callback or getattr(
            parent, "send_midi_parameter", None
        )
        if parent and hasattr(parent, "parent") and parent.parent:
            self.send_midi_callback = self.send_midi_callback or getattr(
                parent.parent, "send_midi_parameter", None
            )
        self.controls: Dict[AddressParameter, QWidget] = {}
        self.midi_requests = [
            MidiRequests.SYSTEM_COMMON,
            MidiRequests.SYSTEM_CONTROLLER,
        ]
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        layout = QVBoxLayout(content)

        # System Common group
        common_group = self._build_system_common_group()
        layout.addWidget(common_group)

        # System Controller group
        ctrl_group = self._build_system_controller_group()
        layout.addWidget(ctrl_group)

        layout.addStretch()
        scroll.setWidget(content)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

    def _build_system_common_group(self) -> QGroupBox:
        form = QFormLayout()
        group, form = create_group_with_layout(label="System Common", layout=form)
        address = SYSTEM_COMMON_ADDRESS
        label_master_tune = "Master Tune (cents)"
        # Master Tune (cents: -100 to +100, raw 24-2024)
        master_tune = self._create_parameter_slider(
            SystemCommonParam.MASTER_TUNE,
            None,
            vertical=False,
            address=address,
        )
        form.addRow(label_master_tune, master_tune)
        # the labes for create_parameter_slider are superfluous since addRow provides them
        # Master Key Shift (-24 to +24)
        key_shift = self._create_parameter_slider(
            SystemCommonParam.MASTER_KEY_SHIFT,
            None,
            vertical=False,
            address=address,
        )
        form.addRow("Master Key Shift:", key_shift)

        # Master Level (0-127)
        master_level = self._create_parameter_slider(
            SystemCommonParam.MASTER_LEVEL,
            None,
            vertical=False,
            address=address,
        )
        form.addRow("Master Level:", master_level)

        # Program Control Channel (0-16: OFF, 1-16)
        prog_ch = self._create_parameter_combo_box(
            SystemCommonParam.PROGRAM_CTRL_CH,
            None,
            options=["OFF"] + [str(i) for i in range(1, 17)],
            values=list(range(17)),
        )
        form.addRow("Program Control Channel:", prog_ch)

        # Receive Program Change
        rx_pc = self._create_parameter_combo_box(
            SystemCommonParam.RX_PROGRAM_CHANGE,
            None,
            options=["OFF", "ON"],
            values=[0, 1],
        )
        form.addRow("Receive Program Change:", rx_pc)

        # Receive Bank Select
        rx_bs = self._create_parameter_combo_box(
            SystemCommonParam.RX_BANK_SELECT,
            None,
            options=["OFF", "ON"],
            values=[0, 1],
        )
        form.addRow("Receive Bank Select:", rx_bs)

        return group

    def _build_system_controller_group(self) -> QGroupBox:
        form = QFormLayout()
        group, form = create_group_with_layout(label="System Controller", layout=form)
        address = SYSTEM_CONTROLLER_ADDRESS

        # Transmit Program Change
        tx_pc = self._create_parameter_combo_box(
            SystemControllerParam.TRANSMIT_PROGRAM_CHANGE,
            None,
            options=["OFF", "ON"],
            values=[0, 1],
        )
        form.addRow("Transmit Program Change:", tx_pc)

        # Transmit Bank Select
        tx_bs = self._create_parameter_combo_box(
            SystemControllerParam.TRANSMIT_BANK_SELECT,
            None,
            options=["OFF", "ON"],
            values=[0, 1],
        )
        form.addRow("Transmit Bank Select:", tx_bs)

        # Keyboard Velocity (0=REAL, 1-127)
        kv = self._create_parameter_combo_box(
            SystemControllerParam.KEYBOARD_VELOCITY,
            None,
            options=["REAL"] + [str(i) for i in range(1, 128)],
            values=list(range(128)),
        )
        form.addRow("Keyboard Velocity:", kv)

        # Keyboard Velocity Curve
        vc = self._create_parameter_combo_box(
            SystemControllerParam.KEYBOARD_VELOCITY_CURVE,
            None,
            options=["LIGHT", "MEDIUM", "HEAVY"],
            values=[1, 2, 3],
        )
        form.addRow("Velocity Curve:", vc)

        # Keyboard Velocity Curve Offset (-10 to +9)
        vco = self._create_parameter_slider(
            SystemControllerParam.KEYBOARD_VELOCITY_CURVE_OFFSET,
            None,
            vertical=False,
            address=address,
        )
        form.addRow("Velocity Curve Offset:", vco)

        return group

    def _create_parameter_slider(
        self,
        param: AddressParameter,
        label: str = None,
        vertical: bool = False,
        address: JDXiSysExAddress = None,
    ):
        slider = super()._create_parameter_slider(
            param=param,
            label=label,
            vertical=vertical,
            address=address,
        )
        self.controls[param] = slider
        return slider

    def _create_parameter_combo_box(
        self,
        param: AddressParameter,
        label: str = None,
        options: list = None,
        values: list = None,
        show_label: bool = True,
    ):
        combo = super()._create_parameter_combo_box(
            param=param,
            label=label,
            options=options,
            values=values,
            show_label=show_label,
        )
        self.controls[param] = combo
        return combo

    def send_midi_parameter(
        self, param: AddressParameter, value: int, address: JDXiSysExAddress = None
    ) -> bool:
        if self.send_midi_callback:
            addr = address or (
                SYSTEM_COMMON_ADDRESS
                if param
                in (
                    SystemCommonParam.MASTER_TUNE,
                    SystemCommonParam.MASTER_KEY_SHIFT,
                    SystemCommonParam.MASTER_LEVEL,
                    SystemCommonParam.PROGRAM_CTRL_CH,
                    SystemCommonParam.RX_PROGRAM_CHANGE,
                    SystemCommonParam.RX_BANK_SELECT,
                )
                else SYSTEM_CONTROLLER_ADDRESS
            )
            return self.send_midi_callback(param, value, address=addr)
        return super().send_midi_parameter(param, value, address=address)

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if self.midi_helper:
            log.message(
                "System Settings shown - requesting current settings",
                scope=self.__class__.__name__,
            )
        self.data_request()

    def _dispatch_sysex_to_area(self, json_sysex_data: str) -> None:
        """Update controls from incoming SysEx."""
        try:
            import json

            sysex_data = json.loads(json_sysex_data)
            temporary_area = sysex_data.get(SysExSection.TEMPORARY_AREA, "")

            if temporary_area not in ("SYSTEM_COMMON", "SYSTEM_CONTROLLER"):
                return

            filtered = filter_sysex_keys(sysex_data)
            for param_name, raw_value in filtered.items():
                if param_name in (SysExSection.TEMPORARY_AREA, SysExSection.SYNTH_TONE):
                    continue
                param = SystemCommonParam.get_by_name(
                    param_name
                ) or SystemControllerParam.get_by_name(param_name)
                if not param:
                    continue
                widget = self.controls.get(param)
                if not widget:
                    continue
                try:
                    value = (
                        int(raw_value) if not isinstance(raw_value, int) else raw_value
                    )
                    if hasattr(widget, "combo_box"):
                        widget.blockSignals(True)
                        widget.setValue(value)
                        widget.blockSignals(False)
                    elif hasattr(widget, "setValue"):
                        widget.blockSignals(True)
                        widget.setValue(value)
                        widget.blockSignals(False)
                except Exception:
                    pass
        except Exception:
            pass

    def get_controls(self) -> Dict[AddressParameter, QWidget]:
        return self.controls
