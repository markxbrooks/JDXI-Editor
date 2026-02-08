from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class DispatchStats:
    applied: List[str]
    skipped: List[str]
    failed: List[str]

    def record_applied(self, name: str):
        self.applied.append(name)

    def record_skipped(self, name: str):
        self.skipped.append(name)

    def record_failed(self, name: str):
        self.failed.append(name)

    @property
    def attempted(self) -> int:
        return len(self.applied) + len(self.failed)

    @property
    def coverage(self) -> float:
        total = self.attempted + len(self.skipped)
        return (self.attempted / total) if total else 0.0

    @property
    def success_rate(self) -> float:
        return (len(self.applied) / self.attempted) if self.attempted else 0.0
