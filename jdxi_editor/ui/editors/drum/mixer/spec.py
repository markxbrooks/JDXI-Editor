from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class DrumLane:
    name: str
    partials: list[str]
    colspan: int = 1


@dataclass(frozen=True)
class DrumLaneRow:
    title: str
    lanes: list[DrumLane]

    # iteration: for lane in row
    def __iter__(self) -> Iterator["DrumLane"]:
        return iter(self.lanes)

    # len(row)
    def __len__(self) -> int:
        return len(self.lanes)

    # row[index]
    def __getitem__(self, index: int) -> "DrumLane":
        return self.lanes[index]


DRUM_MIXER_LANE_ROWS: list[DrumLaneRow] = [
    DrumLaneRow(
        title="Low End",
        lanes=[
            DrumLane(name="Kick", partials=["BD1", "BD2", "BD3"]),
            DrumLane(name="Toms", partials=["TOM1", "TOM2", "TOM3"]),
        ],
    ),
    DrumLaneRow(
        title="Snares",
        lanes=[
            DrumLane(
                name="Snare",
                partials=["SD1", "SD2", "SD3", "SD4", "RIM", "CLAP"],
                colspan=2,
            ),
        ],
    ),
    DrumLaneRow(
        title="Backbeat",
        lanes=[
            DrumLane(name="Hi-Hat", partials=["CHH", "PHH", "OHH"]),
            DrumLane(name="Cymbals", partials=["CYM1", "CYM2", "CYM3"]),
        ],
    ),
    DrumLaneRow(
        title="Time",
        lanes=[
            DrumLane(
                name="Percussion", partials=["PRC1", "PRC2", "PRC3", "PRC4", "PRC5"]
            ),
            DrumLane(name="Other", partials=["HIT", "OTH1", "OTH2"]),
        ],
    ),
    DrumLaneRow(
        title="Notes",
        lanes=[
            DrumLane(
                name="Chromatic",
                partials=[
                    "D4",
                    "Eb4",
                    "E4",
                    "F4",
                    "F#4",
                    "G4",
                    "G#4",
                    "A4",
                    "Bb4",
                    "B4",
                    "C5",
                    "C#5",
                ],
                colspan=2,
            ),
        ],
    ),
]
