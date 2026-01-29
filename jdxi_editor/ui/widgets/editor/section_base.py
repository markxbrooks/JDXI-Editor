"""
Section Base Widget

This module provides the `SectionBaseWidget` class, which provides a common base
for all editor sections. It automatically adds standardized icon rows based on
section type, ensuring consistency across all tabs.

Classes:
--------
- `SectionBaseWidget`: Base widget that automatically adds icon rows to sections.

Features:
---------
- Automatic icon row addition based on section type
- Consistent layout structure
- Theme-aware styling (analog vs regular)
- Easy to subclass for new sections

Usage Example:
--------------
    # In a section's __init__ or setup_ui method:

    class MySection(SectionBaseWidget):
        def __init__(self, ...):
            super().__init__(icon_type="adsr", analog=False)
            # Your initialization code
            self.setup_ui()

        def setup_ui(self):
            layout = self.get_layout()  # Gets the QVBoxLayout with icon row already added
            # Add your controls to layout
            layout.addWidget(my_widget)

"""

from typing import Any, Callable, Literal, Optional

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.digital.filter import DigitalFilterMode
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.data.parameter.digital.spec import TabDefinitionMixin
from jdxi_editor.ui.adsr.spec import ADSRStage, ADSRSpec
from jdxi_editor.ui.editors.synth.base import SynthBase
from jdxi_editor.ui.editors.widget_specs import SliderSpec, SwitchSpec, ComboBoxSpec
from jdxi_editor.ui.widgets.adsr.adsr import ADSR
from jdxi_editor.ui.widgets.editor.helper import transfer_layout_items, create_envelope_group
from jdxi_editor.ui.widgets.editor.icon_type import IconType
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon


class SectionBaseWidget(SynthBase):
    """
    Base widget for editor sections that automatically adds icon rows.

    This widget standardizes section structure by automatically adding
    appropriate icon rows based on section type, reducing boilerplate
    and ensuring consistency.
    """
    ADSR_SPEC: dict[ADSRStage, ADSRSpec] = {}
    WAVEFORM_SPECS: list[SliderSpec] = []
    SLIDER_GROUPS: dict[str, list[SliderSpec]] = {}
    BUTTON_ENABLE_RULES: dict[Any, list[str]] = {}
    ENVELOPE_WIDGET_FACTORIES: list[Callable] = []
    PARAM_SPECS: list = []  # list of SliderSpec / SwitchSpec / ComboBoxSpec
    BUTTON_SPECS: list = []  # optional waveform/mode/shape buttons

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        icons_row_type: Literal[
            IconType.ADSR, IconType.OSCILLATOR, IconType.GENERIC, IconType.NONE
        ] = "adsr",
        analog: bool = False,
        midi_helper: Optional[MidiIOHelper] = None,
    ):
        """
        Initialize the SectionBaseWidget.

        :param parent: Parent widget
        :param icons_row_type: Type of icon row to add ("adsr", "oscillator", "generic", or "none")
        :param analog: Whether to apply analog-specific styling
        :param midi_helper: Optional MIDI helper for communication
        """
        super().__init__(midi_helper=midi_helper, parent=parent)
        self.address: RolandSysExAddress | None = None
        self.analog: bool = analog
        self.icons_row_type = icons_row_type
        self._layout: Optional[QVBoxLayout] = None
        self._icon_added: bool = False

        self.button_widgets: dict[Any, QPushButton] = {}
        self.slider_widgets: dict[Any, QWidget] = {}

    def get_layout(
        self,
        margins: tuple[int, int, int, int] = None,
        spacing: int = None,
    ) -> QVBoxLayout:
        """
        Get or create the main layout for this section.

        If the layout doesn't exist, creates it and adds the icon row.
        This should be called at the start of setup_ui() or init_ui().

        :param margins: Optional tuple of (left, top, right, bottom) margins
        :param spacing: Optional spacing between widgets
        :return: The main QVBoxLayout
        """
        if self._layout is None:
            self._layout = QVBoxLayout()
            self.setLayout(self._layout)

            # Set margins and spacing if provided
            if margins is not None:
                # Margins class now has __iter__, so it can be unpacked directly
                # Also handles tuples/lists for backward compatibility
                self._layout.setContentsMargins(*margins)
            if spacing is not None:
                self._layout.setSpacing(spacing)

            # Apply styling
            JDXi.UI.Theme.apply_adsr_style(self, analog=self.analog)

            # Add icon row if not disabled
            if self.icons_row_type != IconType.NONE and not self._icon_added:
                self._add_icon_row()
                self._icon_added = True

        return self._layout

    def _add_centered_row(self, *widgets: QWidget) -> None:
        """add centered row"""
        row = QHBoxLayout()
        row.addStretch()
        for w in widgets:
            row.addWidget(w)
        row.addStretch()
        self.get_layout().addLayout(row)
        
    def _create_waveform_buttons(self):
        """Create mode/waveform/shape buttons from BUTTON_SPECS"""

        for spec in self.BUTTON_SPECS:
            # --- Handle both SliderSpec (has 'label') and other specs (may have 'name')
            button_label = getattr(spec, "label", getattr(spec, "name", "Button"))
            icon_name_str = getattr(spec, "icon_name", None)

            # --- Create button
            btn = QPushButton(button_label)
            btn.setCheckable(True)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)

            # --- Create icon if icon_name is provided
            if icon_name_str:
                icon = None
                try:
                    # Try to get the WaveformIconType value (it's a class with string constants)
                    from jdxi_editor.midi.data.digital.oscillator import (
                        WaveformType,
                    )

                    # Check if icon_name_str matches a WaveformIconType attribute
                    icon_type_value = getattr(WaveformType, icon_name_str, None)
                    if icon_type_value is not None:
                        # Use generate_waveform_icon directly for waveform/filter icons
                        icon_base64 = generate_waveform_icon(
                            icon_type_value, JDXi.UI.Style.WHITE, 1.0
                        )
                        pixmap = base64_to_pixmap(icon_base64)
                        if pixmap and not pixmap.isNull():
                            icon = QIcon(pixmap)
                except (AttributeError, KeyError, TypeError):
                    pass

                # If not a waveform icon, try registry or QTA
                if icon is None or icon.isNull():
                    try:
                        # Try to get icon from registry (which also uses generate_waveform_icon)
                        icon = JDXi.UI.Icon.get_generated_icon(icon_name_str)
                    except (AttributeError, KeyError):
                        try:
                            # Try to create from QTA icon name
                            from jdxi_editor.ui.widgets.editor.helper import (
                                create_icon_from_qta,
                            )

                            icon = create_icon_from_qta(icon_name_str)
                        except:
                            icon = None

                if icon and not icon.isNull():
                    btn.setIcon(icon)
                    btn.setIconSize(
                        QSize(
                            JDXi.UI.Dimensions.LFOIcon.WIDTH,
                            JDXi.UI.Dimensions.LFOIcon.HEIGHT,
                        )
                    )

            btn.setFixedSize(
                JDXi.UI.Dimensions.WAVEFORM_ICON.WIDTH,
                JDXi.UI.Dimensions.WAVEFORM_ICON.HEIGHT,
            )

            btn.clicked.connect(lambda _, b=spec.param: self._on_button_selected(b))
            self.button_widgets[spec.param] = btn
            # Only store in controls if it's a parameter enum, not a mode enum (like DigitalFilterMode)
            if not isinstance(spec.param, DigitalFilterMode):
                self.controls[spec.param] = btn

        # For compatibility with code that expects filter_mode_buttons (DigitalFilterSection)
        # or wave_buttons (DigitalOscillatorSection), create an alias
        if hasattr(self, "BUTTON_SPECS") and self.BUTTON_SPECS:
            # Check if this is a filter section by checking the first param type
            first_param = self.BUTTON_SPECS[0].param
            if isinstance(first_param, DigitalFilterMode):
                self.filter_mode_buttons = self.button_widgets

    def _add_icon_row(self) -> None:
        """Add the appropriate icon row based on icon_type"""
        if self._layout is None:
            return

        # Create a container layout to avoid "already has a parent" errors
        icon_row_container = QHBoxLayout()

        if self.icons_row_type == IconType.ADSR:
            icon_hlayout = JDXi.UI.Icon.create_adsr_icons_row()
        elif self.icons_row_type == IconType.OSCILLATOR:
            icon_hlayout = JDXi.UI.Icon.create_oscillator_icons_row()
        elif self.icons_row_type == IconType.GENERIC:
            icon_hlayout = JDXi.UI.Icon.create_generic_musical_icon_row()
        else:
            return  # IconType.NONE or unknown

        # Transfer all items from icon_hlayout to icon_row_container

        transfer_layout_items(icon_hlayout, icon_row_container)

        self._layout.addLayout(icon_row_container)

    def _create_adsr_group(self):
        """Create amp ADSR envelope using standardized helper"""
        self.adsr_widget = self.build_adsr_widget()
        self.adsr_group = create_envelope_group(
            name="Envelope",
            adsr_widget=self.adsr_widget,
            analog=self.analog,
        )

    def build_adsr_widget(self) -> ADSR:
        # --- Extract parameters from ADSRSpec objects
        def get_param(spec_or_param):
            """Extract parameter from ADSRSpec or return parameter directly"""
            if isinstance(spec_or_param, ADSRSpec):
                return spec_or_param.param
            return spec_or_param

        attack_spec = self.ADSR_SPEC.get(ADSRStage.ATTACK)
        decay_spec = self.ADSR_SPEC.get(ADSRStage.DECAY)
        sustain_spec = self.ADSR_SPEC.get(ADSRStage.SUSTAIN)
        release_spec = self.ADSR_SPEC.get(ADSRStage.RELEASE)

        attack_param = get_param(attack_spec) if attack_spec else None
        decay_param = get_param(decay_spec) if decay_spec else None
        sustain_param = get_param(sustain_spec) if sustain_spec else None
        release_param = get_param(release_spec) if release_spec else None

        amp_env_adsr_widget = ADSR(
            attack_param=attack_param,
            decay_param=decay_param,
            sustain_param=sustain_param,
            release_param=release_param,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            address=self.address,
            controls=self.controls,
            analog=self.analog,
        )
        return amp_env_adsr_widget

    def setup_ui(self) -> None:
        """
        Setup the UI for this section.

        Subclasses should override this method and call get_layout()
        at the start to ensure the icon row is added.

        Example:
            def setup_ui(self):
                layout = self.get_layout()
                layout.addWidget(my_widget)
        """
        # Default implementation - subclasses should override
        self.get_layout()

    def init_ui(self) -> None:
        """
        Initialize the UI for this section.

        Alias for setup_ui() for sections that use init_ui() naming.
        Subclasses can override either setup_ui() or init_ui().
        """
        self.setup_ui()

    def _add_tab(
        self,
        *,
        key: TabDefinitionMixin,
        widget: QWidget,
    ) -> None:
        """Add a tab using TabDefinitionMixin pattern"""
        from jdxi_editor.midi.data.digital.oscillator import WaveformType
        
        # Handle both regular icons and generated waveform icons
        waveform_type_values = {
            WaveformType.ADSR,
            WaveformType.UPSAW,
            WaveformType.SQUARE,
            WaveformType.PWSQU,
            WaveformType.TRIANGLE,
            WaveformType.SINE,
            WaveformType.SAW,
            WaveformType.SPSAW,
            WaveformType.PCM,
            WaveformType.NOISE,
            WaveformType.LPF_FILTER,
            WaveformType.HPF_FILTER,
            WaveformType.BYPASS_FILTER,
            WaveformType.BPF_FILTER,
            WaveformType.FILTER_SINE,
        }
        
        # Find the tab widget (could be tab_widget or oscillator_tab_widget, etc.)
        tab_widget = None
        if hasattr(self, 'tab_widget') and self.tab_widget is not None:
            tab_widget = self.tab_widget
        elif hasattr(self, 'oscillator_tab_widget') and self.oscillator_tab_widget is not None:
            tab_widget = self.oscillator_tab_widget
        else:
            from PySide6.QtWidgets import QTabWidget
            self.tab_widget = QTabWidget()
            tab_widget = self.tab_widget
        
        # Handle icon - could be a string (qtawesome icon name) or WaveformType value
        if isinstance(key.icon, str) and key.icon in waveform_type_values:
            # Use generated icon for waveform types
            icon = JDXi.UI.Icon.get_generated_icon(key.icon)
        elif isinstance(key.icon, str) and key.icon.startswith("mdi."):
            # Direct qtawesome icon name (e.g., "mdi.numeric-1-circle-outline")
            icon = JDXi.UI.Icon.get_icon(key.icon, color=JDXi.UI.Style.GREY)
        else:
            # Use regular icon from registry
            icon = JDXi.UI.Icon.get_icon(key.icon, color=JDXi.UI.Style.GREY)
        
        tab_widget.addTab(
            widget,
            icon,
            key.label,
        )
        setattr(self, key.attr_name, widget)

    def create_layout(self):
        """create main rows layout"""
        layout = self.get_layout(
            margins=JDXi.UI.Dimensions.EDITOR_DIGITAL.MARGINS,
            spacing=JDXi.UI.Dimensions.EDITOR_DIGITAL.SPACING,
        )
        layout.addSpacing(JDXi.UI.Dimensions.EDITOR_DIGITAL.SPACING)
        return layout

    def _build_sliders(self, specs: list["SliderSpec"]):
        return [
            self._create_parameter_slider(
                spec.param,
                spec.label,
                vertical=spec.vertical,
            )
            for spec in specs
        ]

    def _build_combo_boxes(self, specs: list["ComboBoxSpec"]):
        return [
            self._create_parameter_combo_box(spec.param, spec.label, spec.options, spec.values)
            for spec in specs
        ]

    def _build_switches(self, specs: list["SwitchSpec"]):
        return [
            self._create_parameter_switch(spec.param, spec.label, spec.options)
            for spec in specs
        ]

    def _on_button_selected(self, b):
        pass
