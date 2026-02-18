from PySide6.QtWidgets import QWidget

from jdxi_editor.ui.widgets.filter.filter import FilterWidget


class FilterWidgetFactory:
    def __init__(self):
        pass

    @staticmethod
    def create(
        spec, midi_helper, create_slider, create_switch, controls, address, analog
    ) -> QWidget:
        # spec is FilterWidgetSpec (cutoff_param, slope_param)
        return FilterWidget(
            cutoff_param=spec.cutoff_param,
            slope_param=spec.slope_param,
            midi_helper=midi_helper,
            create_parameter_slider=create_slider,
            create_parameter_switch=create_switch,
            controls=controls,
            address=address,
            analog=analog,
        )
