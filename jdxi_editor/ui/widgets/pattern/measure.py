"""
Pattern Measure
"""

from jdxi_editor.ui.editors.pattern.step.data import StepData


class PatternMeasure:
    def __init__(self, rows: int, steps_per_bar: int):
        self.steps: list[list[StepData]] = [
            [StepData() for _ in range(steps_per_bar)] for _ in range(rows)
        ]
