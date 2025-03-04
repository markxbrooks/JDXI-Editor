import os
from functools import partial

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QComboBox,
    QScrollArea,
    QTabWidget, QFormLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import logging

from jdxi_manager.data.parameter.effects import EffectParameter
from jdxi_manager.data.effects import EffectsCommonParameter
from jdxi_manager.data.parameter.drums import DrumParameter
from jdxi_manager.midi.constants.analog import TEMPORARY_ANALOG_SYNTH_AREA
from jdxi_manager.midi.constants.sysex import TEMPORARY_PROGRAM_AREA
from jdxi_manager.midi.sysex.sysex import PROGRAM_COMMON
from jdxi_manager.ui.editors.base import BaseEditor
from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets.combo_box.combo_box import ComboBox
from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.midi.constants import EFFECTS_AREA
from jdxi_manager.midi.io.helper import MIDIHelper
from typing import Union

from jdxi_manager.ui.widgets.spin_box.spin_box import SpinBox


class EffectsEditor(BaseEditor):
    def __init__(self, midi_helper: MIDIHelper, parent=None):
        super().__init__(midi_helper, parent)
        self.setWindowTitle("Effects")
        self.setFixedWidth(450)
        # Main layout
        main_layout = QVBoxLayout()
        upper_layout = QHBoxLayout()

        self.title_label = QLabel(
            "Effects"
        )
        """
        drum_group.setStyleSheet(
            ""
            QGroupBox {
            width: 300px;
            }
        ""
        )
        """
        self.title_label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
        """
        )
        self.address = 0x00
        main_layout.addLayout(upper_layout)
        upper_layout.addWidget(self.title_label)

        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image
        upper_layout.addWidget(self.image_label)
        self.update_instrument_image()

        self.setLayout(main_layout)
        self.controls: Dict[Union[EffectParameter, EffectsCommonParameter], QWidget] = (
            {}
        )

        # Create address tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(Style.JDXI_TABS)
        main_layout.addWidget(self.tabs)

        # Add tabs
        self.tabs.addTab(self._create_effect1_section(), "Effect 1")
        self.tabs.addTab(self._create_effect2_section(), "Effect 2")
        self.tabs.addTab(self._create_delay_tab(), "Delay")
        self.tabs.addTab(self._create_reverb_section(), "Reverb")

    def update_instrument_image(self):
        image_loaded = False

        def load_and_set_image(image_path):
            """Helper function to load and set the image on the label."""
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaledToHeight(
                    150, Qt.TransformationMode.SmoothTransformation
                )  # Resize to 250px height
                self.image_label.setPixmap(scaled_pixmap)
                return True
            return False

        # Define paths
        default_image_path = os.path.join("resources", "effects", "effects.png")

        if not image_loaded:
            if not load_and_set_image(default_image_path):
                self.image_label.clear()  # Clear label if default image is also missing

    def _update_efx2_parameters(self, effect_type: int):
        """Show/hide parameters based on effect preset_type"""
        # Number of parameters for each effect preset_type
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
        """Create address slider for address parameter with proper display conversion"""
        param = EffectParameter.get_by_name(param_name)
        if param is None:
            logging.error(f"Parameter {param_name} not found.")
            return None

        address, min_val, max_val, _ , _ = param.value
        slider = Slider(label, min_val, max_val, vertical)

        # Use functools.partial to avoid lambda scoping issues
        slider.valueChanged.connect(partial(self._on_parameter_changed, param_name))

        self.controls[param] = slider
        logging.debug(f"Slider created for {param.name} with address {address}")
        return slider

    def _create_effect1_section(self):
        """Create Effect 1 section"""
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)

        # Create address combo box for EFX1 preset_type
        self.efx1_type = self._create_parameter_combo_box(EffectParameter.EFX1_TYPE,
                                                          "Effect 1 Type",
                                                          ["Thru",
                                                           "DISTORTION",
                                                           "FUZZ",
                                                           "COMPRESSOR",
                                                           "BIT CRUSHER"],
                                                          [0, 1, 2, 3, 4])
        layout.addRow("Effect 1 Type", self.efx1_type)

        # Create sliders for EFX1 parameters
        self.efx1_level = self._create_parameter_slider_new(
            EffectParameter.EFX1_LEVEL, "EFX1 Level (0-127)"
        )
        layout.addRow(self.efx1_level)

        self.efx1_delay_send_level = self._create_parameter_slider_new(
            EffectParameter.EFX1_DELAY_SEND_LEVEL, "EFX1 Delay Send Level (0-127)"
        )
        layout.addRow(self.efx1_delay_send_level)

        self.efx1_reverb_send_level = self._create_parameter_slider_new(
            EffectParameter.EFX1_REVERB_SEND_LEVEL, "EFX1 Reverb Send Level (0-127)"
        )
        layout.addRow(self.efx1_reverb_send_level)

        self.efx1_output_assign = self._create_parameter_combo_box(EffectParameter.EFX1_OUTPUT_ASSIGN,
                                                                   "Output Assign",
                                                                   ["DIR", "EFX2"],
                                                                   [0,1])
        layout.addRow("Output Assign", self.efx1_output_assign)

        self.efx1_parameter1_slider = self._create_parameter_slider_new(EffectParameter.EFX1_PARAM_1,
                                                                        "Parameter 1")
        layout.addRow(self.efx1_parameter1_slider)

        self.efx1_parameter2_slider = self._create_parameter_slider_new(EffectParameter.EFX1_PARAM_2,
                                                                        "Parameter 2")
        layout.addRow(self.efx1_parameter2_slider)

        self.efx1_parameter32_slider = self._create_parameter_slider_new(EffectParameter.EFX1_PARAM_32,
                                                                         "Parameter 32")
        layout.addRow(self.efx1_parameter32_slider)

        return widget

    def _create_effect2_section(self):
        """Create Effect 2 section"""
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)

        # Create address combo box for EFX2 preset_type
        self.efx2_type = self._create_parameter_combo_box(EffectParameter.EFX2_TYPE,
                                                          "Effect Type",
                                                          ["OFF", "FLANGER", "PHASER", "RING MOD", "SLICER"],
                                                          [0, 5, 6, 7, 8])
        layout.addRow("Effect 2 Type", self.efx2_type)

        # Create sliders for EFX2 parameters
        self.efx2_level = self._create_parameter_slider(
            "EFX2_LEVEL", "EFX2 Level (0-127)"
        )
        layout.addRow(self.efx2_level)

        self.efx2_delay_send_level = self._create_parameter_slider_new(
            EffectParameter.EFX2_DELAY_SEND_LEVEL, "EFX2 Delay Send Level (0-127)"
        )
        layout.addRow(self.efx2_delay_send_level)

        self.efx2_reverb_send_level = self._create_parameter_slider_new(
            EffectParameter.EFX2_REVERB_SEND_LEVEL, "EFX2 Reverb Send Level (0-127)"
        )
        layout.addRow(self.efx2_reverb_send_level)

        self.efx2_parameter1_slider = self._create_parameter_slider_new(EffectParameter.EFX2_PARAM_1,
                                                                        "Parameter 1")
        layout.addRow(self.efx1_parameter2_slider)

        self.efx2_parameter2_slider = self._create_parameter_slider_new(EffectParameter.EFX2_PARAM_2,
                                                                        "Parameter 2")
        layout.addRow(self.efx2_parameter2_slider)

        self.efx2_parameter32_slider = self._create_parameter_slider_new(EffectParameter.EFX2_PARAM_32,
                                                                         "Parameter 32")
        layout.addRow(self.efx2_parameter32_slider)

        return widget

    def _create_delay_tab(self):
        """Create Delay tab with parameters"""
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)

        # Create address combo box for Delay Type
        delay_level_slider = self._create_parameter_slider_new(EffectParameter.DELAY_LEVEL, "Delay Level")
        layout.addRow(delay_level_slider)

        delay_reverb_send_level_slider = self._create_parameter_slider_new(EffectParameter.DELAY_REVERB_SEND_LEVEL, "Delay to Reverb Send Level")
        layout.addRow(delay_reverb_send_level_slider)

        delay_parameter1_slider = self._create_parameter_slider_new(EffectParameter.DELAY_PARAM_1, "Delay Time (ms)")
        layout.addRow(delay_parameter1_slider)

        delay_parameter2_slider = self._create_parameter_slider_new(EffectParameter.DELAY_PARAM_2, "Delay Tap Time (ms)")
        layout.addRow(delay_parameter2_slider)

        delay_parameter24_slider = self._create_parameter_slider_new(EffectParameter.DELAY_PARAM_24, "Feedback (%)")
        layout.addRow(delay_parameter24_slider)
        return widget

    def _create_reverb_section(self):
        """Create Reverb section"""
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)
        reverb_level_slider = self._create_parameter_slider_new(EffectParameter.REVERB_LEVEL, "Level (0-127)")
        layout.addRow(reverb_level_slider)
        reverb_parameter1_slider = self._create_parameter_slider_new(EffectParameter.REVERB_PARAM_1, "Parameter 1")
        layout.addRow(reverb_parameter1_slider)
        reverb_parameter2_slider = self._create_parameter_slider_new(EffectParameter.REVERB_PARAM_2, "Parameter 2")
        layout.addRow(reverb_parameter2_slider)
        reverb_parameter24_slider = self._create_parameter_slider_new(EffectParameter.REVERB_PARAM_24, "Parameter 24")
        layout.addRow(reverb_parameter24_slider)
        return widget

    def _on_parameter_changed(self, param_name: str, value: int):
        """Handle parameter change"""
        param = EffectParameter.get_by_name(param_name)
        if param is None:
            logging.error(f"Unknown parameter: {param_name}")
            return

        address_offset, _, _, _, _ = param.value

        # Ensure we get address valid common parameter
        common_param = EffectParameter.get_common_param_by_name(param_name)
        if common_param is None:
            logging.error(f"Unknown common parameter preset_type for: {param_name}")
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

    def _create_parameter_slider_new(
        self, param: EffectParameter, label: str = None
    ) -> Slider:
        """Create address slider for address parameter with proper display conversion"""
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val

        slider = Slider(label, display_min, display_max)

        # Connect value changed signal
        slider.valueChanged.connect(lambda v: self._on_parameter_changed_new(param, v))

        # Store control reference
        self.controls[param] = slider
        return slider

    def _create_parameter_combo_box(
        self,
        param: EffectParameter,
        label: str = None,
        options: list = None,
        values: list = None,
    ) -> ComboBox:
        """Create a combo box for a parameter with proper display conversion"""
        combo_box = ComboBox(label, options, values)
        combo_box.valueChanged.connect(lambda v: self._on_parameter_changed_new(param, v))
        self.controls[param] = combo_box
        return combo_box

    def _create_parameter_spin_box(self, param: EffectParameter, label: str = None) -> SpinBox:
        """Create address spin box for address parameter with proper display conversion"""
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val

        spin_box = SpinBox(label, display_min, display_max)

        # Connect value changed signal
        spin_box.valueChanged.connect(lambda v: self._on_parameter_changed_new(param, v))

        # Store control reference
        self.controls[param] = spin_box
        return spin_box

    def _on_parameter_changed_new(self, param: EffectParameter, display_value: int):
        """Handle parameter value changes from UI controls"""
        try:
            # Convert display value to MIDI value if needed
            if hasattr(param, "convert_from_display"):
                midi_value = param.convert_from_display(display_value)
            else:
                midi_value = param.validate_value(display_value)
            logging.info(
                f"parameter: {param} display {display_value} midi value {midi_value}"
            )
            if param in [
                EffectParameter.EFX1_PARAM_1,
                EffectParameter.EFX1_PARAM_2,
                EffectParameter.EFX1_PARAM_32,
                EffectParameter.EFX2_PARAM_1,
                EffectParameter.EFX2_PARAM_2,
                EffectParameter.EFX2_PARAM_32,
                EffectParameter.DELAY_PARAM_1,
                EffectParameter.DELAY_PARAM_2,
                EffectParameter.DELAY_PARAM_24,
                EffectParameter.REVERB_PARAM_1,
                EffectParameter.REVERB_PARAM_2,
                EffectParameter.REVERB_PARAM_24,
            ]:
                size = 4
            else:
                size = 1
            logging.info(
                f"parameter param {param} value {display_value} size {size} sent"
            )
            # Ensure we get address valid common parameter
            common_param = EffectParameter.get_common_param_by_name(param.name)
            if common_param is None:
                logging.error(f"Unknown common parameter preset_type for: {param.name}")
                return
            try:
                # Ensure value is included in the MIDI message
                return self.midi_helper.send_parameter(
                    area=TEMPORARY_PROGRAM_AREA,
                    part=PROGRAM_COMMON,
                    group=common_param.address,
                    param=param.address,
                    value=display_value,  # Make sure this value is being sent
                    size=size,
                )
            except Exception as ex:
                logging.error(f"MIDI error setting {param}: {str(ex)}")
                return False

        except Exception as ex:
            logging.error(f"Error handling parameter {param.name}: {str(ex)}")
            return False

