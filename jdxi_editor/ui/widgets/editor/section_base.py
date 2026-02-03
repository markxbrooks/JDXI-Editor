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

from typing import Any, Callable, Dict, Literal, Optional, Union

from decologr import Decologr as log
from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QTabWidget, QVBoxLayout, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.digital.filter import DigitalFilterMode
from jdxi_editor.midi.data.digital.oscillator import WaveformType
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.analog.spec import AnalogFilterMode
from jdxi_editor.midi.data.parameter.digital import DigitalPartialParam
from jdxi_editor.midi.data.parameter.digital.spec import (
    JDXiMidiDigital,
    TabDefinitionMixin,
)
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.adsr.spec import ADSRSpec, ADSRStage
from jdxi_editor.ui.editors.synth.base import SynthBase
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.style import JDXiUIStyle
from jdxi_editor.ui.widgets.adsr.adsr import ADSR
from jdxi_editor.ui.widgets.editor.helper import (
    create_envelope_group,
    create_group_with_layout,
    create_layout_with_widgets,
    transfer_layout_items,
)
from jdxi_editor.ui.widgets.editor.icon_type import IconType
from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec, SwitchSpec


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
    SYNTH_SPEC = JDXiMidiDigital

    def __init__(
        self,
        send_midi_parameter: Callable = None,
        midi_helper: Optional[MidiIOHelper] = None,
        controls: dict = None,
        address: RolandSysExAddress = None,
        parent: Optional[QWidget] = None,
        icons_row_type: Literal[
            IconType.ADSR, IconType.OSCILLATOR, IconType.GENERIC, IconType.NONE
        ] = "adsr",
        analog: bool = False,
    ):
        """
        Initialize the SectionBaseWidget.

        :param parent: Parent widget
        :param icons_row_type: Type of icon row to add ("adsr", "oscillator", "generic", or "none")
        :param analog: Whether to apply analog-specific styling
        :param midi_helper: Optional MIDI helper for communication
        """
        super().__init__(midi_helper=midi_helper, parent=parent)
        self.controls: Dict[Union[DigitalPartialParam], QWidget] = controls or {}
        self.analog: bool = analog
        self.icons_row_type = icons_row_type
        self._layout: Optional[QVBoxLayout] = None
        self._icon_added: bool = False

        self.midi_helper = midi_helper
        self.address: RolandSysExAddress | None = address
        self.send_midi_parameter = send_midi_parameter

        self.tab_widget = None
        self.adsr_widget = None
        self.control_widgets = []
        self.button_widgets = {}

        self.button_widgets: dict[Any, QPushButton] = {}
        self.slider_widgets: dict[Any, QWidget] = {}
        self.build_widgets()
        if not self.analog:
            self._setup_ui()
            if self.BUTTON_SPECS:
                self._initialize_button_states()

    def get_parent_midi_helper(self, parent: QWidget | None):
        if parent and hasattr(parent, "midi_helper"):
            midi_helper = parent.midi_helper
            return midi_helper
        return None

        # -------------------------------
        # Layout & Tabs
        # -------------------------------

    def _setup_ui(self):
        """Assemble section UI"""
        layout = self.create_layout()
        if self.button_widgets:
            button_layout = self._create_button_row_layout()
            if button_layout is not None:
                layout.addLayout(button_layout)
        self._create_tab_widget()
        layout.addWidget(self.tab_widget)
        # layout.addStretch()

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

    # -------------------------------
    # Build Widgets
    # -------------------------------
    def build_widgets(self):
        """Build sliders, switches, combo boxes, buttons, and ADSR"""
        class_name = self.__class__.__name__
        is_filter_section = class_name == "DigitalFilterSection"

        if is_filter_section:
            log.message(f"🔧 {class_name}.build_widgets() called")
            log.message(f"📋 PARAM_SPECS count: {len(self.PARAM_SPECS)}")
            log.message(f"📋 ADSR_SPEC: {self.ADSR_SPEC if self.ADSR_SPEC else 'None'}")

            # --- Check if FILTER_ENV_DEPTH is in PARAM_SPECS
            filter_env_depth_in_specs = any(
                (hasattr(spec.param, "name") and spec.param.name == "FILTER_ENV_DEPTH")
                or (spec.param == DigitalPartialParam.FILTER_ENV_DEPTH)
                for spec in self.PARAM_SPECS
            )
            if filter_env_depth_in_specs:
                log.message(f"✅ FILTER_ENV_DEPTH found in PARAM_SPECS")
            else:
                log.warning(f"⚠️ FILTER_ENV_DEPTH NOT in PARAM_SPECS!")

        self._create_parameter_widgets()
        if self.BUTTON_SPECS:
            self._create_waveform_buttons()
        if self.ADSR_SPEC:
            self._create_adsr()

    def _create_tab_widget(self):
        """Override to add Pan slider in its own horizontal layout"""

        self.tab_widget = QTabWidget()

        controls_widget = self._create_controls_widget()
        self._add_tab(key=self.SYNTH_SPEC.Amp.Tab.CONTROLS, widget=controls_widget)

        # --- ADSR tab if any
        if self.adsr_widget:
            adsr_group = create_envelope_group(
                "Envelope", adsr_widget=self.adsr_widget, analog=self.analog
            )
            self._add_tab(key=self.SYNTH_SPEC.Amp.Tab.ADSR, widget=adsr_group)

    def _create_controls_widget(self) -> QWidget:
        # Controls tab
        controls_widget = QWidget()
        controls_layout = create_layout_with_widgets(self.control_widgets)
        controls_widget.setLayout(controls_layout)
        return controls_widget

    def _create_parameter_widgets(self):
        """Create widgets from PARAM_SPECS declaratively"""
        class_name = self.__class__.__name__
        is_filter_section = class_name == "DigitalFilterSection"

        if is_filter_section:
            log.message(
                f"🔧 Creating parameter widgets from {len(self.PARAM_SPECS)} specs"
            )

        for spec in self.PARAM_SPECS:
            param_name = getattr(spec.param, "name", str(spec.param))
            is_filter_env_depth = (
                hasattr(spec.param, "name") and spec.param.name == "FILTER_ENV_DEPTH"
            ) or (spec.param == DigitalPartialParam.FILTER_ENV_DEPTH)

            if is_filter_env_depth and is_filter_section:
                log.message(
                    f"🎯 Found FILTER_ENV_DEPTH in PARAM_SPECS: {spec.param}, label: {spec.label}"
                )

            if isinstance(spec, SliderSpec):
                widget = self._create_parameter_slider(
                    spec.param, spec.label, vertical=spec.vertical
                )
                if is_filter_env_depth and is_filter_section:
                    log.message(
                        f"✅ Created FILTER_ENV_DEPTH slider widget: {widget}, type: {type(widget)}"
                    )
            elif isinstance(spec, SwitchSpec):
                widget = self._create_parameter_switch(
                    spec.param, spec.label, spec.options
                )
            elif isinstance(spec, ComboBoxSpec):
                widget = self._create_parameter_combo_box(
                    spec.param, spec.label, options=spec.options
                )
            else:
                if is_filter_env_depth and is_filter_section:
                    log.warning(
                        f"⚠️ FILTER_ENV_DEPTH spec is not SliderSpec/SwitchSpec/ComboBoxSpec: {type(spec)}"
                    )
                continue

            self.controls[spec.param] = widget
            if is_filter_env_depth and is_filter_section:
                log.message(
                    f"📝 Stored FILTER_ENV_DEPTH in controls dict: {spec.param} -> {widget}"
                )
                log.message(f"📊 Controls dict now has {len(self.controls)} entries")

            self.control_widgets.append(widget)
            if is_filter_env_depth and is_filter_section:
                log.message(
                    f"📦 Added FILTER_ENV_DEPTH to control_widgets list (total: {len(self.control_widgets)})"
                )

    def _update_button_enabled_states(self, button_param):
        """Enable/disable controls based on BUTTON_ENABLE_RULES"""
        # Disable all first
        for attrs in self.BUTTON_ENABLE_RULES.values():
            for attr in attrs:
                getattr(self, attr, None).setEnabled(False)
        # Enable per selected button
        for attr in self.BUTTON_ENABLE_RULES.get(button_param, []):
            getattr(self, attr, None).setEnabled(True)

    def _initialize_button_states(self):
        """Set initial button state (first in BUTTON_SPECS)"""
        if self.BUTTON_SPECS:
            first_param = self.BUTTON_SPECS[0].param
            self._on_button_selected(first_param)

    def _create_button_row_layout(self):
        """Create layout for button row. Override in subclasses."""
        if not self.button_widgets:
            return None
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addLayout(create_layout_with_widgets(list(self.button_widgets.values())))
        layout.addStretch()
        return layout

    def _create_adsr(self):
        """Create ADSR widget from ADSR_SPEC"""
        from decologr import Decologr as log

        class_name = self.__class__.__name__
        is_filter_section = class_name == "DigitalFilterSection"

        if is_filter_section:
            log.message(f"🔧 Creating ADSR widget from ADSR_SPEC")
            log.message(f"📋 ADSR_SPEC keys: {list(self.ADSR_SPEC.keys())}")

        # Handle both string keys and ADSRType enum keys

        attack_key = (
            ADSRStage.ATTACK
        )  # if "attack" in self.ADSR_SPEC else ADSRType.ATTACK
        decay_key = ADSRStage.DECAY  # if "decay" in self.ADSR_SPEC else ADSRType.DECAY
        sustain_key = (
            ADSRStage.SUSTAIN
        )  # if "sustain" in self.ADSR_SPEC else ADSRType.SUSTAIN
        release_key = (
            ADSRStage.RELEASE
        )  # "release" in self.ADSR_SPEC else ADSRType.RELEASE
        peak_key = ADSRStage.PEAK  #  if "peak" in self.ADSR_SPEC else ADSRType.PEAK

        # Extract parameters from ADSR_SPEC (handles both ADSRSpec objects and direct parameters)
        def get_param(spec_or_param):
            """Extract parameter from ADSRSpec or return parameter directly"""
            if isinstance(spec_or_param, ADSRSpec):
                return spec_or_param.param
            return spec_or_param

        attack_spec = self.ADSR_SPEC.get(attack_key)
        decay_spec = self.ADSR_SPEC.get(decay_key)
        sustain_spec = self.ADSR_SPEC.get(sustain_key)
        release_spec = self.ADSR_SPEC.get(release_key)
        peak_spec = self.ADSR_SPEC.get(peak_key) if peak_key else None

        attack_param = get_param(attack_spec) if attack_spec else None
        decay_param = get_param(decay_spec) if decay_spec else None
        sustain_param = get_param(sustain_spec) if sustain_spec else None
        release_param = get_param(release_spec) if release_spec else None
        peak_param = get_param(peak_spec) if peak_spec else None

        if peak_param:
            peak_name = getattr(peak_param, "name", str(peak_param))
            if is_filter_section:
                log.message(f"🎯 ADSR peak_param: {peak_param} (name: {peak_name})")
            is_filter_env_depth = (
                hasattr(peak_param, "name") and peak_param.name == "FILTER_ENV_DEPTH"
            ) or (peak_param == DigitalPartialParam.FILTER_ENV_DEPTH)
            if is_filter_env_depth and is_filter_section:
                log.message(f"✅ Peak param is FILTER_ENV_DEPTH")
                # Check if it exists in controls
                if peak_param in self.controls:
                    existing_widget = self.controls[peak_param]
                    log.message(
                        f"📝 FILTER_ENV_DEPTH already in controls: {existing_widget}, type: {type(existing_widget)}"
                    )
                else:
                    log.warning(f"⚠️ FILTER_ENV_DEPTH NOT found in controls dict!")
                    log.message(f"📊 Controls dict has {len(self.controls)} entries")
                    log.message(
                        f"📋 Controls keys: {[getattr(k, 'name', str(k)) for k in self.controls.keys()]}"
                    )
        else:
            if is_filter_section:
                log.warning(f"⚠️ No peak parameter in ADSR_SPEC")

        self.adsr_widget = ADSR(
            attack_param=attack_param,
            decay_param=decay_param,
            sustain_param=sustain_param,
            release_param=release_param,
            peak_param=peak_param,  # Optional peak parameter
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
            analog=self.analog,
        )

        if peak_param and is_filter_section:
            peak_name = getattr(peak_param, "name", str(peak_param))
            log.message(f"✅ ADSR widget created with peak_param: {peak_name}")
            if hasattr(self.adsr_widget, "peak_control"):
                log.message(
                    f"✅ ADSR widget has peak_control: {self.adsr_widget.peak_control}, type: {type(self.adsr_widget.peak_control)}"
                )
            else:
                log.warning(f"⚠️ ADSR widget does NOT have peak_control attribute")

    def _add_centered_row(self, *widgets: QWidget) -> None:
        """add centered row"""
        row = QHBoxLayout()
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
            if not self.analog:
                btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)
            else:
                btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)
            # --- Create icon if icon_name is provided
            if icon_name_str:
                icon = None
                try:
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
                JDXi.UI.Dimensions.WaveformIcon.WIDTH,
                JDXi.UI.Dimensions.WaveformIcon.HEIGHT,
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
        peak_spec = self.ADSR_SPEC.get(ADSRStage.PEAK)

        attack_param = get_param(attack_spec) if attack_spec else None
        decay_param = get_param(decay_spec) if decay_spec else None
        sustain_param = get_param(sustain_spec) if sustain_spec else None
        release_param = get_param(release_spec) if release_spec else None
        peak_param = get_param(peak_spec) if peak_spec else None

        amp_env_adsr_widget = ADSR(
            attack_param=attack_param,
            decay_param=decay_param,
            sustain_param=sustain_param,
            release_param=release_param,
            peak_param=peak_param,
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
        if hasattr(self, "tab_widget") and self.tab_widget is not None:
            tab_widget = self.tab_widget
        else:
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
        widget.setMaximumHeight(JDXi.UI.Dimensions.EDITOR.HEIGHT)
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
            self._create_parameter_combo_box(
                spec.param, spec.label, spec.options, spec.values
            )
            for spec in specs
        ]

    def _build_switches(self, specs: list["SwitchSpec"]):
        return [
            self._create_parameter_switch(spec.param, spec.label, spec.options)
            for spec in specs
        ]

    # -------------------------------
    # Button Logic
    # -------------------------------

    def _on_button_selected(self, button_param):
        """Handle button selection & enabling dependent widgets"""
        if button_param is None:
            return
        for btn in self.button_widgets.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)
        selected_btn = self.button_widgets.get(button_param)
        if selected_btn is None:
            return
        selected_btn.setChecked(True)
        # selected_btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE_ANALOG)
        self._update_button_enabled_states(button_param)
        if self.send_midi_parameter:
            # Map filter mode enums to their corresponding parameter
            if isinstance(button_param, DigitalFilterMode):
                # Filter mode buttons map to FILTER_MODE_SWITCH parameter
                actual_param = DigitalPartialParam.FILTER_MODE_SWITCH
                param_value = button_param.value
            elif isinstance(button_param, AnalogFilterMode):
                # Filter mode buttons map to FILTER_MODE_SWITCH parameter
                actual_param = AnalogParam.FILTER_MODE_SWITCH
                param_value = button_param.value
            else:
                # For other button types (like waveform), use the param directly
                actual_param = button_param
                param_value = getattr(button_param, "value", button_param)

            if actual_param is None:
                return
            # Ensure we have a valid AddressParameter before sending
            if not isinstance(actual_param, AddressParameter):
                from decologr import Decologr as log

                log.error(
                    f"Cannot send MIDI: {button_param} is not an AddressParameter (got {type(button_param)})"
                )
                return

            self.send_midi_parameter(actual_param, param_value)

    def add_widget_lists_to_layout(self, layout, widget_lists: list[list]):
        """add a list of rows of widgets to a layout"""
        for widget_list in widget_lists:
            layout.addLayout(
                    create_layout_with_widgets(widget_list)
                    )
                
    def _setup_group_with_widget_rows(self, label: str, widget_rows: list[list]):
        """setup group box with a list of widgets"""
        layout = self.get_layout()
        group, group_layout = create_group_with_layout(label=label)
        layout.addWidget(group)
        group.setStyleSheet(JDXiUIStyle.ADSR)
        self.add_widget_lists_to_layout(group_layout, widget_rows)
        group_layout.addStretch()