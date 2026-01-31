"""
Digital Filter Section for the JDXI Editor
"""

from typing import Dict

from decologr import Decologr as log
from PySide6.QtWidgets import QGroupBox, QTabWidget, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.digital.filter import DigitalFilterType, DigitalFilterTypeEnum
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.ui.adsr.spec import ADSRSpec, ADSRStage
from jdxi_editor.ui.editors.base.filter import BaseFilterSection
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.filter.filter import FilterWidget
from jdxi_editor.ui.widgets.spec import SliderSpec, FilterSpec


class DigitalFilterSection(BaseFilterSection):
    """Digital Filter Section for JD-Xi Digital Partial"""

    # --- Filter sliders
    #     Note: FILTER_CUTOFF and FILTER_SLOPE are handled by FilterWidget (includes plot)
    PARAM_SPECS = [
        SliderSpec(
            Digital.Param.FILTER_RESONANCE, Digital.Display.Name.FILTER_RESONANCE
        ),
        SliderSpec(
            Digital.Param.FILTER_CUTOFF_KEYFOLLOW,
            Digital.Display.Name.FILTER_CUTOFF_KEYFOLLOW,
        ),
        SliderSpec(
            Digital.Param.FILTER_ENV_VELOCITY_SENSITIVITY,
            Digital.Display.Name.FILTER_ENV_VELOCITY_SENSITIVITY,
        ),
        SliderSpec(
            Digital.Param.FILTER_ENV_DEPTH, Digital.Display.Name.FILTER_ENV_DEPTH
        ),
    ]

    # --- Log PARAM_SPECS at class definition time
    _log_param_specs = True
    if _log_param_specs:
        filter_env_depth_spec = next(
            (
                s
                for s in PARAM_SPECS
                if hasattr(s.param, "name") and s.param.name == "FILTER_ENV_DEPTH"
            ),
            None,
        )
        if filter_env_depth_spec:
            log.message(
                f"🎯 DigitalFilterSection: FILTER_ENV_DEPTH found in PARAM_SPECS: {filter_env_depth_spec.param}, label: {filter_env_depth_spec.label}"
            )
        else:
            log.warning(
                f"⚠️ DigitalFilterSection: FILTER_ENV_DEPTH NOT found in PARAM_SPECS!"
            )
        log.message(f"📋 DigitalFilterSection PARAM_SPECS count: {len(PARAM_SPECS)}")
        log.message(
            f"📋 PARAM_SPECS params: {[getattr(s.param, 'name', str(s.param)) for s in PARAM_SPECS]}"
        )

    # --- Filter mode buttons
    BUTTON_SPECS = [
        SliderSpec(
            Digital.Filter.Mode.BYPASS,
            Digital.Filter.FilterType.BYPASS,
            icon_name=JDXi.UI.Icon.Wave.BYPASS_FILTER,
        ),
        SliderSpec(
            Digital.Filter.Mode.LPF,
            Digital.Filter.FilterType.LPF,
            icon_name=JDXi.UI.Icon.Wave.LPF_FILTER,
        ),
        SliderSpec(
            Digital.Filter.Mode.HPF,
            Digital.Filter.FilterType.HPF,
            icon_name=JDXi.UI.Icon.Wave.HPF_FILTER,
        ),
        SliderSpec(
            Digital.Filter.Mode.BPF,
            Digital.Filter.FilterType.BPF,
            icon_name=JDXi.UI.Icon.Wave.BPF_FILTER,
        ),
        SliderSpec(
            Digital.Filter.Mode.PKG,
            Digital.Filter.FilterType.PKG,
            icon_name=JDXi.UI.Icon.Wave.LPF_FILTER,
        ),
        SliderSpec(
            Digital.Filter.Mode.LPF2,
            Digital.Filter.FilterType.LPF2,
            icon_name=JDXi.UI.Icon.Wave.LPF_FILTER,
        ),
        SliderSpec(
            Digital.Filter.Mode.LPF3,
            Digital.Filter.FilterType.LPF3,
            icon_name=JDXi.UI.Icon.Wave.LPF_FILTER,
        ),
        SliderSpec(
            Digital.Filter.Mode.LPF4,
            Digital.Filter.FilterType.LPF4,
            icon_name=JDXi.UI.Icon.Wave.LPF_FILTER,
        ),
    ]

    BUTTON_ENABLE_RULES = {
        Digital.Filter.Mode.BYPASS: [],  # disables everything
        # --- Other modes: all sliders are enabled (default)
    }

    ADSR_SPEC: Dict[ADSRStage, ADSRSpec] = {
        ADSRStage.ATTACK: ADSRSpec(ADSRStage.ATTACK, Digital.Param.FILTER_ENV_ATTACK_TIME),
        ADSRStage.DECAY: ADSRSpec(ADSRStage.DECAY, Digital.Param.FILTER_ENV_DECAY_TIME),
        ADSRStage.SUSTAIN: ADSRSpec(ADSRStage.SUSTAIN, Digital.Param.FILTER_ENV_SUSTAIN_LEVEL),
        ADSRStage.RELEASE: ADSRSpec(ADSRStage.RELEASE, Digital.Param.FILTER_ENV_RELEASE_TIME),
        ADSRStage.PEAK: ADSRSpec(ADSRStage.PEAK, Digital.Param.FILTER_ENV_DEPTH),
    }

    FILTER_SPECS: Dict[DigitalFilterType, FilterSpec] = {
        DigitalFilterType.BYPASS: FilterSpec(
            param=None,
            icon=JDXi.UI.Icon.POWER,
            name=DigitalFilterTypeEnum.BYPASS.name,
            description=DigitalFilterTypeEnum.BYPASS.tooltip,
        ),
        DigitalFilterType.LPF: FilterSpec(
            param=Digital.Param.FILTER_MODE_SWITCH,
            icon=JDXi.UI.Icon.FILTER,
            name=DigitalFilterTypeEnum.LPF.name,
            description=DigitalFilterTypeEnum.LPF.tooltip,
        ),
        DigitalFilterType.HPF: FilterSpec(
            param=Digital.Param.FILTER_MODE_SWITCH,
            icon=JDXi.UI.Icon.FILTER,
            name=DigitalFilterTypeEnum.HPF.name,
            description=DigitalFilterTypeEnum.HPF.tooltip,
        ),
        DigitalFilterType.BPF: FilterSpec(
            param=Digital.Param.FILTER_MODE_SWITCH,
            icon=JDXi.UI.Icon.FILTER,
            name=DigitalFilterTypeEnum.BPF.name,
            description=DigitalFilterTypeEnum.BPF.tooltip,
        ),
        DigitalFilterType.PKG: FilterSpec(
            param=Digital.Param.FILTER_MODE_SWITCH,
            icon=JDXi.UI.Icon.FILTER,
            name=DigitalFilterTypeEnum.PKG.name,
            description=DigitalFilterTypeEnum.PKG.tooltip,
        ),
        DigitalFilterType.LPF2: FilterSpec(
            param=Digital.Param.FILTER_MODE_SWITCH,
            icon=JDXi.UI.Icon.FILTER,
            name=DigitalFilterTypeEnum.LPF2.name,
            description=DigitalFilterTypeEnum.LPF2.tooltip,
        ),
        DigitalFilterType.LPF3: FilterSpec(
            param=Digital.Param.FILTER_MODE_SWITCH,
            icon=JDXi.UI.Icon.FILTER,
            name=DigitalFilterTypeEnum.LPF3.name,
            description=DigitalFilterTypeEnum.LPF3.tooltip,
        ),
        DigitalFilterType.LPF4: FilterSpec(
            param=Digital.Param.FILTER_MODE_SWITCH,
            icon=JDXi.UI.Icon.FILTER,
            name=DigitalFilterTypeEnum.LPF4.name,
            description=DigitalFilterTypeEnum.LPF4.tooltip,
        ),
    }

    SYNTH_SPEC = Digital

    # --- Log ADSR_SPEC at class definition time
    if _log_param_specs:
        peak_spec = ADSR_SPEC.get(ADSRStage.PEAK)
        if peak_spec:
            peak_param = peak_spec.param if isinstance(peak_spec, ADSRSpec) else peak_spec
            peak_name = getattr(peak_param, "name", str(peak_param))
            log.message(
                f"🎯 DigitalFilterSection: ADSR_SPEC peak param: {peak_param} (name: {peak_name})"
            )
            if peak_name == "FILTER_ENV_DEPTH":
                log.message(f"✅ ADSR_SPEC peak is FILTER_ENV_DEPTH")
        else:
            log.warning(f"⚠️ DigitalFilterSection: No peak param in ADSR_SPEC!")
        log.message(f"📋 ADSR_SPEC keys: {list(ADSR_SPEC.keys())}")

    def __init__(self, *, icons_row_type: str = IconType.ADSR, **kwargs):
        """Initialize DigitalFilterSection with ADSR icon type"""
        super().__init__(icons_row_type=icons_row_type, **kwargs)

    def build_widgets(self):
        """Override to create FilterWidget with plot"""
        # --- Create FilterWidget first (includes cutoff and slope with plot)
        self.filter_widget = FilterWidget(
            cutoff_param=Digital.Param.FILTER_CUTOFF,
            slope_param=Digital.Param.FILTER_SLOPE,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            create_parameter_switch=self._create_parameter_switch,
            controls=self.controls,
            address=self.address,
        )
        # --- Store filter widget controls
        self.controls[Digital.Param.FILTER_CUTOFF] = (
            self.filter_widget.cutoff_param_control
        )
        if hasattr(self.filter_widget, "slope_param_control"):
            self.controls[Digital.Param.FILTER_SLOPE] = (
                self.filter_widget.slope_param_control
            )

        # --- Create parameter widgets (resonance, keyfollow, etc.) then run base build_widgets.
        # BaseFilterSection.build_widgets() calls _create_controls_group(); we override it so it
        # does not create AnalogFilterWidget (which would overwrite self.filter_widget).
        self._create_controls_widget()
        super().build_widgets()

    def _create_controls_group(self) -> QGroupBox:
        """Digital filter: do not create AnalogFilterWidget; populate control_widgets and filter-mode buttons for the tab."""
        self._create_parameter_widgets()
        if self.BUTTON_SPECS:
            self._create_waveform_buttons()
        return QGroupBox("Controls")

    def _create_tab_widget(self):
        """Override to add FilterWidget to Controls tab. Idempotent: skip if already built (called from both build_widgets and _setup_ui)."""
        if self.tab_widget is not None and self.tab_widget.count() > 0:
            return
        self.tab_widget = QTabWidget()
        self._add_tab(key=self.SYNTH_SPEC.Filter.Tab.CONTROLS, widget=self.controls_widget)

        # --- ADSR tab (adsr_group set by _create_adsr_group() in build_widgets)
        if getattr(self, "adsr_group", None):
            self._add_tab(key=self.SYNTH_SPEC.Filter.Tab.ADSR, widget=self.adsr_group)

    def _create_controls_widget(self):
        # --- Controls tab - include FilterWidget first, then other controls
        self.controls_widget = QWidget()
        # --- FilterWidget includes cutoff and slope with plot
        #     Other controls from PARAM_SPECS (resonance, keyfollow, velocity, depth)
        all_control_widgets = [self.filter_widget] + self.control_widgets
        self.controls_layout = create_layout_with_widgets(all_control_widgets)
        self.controls_widget.setLayout(self.controls_layout)

    def _create_adsr_group(self):
        """Create ADSR group (base creates adsr_widget and adsr_group)."""
        super()._create_adsr_group()

    def _on_button_selected(self, button_param):
        """Override to update filter mode in FilterWidget plot and enable/disable plot and ADSR"""
        # --- Call parent to handle button selection
        super()._on_button_selected(button_param)

        # --- Determine if bypass is selected
        is_bypass = button_param == Digital.Filter.Mode.BYPASS
        enabled = not is_bypass

        # --- Update filter mode in FilterWidget plot
        if (
            hasattr(self, "filter_widget")
            and self.filter_widget
            and hasattr(self.filter_widget, "plot")
        ):
            # Map Digital.Filter.Mode to filter mode string
            filter_mode_map = {
                Digital.Filter.Mode.BYPASS: Digital.Filter.ModeType.BYPASS,
                Digital.Filter.Mode.LPF: Digital.Filter.ModeType.LPF,
                Digital.Filter.Mode.HPF: Digital.Filter.ModeType.HPF,
                Digital.Filter.Mode.BPF: Digital.Filter.ModeType.BPF,
                Digital.Filter.Mode.PKG: Digital.Filter.ModeType.LPF,  # PKG uses LPF-style plot
                Digital.Filter.Mode.LPF2: Digital.Filter.ModeType.LPF,
                Digital.Filter.Mode.LPF3: Digital.Filter.ModeType.LPF,
                Digital.Filter.Mode.LPF4: Digital.Filter.ModeType.LPF,
            }
            filter_mode_str = filter_mode_map.get(
                button_param, Digital.Filter.ModeType.LPF
            )
            self.filter_widget.filter_mode = filter_mode_str
            if hasattr(self.filter_widget.plot, "set_filter_mode"):
                self.filter_widget.plot.set_filter_mode(filter_mode_str)

            # --- Disable plot display when bypass is selected
            self.filter_widget.plot.enabled = enabled
            self.filter_widget.plot.update()  # Trigger redraw

        # --- Enable/disable ADSR widget based on filter mode (like PWM widget)
        if self.adsr_widget:
            self.adsr_widget.setEnabled(enabled)

    def update_controls_state(self, value: int) -> None:
        """
        Update filter controls enabled state based on filter mode value.
        Called when filter mode changes from SysEx data.

        :param value: int - Filter mode value (0=BYPASS, 1=LPF, 2=HPF, etc.)
        :return: None
        """

        filter_mode_map = {
            0: Digital.Filter.Mode.BYPASS,
            1: Digital.Filter.Mode.LPF,
            2: Digital.Filter.Mode.HPF,
            3: Digital.Filter.Mode.BPF,
            4: Digital.Filter.Mode.PKG,
            5: Digital.Filter.Mode.LPF2,
            6: Digital.Filter.Mode.LPF3,
            7: Digital.Filter.Mode.LPF4,
        }

        selected_filter_mode = filter_mode_map.get(value)
        if selected_filter_mode is None:
            log.warning(f"Unknown filter mode value: {value}")
            return

        # --- Enable/disable controls based on filter mode
        is_bypass = selected_filter_mode == Digital.Filter.Mode.BYPASS
        enabled = not is_bypass

        # --- Enable/disable filter controls
        filter_params = [
            Digital.Param.FILTER_CUTOFF,
            Digital.Param.FILTER_SLOPE,
            Digital.Param.FILTER_RESONANCE,
            Digital.Param.FILTER_CUTOFF_KEYFOLLOW,
            Digital.Param.FILTER_ENV_VELOCITY_SENSITIVITY,
            Digital.Param.FILTER_ENV_DEPTH,
        ]
        # --- TODO: This section seems to disable the filter section, never to be used again
        """for param in filter_params:
            if param in self.controls:
                self.controls[param].setEnabled(enabled)
        
        # --- Enable/disable filter widget and ADSR
        if hasattr(self, 'filter_widget') and self.filter_widget:
            if hasattr(self.filter_widget, 'cutoff_param_control'):
                self.filter_widget.cutoff_param_control.setEnabled(enabled)
            if hasattr(self.filter_widget, 'slope_param_control'):
                self.filter_widget.slope_param_control.setEnabled(enabled)
            if hasattr(self.filter_widget, 'plot'):
                self.filter_widget.plot.enabled = enabled
                self.filter_widget.plot.update()
        """

        if self.adsr_widget:
            self.adsr_widget.setEnabled(enabled)

        # --- Update filter mode in FilterWidget plot
        if (
            hasattr(self, "filter_widget")
            and self.filter_widget
            and hasattr(self.filter_widget, "plot")
        ):
            filter_mode_str_map = {
                Digital.Filter.Mode.BYPASS: Digital.Filter.ModeType.BYPASS,
                Digital.Filter.Mode.LPF: Digital.Filter.ModeType.LPF,
                Digital.Filter.Mode.HPF: Digital.Filter.ModeType.HPF,
                Digital.Filter.Mode.BPF: Digital.Filter.ModeType.BPF,
                Digital.Filter.Mode.PKG: Digital.Filter.ModeType.BYPASS,
                Digital.Filter.Mode.LPF2: Digital.Filter.ModeType.BYPASS,
                Digital.Filter.Mode.LPF3: Digital.Filter.ModeType.BYPASS,
                Digital.Filter.Mode.LPF4: Digital.Filter.ModeType.BYPASS,
            }
            filter_mode_str = filter_mode_str_map.get(
                selected_filter_mode, Digital.Filter.ModeType.BYPASS
            )
            self.filter_widget.filter_mode = filter_mode_str
            if hasattr(self.filter_widget.plot, "set_filter_mode"):
                self.filter_widget.plot.set_filter_mode(filter_mode_str)
