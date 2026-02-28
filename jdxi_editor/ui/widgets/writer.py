from __future__ import annotations


class WidgetWriter:

    @staticmethod
    def apply(widget, raw_value: int, display_value: int | float):

        if hasattr(widget, "setValue"):
            widget.blockSignals(True)
            widget.setValue(display_value)
            widget.blockSignals(False)
            return

        combo = getattr(widget, "combo_box", None)
        if combo:
            combo.blockSignals(True)
            values = getattr(widget, "values", None)

            if values and raw_value in values:
                combo.setCurrentIndex(values.index(raw_value))
            else:
                combo.setCurrentIndex(raw_value)

            combo.blockSignals(False)
            return

        raise TypeError(f"Unsupported widget type: {type(widget)}")

    @classmethod
    def set_slider(cls, widget, display):
        pass

    @classmethod
    def set_combo(cls, widget, value):
        pass
