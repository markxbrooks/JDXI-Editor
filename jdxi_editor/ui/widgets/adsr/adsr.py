"""
ADSR Widget for Roland JD-Xi

This widget provides address visual interface for editing ADSR (Attack, Decay, Sustain, Release)
envelope parameters. It includes:
- Interactive sliders for each ADSR parameter
- Visual envelope plot
- Real-time parameter updates
- MIDI parameter integration via SynthParameter objects

The widget supports both analog and digital synth parameters and provides visual feedback
through an animated envelope curve.
"""

from typing import Dict, Optional, Callable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QGridLayout

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.sysex.composer import JDXiSysExComposer
from jdxi_editor.ui.widgets.adsr.plot import ADSRPlot
from jdxi_editor.ui.widgets.envelope.base import EnvelopeWidgetBase, TOOLTIPS
from jdxi_editor.ui.widgets.slider_spinbox.slider_spinbox import AdsrSliderSpinbox


class ADSR(EnvelopeWidgetBase):
    """ ADSR Widget for Roland JD-Xi """
    envelope_changed = Signal(dict)

    def __init__(
            self,
            attack_param: AddressParameter,
            decay_param: AddressParameter,
            sustain_param: AddressParameter,
            release_param: AddressParameter,
            initial_param: Optional[AddressParameter] = None,
            peak_param: Optional[AddressParameter] = None,
            create_parameter_slider: Callable = None,
            midi_helper: Optional[MidiIOHelper] = None,
            address: Optional[RolandSysExAddress] = None,
            controls: Dict[AddressParameter, QWidget] = None,
            parent: Optional[QWidget] = None,
    ):
        super().__init__(envelope_keys=["attack_time", "decay_time", "sustain_level", "release_time"],
                         create_parameter_slider=create_parameter_slider,
                         parameters=[attack_param, decay_param, sustain_param, release_param],
                         midi_helper=midi_helper,
                         address=address,
                         controls=controls,
                         parent=parent)
        self.sysex_composer = JDXiSysExComposer()
        """
        Initialize the ADSR widget
        :param attack_param: AddressParameter
        :param decay_param: AddressParameter
        :param sustain_param: AddressParameter
        :param release_param: AddressParameter
        :param initial_param: Optional[AddressParameter]
        :param peak_param: Optional[AddressParameter]
        :param midi_helper: Optional[MidiIOHelper]
        :param address: Optional[RolandSysExAddress]
        :param parent: Optional[QWidget]
        """
        self.address = address
        self.midi_helper = midi_helper
        if controls:
            self.controls = controls
        else:
            self.controls = {}
        self._create_parameter_slider = create_parameter_slider
        self.envelope = {
            "attack_time": 300.0,
            "decay_time": 800.0,
            "release_time": 500.0,
            "initial_level": 0.0,
            "peak_level": 1.0,
            "sustain_level": 0.8,
        }
        self.attack_control = AdsrSliderSpinbox(
            attack_param,
            min_value=0,
            max_value=1000,
            units=" ms",
            label="Attack",
            value=self.envelope["attack_time"],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.decay_control = AdsrSliderSpinbox(
            decay_param,
            min_value=0,
            max_value=1000,
            units=" ms",
            label="Decay",
            value=self.envelope["decay_time"],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.sustain_control = AdsrSliderSpinbox(
            sustain_param,
            min_value=0.0,
            max_value=1.0,
            units="",
            label="Sustain",
            value=self.envelope["sustain_level"],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.release_control = AdsrSliderSpinbox(
            release_param,
            min_value=0,
            max_value=1000,
            units=" ms",
            label="Release",
            value=self.envelope["release_time"],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self._control_widgets = [
            self.attack_control,
            self.decay_control,
            self.sustain_control,
            self.release_control,
        ]
        self.controls[attack_param] = self.attack_control
        self.controls[decay_param] = self.decay_control
        self.controls[sustain_param] = self.sustain_control
        self.controls[release_param] = self.release_control
        if peak_param:
            self.peak_control = AdsrSliderSpinbox(
                peak_param,
                min_value=0,
                max_value=1.0,
                units="",
                label="Depth",
                value=self.envelope["peak_level"],
                create_parameter_slider=self._create_parameter_slider,
                parent=self,
            )
            self._control_widgets.append(self.peak_control)

        for key, widget in [("attack_time", self.attack_control),
                            ("decay_time", self.decay_control),
                            ("sustain_level", self.sustain_control),
                            ("release_time", self.release_control),]:
            if tooltip := TOOLTIPS.get(key):
                widget.setToolTip(tooltip)
        self.attack_parameter = attack_param
        self.decay_parameter = decay_param
        self.sustain_parameter = sustain_param
        self.release_parameter = release_param
        self._control_parameters = [
            self.attack_parameter,
            self.decay_parameter,
            self.sustain_parameter,
            self.release_parameter,
        ]
        if peak_param:
            self._control_parameters.append(peak_param)
        self.layout = QGridLayout()
        self.layout.addWidget(self.attack_control, 0, 0)
        self.layout.addWidget(self.decay_control, 0, 1)
        self.layout.addWidget(self.sustain_control, 0, 2)
        self.layout.addWidget(self.release_control, 0, 3)
        self.setLayout(self.layout)

        self.envelope_spinbox_map = {
            "attack_time": self.attack_control.spinbox,
            "decay_time": self.decay_control.spinbox,
            "sustain_level": self.sustain_control.spinbox,
            "release_time": self.release_control.spinbox,
        }
        # Create layout
        self.plot = ADSRPlot(width=JDXiStyle.ADSR_PLOT_WIDTH,
                             height=JDXiStyle.ADSR_PLOT_HEIGHT,
                             envelope=self.envelope,
                             parent=self)
        if hasattr(self, 'peak_control'):
            self.layout.addWidget(self.peak_control, 0, 4)
            self.envelope_spinbox_map["peak_level"] = self.peak_control.spinbox
            self.layout.addWidget(self.plot, 0, 5, 3, 1)
        else:
            self.layout.addWidget(self.plot, 0, 4, 3, 1)
        self.plot.set_values(self.envelope)
        for control in self._control_widgets:
            control.envelope_changed.connect(self.on_control_changed)
        self.update_controls_from_envelope()

    def on_control_changed(self, change: dict):
        self.envelope.update(change)
        self.plot.set_values(self.envelope)
        self.envelope_changed.emit(self.envelope)

    def update_envelope_from_spinboxes(self):
        """Update envelope values from spin boxes"""
        self.envelope["attack_time"] = self.attack_control.value()
        self.envelope["decay_time"] = self.decay_control.value()
        self.envelope["sustain_level"] = self.sustain_control.value()
        self.envelope["release_time"] = self.release_control.value()
        self.plot.set_values(self.envelope)
        self.envelope_changed.emit(self.envelope)

    def update_spinboxes_from_envelope(self):
        """Update spinboxes from envelope values"""
        self.attack_control.setValue(self.envelope["attack_time"])
        self.decay_control.setValue(self.envelope["decay_time"])
        self.sustain_control.setValue(self.envelope["sustain_level"])
        self.release_control.setValue(self.envelope["release_time"])
        self.plot.set_values(self.envelope)
        self.envelope_changed.emit(self.envelope)
