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
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.digital.filter import DigitalFilterMode
from jdxi_editor.midi.data.digital.oscillator import WaveForm
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
from jdxi_editor.ui.widgets.adsr.adsr import ADSR
from jdxi_editor.ui.widgets.editor.helper import (
    create_button_with_icon,
    create_envelope_group,
    create_group_with_layout,
    create_icon_from_qta,
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
    SLIDER_GROUPS: dict[str, list] = {}  # e.g. {"controls": [SliderSpec, ...], "pan": [...]}
    BUTTON_ENABLE_RULES: dict[Any, list[str]] = {}
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
        self.wave_shape_param: list | None = None
        self.wave_shape_buttons = None
        # Only set default if subclass (e.g. oscillator/filter) did not set wave_shapes before super().__init__()
        if not hasattr(self, "wave_shapes"):
            self.wave_shapes: list | None = None
        self.wave_shape_icon_map: dict | None = None
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
        self.tuning_control_widgets = []
        self.button_widgets = {}

        self.button_widgets: dict[Any, QPushButton] = {}
        self.slider_widgets: dict[Any, QWidget] = {}
        self.build_widgets()
        if not self.analog:
            self._setup_ui()
            if self._get_button_specs():
                self._initialize_button_states()

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
        self._create_parameter_widgets()
        if self._get_button_specs():
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
        """Controls tab"""
        controls_widget = QWidget()
        controls_layout = create_layout_with_widgets(self.tuning_control_widgets)
        controls_widget.setLayout(controls_layout)
        return controls_widget

    def _get_param_specs(self) -> list:
        """Return the main list of specs for widget creation: SLIDER_GROUPS['controls'] when present."""
        return self.SLIDER_GROUPS.get("controls", [])

    def _create_parameter_widgets(self):
        """Create widgets from SLIDER_GROUPS['controls'] (sliders, switches, combos)."""
        for spec in self._get_param_specs():
            if isinstance(spec, SliderSpec):
                widget = self._create_parameter_slider(
                    spec.param, spec.label, vertical=spec.vertical
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
                continue

            self.controls[spec.param] = widget
            self.tuning_control_widgets.append(widget)

    def _update_button_enabled_states(self, button_param):
        """Enable/disable controls based on BUTTON_ENABLE_RULES"""
        # --- Disable all first
        for attrs in self.BUTTON_ENABLE_RULES.values():
            for attr in attrs:
                getattr(self, attr, None).setEnabled(False)
        # --- Enable per selected button
        for attr in self.BUTTON_ENABLE_RULES.get(button_param, []):
            getattr(self, attr, None).setEnabled(True)

    def _initialize_button_states(self):
        """Set initial button state (first in wave_shapes / BUTTON_SPECS). Uses spec.param (SliderSpec and WaveShapeSpec both expose .param)."""
        specs = self._get_button_specs()
        if specs:
            first_param = getattr(specs[0], "param", None)
            if first_param is not None:
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
        attack_key = ADSRStage.ATTACK
        decay_key = ADSRStage.DECAY
        sustain_key = ADSRStage.SUSTAIN
        release_key = ADSRStage.RELEASE
        peak_key = ADSRStage.PEAK

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

        self.adsr_widget = ADSR(
            attack_param=attack_param,
            decay_param=decay_param,
            sustain_param=sustain_param,
            release_param=release_param,
            peak_param=peak_param,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
            analog=self.analog,
        )

    def _add_centered_row(self, *widgets: QWidget) -> None:
        """add centered row"""
        row = QHBoxLayout()
        for w in widgets:
            row.addWidget(w)
        row.addStretch()
        self.get_layout().addLayout(row)

    def _get_button_specs(self):
        """Return list of button specs: wave_shapes when set by subclass, else BUTTON_SPECS."""
        return getattr(self, "wave_shapes", None) or self.BUTTON_SPECS

    def _create_waveform_buttons(self):
        """Create mode/waveform/shape buttons from wave_shapes or BUTTON_SPECS."""
        for spec in self._get_button_specs():
            # --- Handle both SliderSpec (has 'label') and other specs (may have 'name')
            button_label = getattr(spec, "label", getattr(spec, "name", "Button"))
            icon_name_str = getattr(spec, "icon_name", None)

            # --- Create button
            btn = QPushButton(button_label)
            btn.setCheckable(True)
            if self.analog:
                JDXi.UI.Theme.apply_button_rect_analog(btn)
            else:
                btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)
            # --- Create icon if icon_name is provided
            if icon_name_str:
                icon = None
                try:
                    # Check if icon_name_str matches a WaveformIconType attribute
                    icon_type_value = getattr(WaveForm, icon_name_str, None)
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

                # --- If not a waveform icon, try registry or QTA
                if icon is None or icon.isNull():
                    try:
                        # --- Try to get icon from registry (which also uses generate_waveform_icon)
                        icon = JDXi.UI.Icon.get_generated_icon(icon_name_str)
                    except (AttributeError, KeyError):
                        try:
                            # --- Try to create from QTA icon name
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
            # --- Only store in controls if it's a parameter enum, not a mode enum (like DigitalFilterMode)
            if not isinstance(spec.param, DigitalFilterMode):
                self.controls[spec.param] = btn

        # --- For compatibility with code that expects filter_mode_buttons (DigitalFilterSection)
        specs = self._get_button_specs()
        if specs and isinstance(specs[0].param, DigitalFilterMode):
            self.filter_mode_buttons = self.button_widgets

    def _add_icon_row(self) -> None:
        """Add the appropriate icon row based on icon_type"""
        if self._layout is None:
            return

        # --- Create a container layout to avoid "already has a parent" errors
        icon_row_container = QHBoxLayout()

        if self.icons_row_type == IconType.ADSR:
            icon_hlayout = JDXi.UI.Icon.create_adsr_icons_row()
        elif self.icons_row_type == IconType.OSCILLATOR:
            icon_hlayout = JDXi.UI.Icon.create_oscillator_icons_row()
        elif self.icons_row_type == IconType.GENERIC:
            icon_hlayout = JDXi.UI.Icon.create_generic_musical_icon_row()
        else:
            return  # --- IconType.NONE or unknown

        # --- Transfer all items from icon_hlayout to icon_row_container

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
        """build ADSR widget"""
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
        # --- Default implementation - subclasses should override
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
        from jdxi_editor.midi.data.digital.oscillator import WaveForm

        # --- Handle both regular icons and generated waveform icons
        waveform_type_values = {
            WaveForm.ADSR,
            WaveForm.UPSAW,
            WaveForm.SQUARE,
            WaveForm.PWSQU,
            WaveForm.TRIANGLE,
            WaveForm.SINE,
            WaveForm.SAW,
            WaveForm.SPSAW,
            WaveForm.PCM,
            WaveForm.NOISE,
            WaveForm.LPF_FILTER,
            WaveForm.HPF_FILTER,
            WaveForm.BYPASS_FILTER,
            WaveForm.BPF_FILTER,
            WaveForm.FILTER_SINE,
        }

        # --- Find the tab widget (could be tab_widget or oscillator_tab_widget, etc.)
        tab_widget = None
        if hasattr(self, "tab_widget") and self.tab_widget is not None:
            tab_widget = self.tab_widget
        else:
            self.tab_widget = QTabWidget()
            tab_widget = self.tab_widget

        # --- Handle icon - could be a string (qtawesome icon name) or WaveformType value
        if isinstance(key.icon, str) and key.icon in waveform_type_values:
            # --- Use generated icon for waveform types
            icon = JDXi.UI.Icon.get_generated_icon(key.icon)
        elif isinstance(key.icon, str) and key.icon.startswith("mdi."):
            # --- Direct qtawesome icon name (e.g., "mdi.numeric-1-circle-outline")
            icon = JDXi.UI.Icon.get_icon(key.icon, color=JDXi.UI.Style.GREY)
        else:
            # --- Use regular icon from registry
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
        """build sliders"""
        return [
            self._create_parameter_slider(
                spec.param,
                spec.label,
                vertical=spec.vertical,
            )
            for spec in specs
        ]

    def _build_combo_boxes(self, specs: list["ComboBoxSpec"]):
        """build combo boxes"""
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
            if self.analog:
                JDXi.UI.Theme.apply_button_rect_analog(btn)
            else:
                btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)
        selected_btn = self.button_widgets.get(button_param)
        if selected_btn is None:
            return
        selected_btn.setChecked(True)
        if self.analog:
            JDXi.UI.Theme.apply_button_analog_active(selected_btn)
        else:
            selected_btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)
        self._update_button_enabled_states(button_param)
        if self.send_midi_parameter:
            # --- Map filter mode enums to their corresponding parameter
            if isinstance(button_param, DigitalFilterMode):
                # --- Filter mode buttons map to FILTER_MODE_SWITCH parameter
                actual_param = DigitalPartialParam.FILTER_MODE_SWITCH
                param_value = button_param.value
            elif isinstance(button_param, AnalogFilterMode):
                # --- Filter mode buttons map to FILTER_MODE_SWITCH parameter
                actual_param = AnalogParam.FILTER_MODE_SWITCH
                param_value = button_param.value
            else:
                # --- For other button types (like waveform), use the param directly
                actual_param = button_param
                param_value = getattr(button_param, "value", button_param)

            if actual_param is None:
                return
            # --- Ensure we have a valid AddressParameter before sending
            if not isinstance(actual_param, AddressParameter):
                from decologr import Decologr as log

                log.error(
                    f"Cannot send MIDI: {button_param} is not an AddressParameter (got {type(button_param)})"
                )
                return

            self.send_midi_parameter(actual_param, param_value)

    def _add_widget_rows(self, layout: QHBoxLayout | QVBoxLayout, rows: list[list[QWidget]]):
        """add a list of rows of widgets to a layout"""
        for row in rows:
            layout.addLayout(
                    create_layout_with_widgets(row)
                    )

    def _add_group_with_widget_rows(self, label: str, rows: list[list[QWidget]]):
        """Create a group box, populate it with rows of widgets, and add it to the parent layout."""
        group, group_layout = create_group_with_layout(label=label)
        self._add_widget_rows(group_layout, rows)
        group_layout.addStretch()
        layout = self.get_layout()
        layout.addWidget(group)
        JDXi.UI.Theme.apply_adsr_style(group, analog=self.analog)

    def _create_shape_row(self):
        """Shape and sync controls"""

        shape_label = QLabel("Shape")
        layout_widgets = [shape_label]

        self.wave_shape_group = QButtonGroup(self)
        self.wave_shape_group.setExclusive(True)

        for wave in self.wave_shapes:
            icon = create_icon_from_qta(wave.icon)

            btn = create_button_with_icon(
                icon_name=wave.shape.display_name,
                icon=icon,
                button_dimensions=JDXi.UI.Dimensions.WaveformIcon,
                icon_dimensions=JDXi.UI.Dimensions.LFOIcon,
            )

            btn.setCheckable(True)

            if self.analog:
                JDXi.UI.Theme.apply_button_rect_analog(btn)

            self.wave_shape_group.addButton(btn, wave.shape.value)
            self.wave_shape_buttons[wave.shape] = btn
            layout_widgets.append(btn)

        self.wave_shape_group.idToggled.connect(self._on_shape_group_changed)

        return create_layout_with_widgets(layout_widgets)

    def _apply_wave_shape_style(self, active_shape):
        for shape, btn in self.wave_shape_buttons.items():
            if shape == active_shape:
                if self.analog:
                    JDXi.UI.Theme.apply_button_analog_active(btn)
                else:
                    btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)
            else:
                if self.analog:
                    JDXi.UI.Theme.apply_button_rect_analog(btn)
                else:
                    btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)

    def _on_shape_group_changed(self, shape_value: int, checked: bool):
        log.message(
            "[LFO Shape] _on_shape_group_changed shape_value %s, checked: %s section: %s",
            shape_value, checked, self.__class__.__name__,
        )
        if not checked:
            return
        try:
            shape = self.SYNTH_SPEC.LFO.Shape(shape_value)
            self.set_wave_shape(shape, send_midi=True)
        except Exception as ex:
            log.error("[SectionBaseWidget] [_on_shape_group_changed] error %s occurred", ex)

    def set_wave_shape(self, shape, send_midi=False):
        """Update UI + optionally send MIDI"""

        btn = self.wave_shape_buttons.get(shape)
        if not btn:
            log.warning(
                "[LFO Shape] set_wave_shape: no button for shape %s (section=%s)",
                shape,
                self.__class__.__name__,
            )
            return

        # prevent recursive signals when updating from MIDI
        self.wave_shape_group.blockSignals(True)
        btn.setChecked(True)
        self.wave_shape_group.blockSignals(False)

        self._apply_wave_shape_style(shape)

        if send_midi and self.send_midi_parameter:
            address = getattr(self, "address", None)
            log.message(
                "[LFO Shape] sending MIDI param: %s value %s address %s section %s",getattr(self.wave_shape_param, "name", self.wave_shape_param),
                shape.value,
                address,
                self.__class__.__name__,
            )
            if not self.send_midi_parameter(
                self.wave_shape_param, shape.value, address
            ):
                log.warning(f"Failed to set Mod LFO shape to {shape.name}")
        elif send_midi and not self.send_midi_parameter:
            log.warning(
                "[LFO Shape] send_midi=True but send_midi_parameter is not set (section=%s)",
                self.__class__.__name__,
            )

    def _wrap_row(self, widgets: list[QWidget]) -> QWidget:
        """
        Convert a list of controls into a QWidget row container.

        Qt rule: layouts cannot be inserted where a QWidget is required
        (tabs, group boxes, pages). So we wrap the layout inside a QWidget.
        """
        row_widget = QWidget()
        row_layout = create_layout_with_widgets(widgets)
        row_widget.setLayout(row_layout)
        return row_widget