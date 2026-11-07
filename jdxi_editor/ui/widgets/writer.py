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
        """Show *display* on a slider (or any control with setValue) without emitting."""
        widget.blockSignals(True)
        widget.setValue(display)
        widget.blockSignals(False)

    @classmethod
    def set_combo(cls, widget, value):
        """Select *value* (one of the combo's values, else an index) without emitting."""
        cls.apply(widget, value, value)
