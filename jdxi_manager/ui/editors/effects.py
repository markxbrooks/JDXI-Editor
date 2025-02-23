from functools import partial

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QComboBox,
    QScrollArea,
    QTabWidget,
)
from PySide6.QtCore import Qt
import logging

from jdxi_manager.data import EffectParameter
from jdxi_manager.data.effects import EffectsCommonParameter
from jdxi_manager.midi.constants.analog import TEMPORARY_ANALOG_SYNTH_AREA
from jdxi_manager.midi.constants.sysex import TEMPORARY_PROGRAM_AREA
from jdxi_manager.midi.sysex.sysex import PROGRAM_COMMON
from jdxi_manager.ui.editors.base import BaseEditor
from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.midi.constants import EFFECTS_AREA
from jdxi_manager.midi.io.helper import MIDIHelper
from typing import Union


class EffectsEditor(BaseEditor):
    def __init__(self, midi_helper: MIDIHelper, parent=None):
        super().__init__(midi_helper, parent)
        self.setWindowTitle("Effects")

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.controls: Dict[Union[EffectParameter, EffectsCommonParameter], QWidget] = (
            {}
        )

        # Create a tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(Style.JDXI_TABS_STYLE)
        main_layout.addWidget(self.tabs)

        # Add tabs
        self.tabs.addTab(self._create_effect1_section(), "Effect 1")
        self.tabs.addTab(self._create_effect2_section(), "Effect 2")
        self.tabs.addTab(self._create_delay_tab(), "Delay")
        self.tabs.addTab(self._create_reverb_section(), "Reverb")

    def _update_efx2_parameters(self, effect_type: int):
        """Show/hide parameters based on effect type"""
        # Number of parameters for each effect type
        param_counts = {
            0: 0,  # OFF
            5: 8,  # PHASER
            6: 6,  # FLANGER
            7: 4,  # DELAY
            8: 6,  # CHORUS
        }

        # Get number of parameters for current effect
        count = param_counts.get(effect_type, 0)

        # Show/hide parameters
        for i, param in enumerate(self.efx2_additional_params):
            param.setVisible(i < count)

    def _update_delay_parameters(self, show_all: bool = False):
        """Show/hide delay parameters

        Args:
            show_all: If True, show all parameters, otherwise show commonly used ones
        """
        # Common parameter names and indices to show by default
        common_params = {
            0: "Time",
            1: "Feedback",
            2: "High Damp",
            3: "Low Damp",
            4: "Spread",
        }

        for i, param in enumerate(self.delay_params):
            if show_all:
                param.setVisible(True)
                if i in common_params:
                    param.setLabel(common_params[i])
            else:
                param.setVisible(i in common_params)
                if i in common_params:
                    param.setLabel(common_params[i])

    from functools import partial

    def _create_parameter_slider(
        self, param_name: str, label: str, vertical=False
    ) -> Slider:
        """Create a slider for a parameter with proper display conversion"""
        param = EffectParameter.get_by_name(param_name)
        if param is None:
            logging.error(f"Parameter {param_name} not found.")
            return None

        address, min_val, max_val = param.value
        slider = Slider(label, min_val, max_val, vertical)

        # Use functools.partial to avoid lambda scoping issues
        slider.valueChanged.connect(partial(self._on_parameter_changed, param_name))

        self.controls[param] = slider
        logging.debug(f"Slider created for {param.name} with address {address}")
        return slider

    def _create_effect1_section(self):
        """Create Effect 1 section"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Create a combo box for EFX1 type
        self.efx1_type = QComboBox()
        self.efx1_type.addItems(
            ["OFF", "DISTORTION", "FUZZ", "COMPRESSOR", "BIT CRUSHER", "FLANGER"]
        )
        self.efx1_type.currentIndexChanged.connect(self._on_efx1_type_changed)
        layout.addWidget(self.efx1_type)

        # Create sliders for EFX1 parameters
        self.efx1_level = self._create_parameter_slider(
            "EFX1_LEVEL", "EFX1 Level (0-127)"
        )
        self.efx1_delay_send_level = self._create_parameter_slider(
            "EFX1_DELAY_SEND_LEVEL", "EFX1 Delay Send Level (0-127)"
        )
        self.efx1_reverb_send_level = self._create_parameter_slider(
            "EFX1_REVERB_SEND_LEVEL", "EFX1 Reverb Send Level (0-127)"
        )

        # Flanger-specific sliders
        self.flanger_rate = self._create_parameter_slider(
            "FLANGER_RATE", "Rate (0-127)"
        )
        self.flanger_depth = self._create_parameter_slider(
            "FLANGER_DEPTH", "Depth (0-127)"
        )
        self.flanger_feedback = self._create_parameter_slider(
            "FLANGER_FEEDBACK", "Feedback (0-127)"
        )
        self.flanger_manual = self._create_parameter_slider(
            "FLANGER_MANUAL", "Manual (0-127)"
        )
        self.flanger_balance = self._create_parameter_slider(
            "FLANGER_BALANCE", "Balance (D100:0W - D0:100W)"
        )

        # Add all sliders to layout
        layout.addWidget(self.efx1_level)
        layout.addWidget(self.efx1_delay_send_level)
        layout.addWidget(self.efx1_reverb_send_level)
        layout.addWidget(self.flanger_rate)
        layout.addWidget(self.flanger_depth)
        layout.addWidget(self.flanger_feedback)
        layout.addWidget(self.flanger_manual)
        layout.addWidget(self.flanger_balance)

        return widget

    def _create_effect2_section(self):
        """Create Effect 2 section"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Create a combo box for EFX2 type
        self.efx2_type = QComboBox()
        self.efx2_type.addItems(
            ["OFF", "PHASER", "FLANGER", "DELAY", "CHORUS"]
        )  # Types 0, 5-8
        self.efx2_type.currentIndexChanged.connect(self._on_efx2_type_changed)
        layout.addWidget(self.efx2_type)

        # Create sliders for EFX2 parameters

        # layout.addWidget(self._create_parameter_slider("EFX2_LEVEL", "EFX2 Level"))
        self.efx2_level = Slider("EFX2 Level (0-127)", 0, 127)
        self.efx2_level.valueChanged.connect(self._on_efx2_level_changed)
        layout.addWidget(self.efx2_level)

        # layout.addWidget(self._create_parameter_slider("EFX2_DELAY_SEND_LEVEL", "EFX2 Delay Send Level"))
        self._on_efx2_delay_send_level = Slider("EFX2 Delay Send Level (0-127)", 0, 127)
        self._on_efx2_delay_send_level.valueChanged.connect(
            self._on_efx2_delay_send_level_changed
        )
        layout.addWidget(self._on_efx2_delay_send_level)

        # layout.addWidget(self._create_parameter_slider("EFX2_REVERB_SEND_LEVEL", "EFX2 Reverb Send Level"))
        self._on_efx2_reverb_send_level = Slider(
            "EFX2 Delay Send Level (0-127)", 0, 127
        )
        self._on_efx2_reverb_send_level.valueChanged.connect(
            self._on_efx2_reverb_send_level_changed
        )
        layout.addWidget(self._on_efx2_reverb_send_level)

        return widget

    def _on_efx2_level_changed(self, value: int):
        """Handle pulse width modulation depth change"""
        common_param = EffectParameter.get_common_param_by_name("EFX2_LEVEL")
        address_offset = EffectParameter.get_address_by_name("EFX2_LEVEL")
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_PROGRAM_AREA,  # 0x18
                part=PROGRAM_COMMON,
                group=common_param.address,
                param=address_offset,
                value=value,
            )

    def _on_efx2_delay_send_level_changed(self, value: int):
        """Handle pulse width modulation depth change"""
        common_param = EffectParameter.get_common_param_by_name("EFX2_DELAY_SEND_LEVEL")
        address_offset = EffectParameter.get_address_by_name("EFX2_DELAY_SEND_LEVEL")
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_PROGRAM_AREA,  # 0x18
                part=PROGRAM_COMMON,
                group=common_param.address,
                param=address_offset,
                value=value,
            )

    def _on_efx2_reverb_send_level_changed(self, value: int):
        """Handle pulse width modulation depth change"""
        common_param = EffectParameter.get_common_param_by_name(
            "EFX2_REVERB_SEND_LEVEL"
        )
        address_offset = EffectParameter.get_address_by_name("EFX2_REVERB_SEND_LEVEL")
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_PROGRAM_AREA,  # 0x18
                part=PROGRAM_COMMON,
                group=common_param.address,
                param=address_offset,
                value=value,
            )

    def _create_delay_tab(self):
        """Create Delay tab with parameters"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Create a combo box for Delay Type
        delay_type_combo = QComboBox()
        delay_type_combo.addItems(["OFF", "ON"])
        delay_type_combo.currentIndexChanged.connect(self._on_delay_type_changed)
        layout.addWidget(delay_type_combo)

        # Add Delay parameters
        layout.addWidget(self._create_parameter_slider("DELAY_TIME", "Time (ms)"))
        layout.addWidget(
            self._create_parameter_slider("DELAY_TAP_TIME", "Tap Time (%)")
        )
        layout.addWidget(
            self._create_parameter_slider("DELAY_FEEDBACK", "Feedback (%)")
        )
        layout.addWidget(self._create_parameter_slider("DELAY_HF_DAMP", "HF Damp (Hz)"))
        layout.addWidget(self._create_parameter_slider("DELAY_LEVEL", "Level (0-127)"))
        layout.addWidget(
            self._create_parameter_slider(
                "DELAY_REV_SEND_LEVEL", "Delay to Reverb Send Level (0-127)"
            )
        )

        return widget

    def _create_reverb_section(self):
        """Create Reverb section"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Create a combo box for Reverb Type
        reverb_type_combo = QComboBox()
        reverb_type_combo.addItems(
            ["ROOM1", "ROOM2", "STAGE1", "STAGE2", "HALL1", "HALL2"]
        )
        reverb_type_combo.currentIndexChanged.connect(self._on_reverb_type_changed)
        layout.addWidget(reverb_type_combo)

        # Create sliders for Reverb parameters
        layout.addWidget(self._create_parameter_slider("REVERB_TIME", "Time (0-127)"))
        layout.addWidget(
            self._create_parameter_slider("REVERB_HF_DAMP", "HF Damp (Hz)")
        )
        layout.addWidget(self._create_parameter_slider("REVERB_LEVEL", "Level (0-127)"))

        return widget

    def _on_parameter_changed(self, param_name: str, value: int):
        """Handle parameter change"""
        param = EffectParameter.get_by_name(param_name)
        if param is None:
            logging.error(f"Unknown parameter: {param_name}")
            return

        address_offset, _, _ = param.value

        # Ensure we get a valid common parameter
        common_param = EffectParameter.get_common_param_by_name(param_name)
        if common_param is None:
            logging.error(f"Unknown common parameter type for: {param_name}")
            return

        base_address = common_param.address

        full_address = [0x18, 0x00, base_address, address_offset]
        logging.debug(f"Full address calculated for {param.name}: {full_address}")

        self.midi_helper.send_parameter(
            area=TEMPORARY_PROGRAM_AREA,  # 0x18
            part=PROGRAM_COMMON,
            group=common_param.address,
            param=address_offset,
            value=value,
        )

    def _update_efx2_parameters(self, effect_type: int):
        """Show/hide parameters based on effect type"""
        # Number of parameters for each effect type
        param_counts = {
            0: 0,  # OFF
            5: 8,  # PHASER
            6: 6,  # FLANGER
            7: 4,  # DELAY
            8: 6,  # CHORUS
        }

        # Get number of parameters for current effect
        count = param_counts.get(effect_type, 0)

        # Show/hide parameters
        for i, param in enumerate(self.efx2_additional_params):
            param.setVisible(i < count)

    def _update_delay_parameters(self, show_all: bool = False):
        """Show/hide delay parameters

        Args:
            show_all: If True, show all parameters, otherwise show commonly used ones
        """
        # Common parameter names and indices to show by default
        common_params = {
            0: "Time",
            1: "Feedback",
            2: "High Damp",
            3: "Low Damp",
            4: "Spread",
        }

        for i, param in enumerate(self.delay_params):
            if show_all:
                param.setVisible(True)
                if i in common_params:
                    param.setLabel(common_params[i])
            else:
                param.setVisible(i in common_params)
                if i in common_params:
                    param.setLabel(common_params[i])

    def _on_efx1_type_changed(self, index):
        """Handle changes to the EFX1 type."""
        # Map the combo box index to the effect type value
        effect_type_map = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}  # FLANGER = 5
        effect_type_value = effect_type_map.get(index, 0)

        # Update the effect type parameter
        self._on_parameter_changed("EFX1_TYPE", effect_type_value)

        # Show/hide sliders based on the selected effect type
        is_flanger = effect_type_value == 5
        self.flanger_rate.setVisible(is_flanger)
        self.flanger_depth.setVisible(is_flanger)
        self.flanger_feedback.setVisible(is_flanger)
        self.flanger_manual.setVisible(is_flanger)
        self.flanger_balance.setVisible(is_flanger)

    def _on_efx2_type_changed(self, index):
        """Handle changes to the EFX2 type."""
        # Map the combo box index to the effect type value
        effect_type_map = {0: 0, 1: 5, 2: 6, 3: 7, 4: 8}
        effect_type_value = effect_type_map.get(index, 0)

        # Update the effect type parameter
        self._on_parameter_changed("EFX2_TYPE", effect_type_value)

    def _on_efx1_output_changed(self, index):
        """Handle changes to the EFX1 output assignment."""
        # Map the combo box index to the output assignment value
        output_map = {0: 0, 1: 1}  # DIR = 0, EFX2 = 1
        output_value = output_map.get(index, 0)

        # Update the output assignment parameter
        self._on_parameter_changed("EFX1_OUTPUT_ASSIGN", output_value)

    def _on_reverb_type_changed(self, index):
        """Handle changes to the Reverb type."""
        # Map the combo box index to the reverb type value
        reverb_type_map = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
        reverb_type_value = reverb_type_map.get(index, 0)

        # Update the reverb type parameter
        self._on_parameter_changed("REVERB_TYPE", reverb_type_value)

    def _on_delay_type_changed(self, index):
        """Handle changes to the Delay type."""
        # Map the combo box index to the delay type value
        delay_type_map = {0: 0, 1: 1}  # SINGLE = 0, PAN = 1
        delay_type_value = delay_type_map.get(index, 0)

        # Update the delay type parameter
        self._on_parameter_changed("DELAY_TYPE", delay_type_value)

    def _on_reverb_off_on_changed(self, index):
        """Handle changes to the Delay type."""
        # Map the combo box index to the delay type value
        reverb_off_on_map = {0: 0, 1: 1}  # SINGLE = 0, PAN = 1
        reverb_off_on_value = reverb_off_on_map.get(index, 0)

        # Update the delay type parameter
        self._on_parameter_changed("REVERB_OFF_ON", reverb_off_on_value)
