"""
Pattern Measure
"""
import random
from jdxi_editor.ui.editors.pattern.step.data import StepData


class PatternMeasure:
    """Pattern Measure class"""

    def __init__(self, rows: int, steps_per_bar: int):
        self.rows = rows
        self.steps_per_bar = steps_per_bar
        self.steps: list[list[StepData]] = [
            [StepData() for _ in range(steps_per_bar)] for _ in range(rows)
        ]

    def _apply_region(self, func, rows=None, steps=None):
        """Apply func(row, step, StepData) to a region."""
        rows = rows if rows is not None else range(self.rows)
        steps = steps if steps is not None else range(self.steps_per_bar)

        for r in rows:
            for s in steps:
                func(r, s, self.steps[r][s])

    def clear(self):
        """clear the measure"""
        self._apply_region(lambda r, s, step: setattr(step, "active", False))

    def scale_velocity(self, factor: float):
        """scale velocity"""
        def op(r, s, step):
            if step.active:
                step.velocity = max(1, min(127, int(step.velocity * factor)))

        self._apply_region(op)

    def shift_steps(self, amount: int):
        """Rotate steps in each row."""
        for row in self.steps:
            amount_mod = amount % self.steps_per_bar
            row[:] = row[-amount_mod:] + row[:-amount_mod]

    def copy_steps(self, src_start: int, length: int, dest_start: int):
        """copy steps"""
        for row in self.steps:
            block = row[src_start:src_start + length]
            for i, step in enumerate(block):
                row[(dest_start + i) % self.steps_per_bar] = StepData(
                    active=step.active,
                    note=step.note,
                    velocity=step.velocity,
                    duration_steps=step.duration_steps,
                )

    def invert(self):
        """invert a region"""
        self._apply_region(lambda r, s, step: setattr(step, "active", not step.active))

    def humanize_velocity(self, amount: int = 10):
        """'humanize' velocity with random quirks"""
        def op(r, s, step):
            if step.active:
                delta = random.randint(-amount, amount)
                step.velocity = max(1, min(127, step.velocity + delta))

        self._apply_region(op)
