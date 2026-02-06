from typing import Callable, Optional

from PySide6.QtWidgets import QTabWidget, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import create_layout_with_widgets
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget


class BaseAmpSection(SectionBaseWidget):
    """Base Amp Section"""

    def __init__(
        self,
        # controls: dict,
        analog: bool = False,
        parent: Optional[QWidget] = None,
        send_midi_parameter: Callable = None,
        midi_helper: MidiIOHelper = None,
        controls: dict = None,
        address: RolandSysExAddress = None,
    ):

        # Dynamic widgets storage
        self.amp_sliders = {}
        self.tab_widget = None
        self.layout = None

        super().__init__(
            icons_row_type=IconType.ADSR,
            analog=analog,
            midi_helper=midi_helper,
            send_midi_parameter=send_midi_parameter,
            controls=controls,
            address=address,
        )

    # ------------------------------------------------------------------
    # Build Widgets
    # ------------------------------------------------------------------
    def build_widgets(self):
        """Build all amp widgets"""
        self.tab_widget = QTabWidget()
        JDXi.UI.Theme.apply_tabs_style(self.tab_widget, analog=self.analog)
        sliders = self._build_sliders(self.PARAM_SPECS)
        for entry, slider in zip(self.PARAM_SPECS, sliders):
            self.amp_sliders[entry.param] = slider
            self.controls[entry.param] = slider
        self._create_adsr_group()

    # ------------------------------------------------------------------
    # Setup UI
    # ------------------------------------------------------------------
    def setup_ui(self):
        """Setup the UI for the analog amp section"""
        self.layout = self.create_layout()

        # --- Level Controls Tab
        self.controls_layout = create_layout_with_widgets(
            list(self.amp_sliders.values())
        )
        self.level_controls_widget = QWidget()
        self.level_controls_widget.setLayout(self.controls_layout)

        self._add_tab(
            key=self.SYNTH_SPEC.Amp.Tab.CONTROLS, widget=self.level_controls_widget
        )

        # --- ADSR Tab
        self._add_tab(key=self.SYNTH_SPEC.Amp.Tab.ADSR, widget=self.adsr_group)

        # --- Add tab widget to main layout
        self.layout.addWidget(self.tab_widget)
        self.layout.addStretch()
