from dataclasses import dataclass


class TrackCategory:
    BASS = "bass"
    KEYS_GUITARS = "keys_guitars"
    STRINGS = "strings"
    # DRUMS = "drums"
    UNCLASSIFIED = "unclassified"


STR_TO_TRACK_CATEGORY: dict[str, str] = {
    TrackCategory.BASS: TrackCategory.BASS,
    TrackCategory.KEYS_GUITARS: TrackCategory.KEYS_GUITARS,
    TrackCategory.STRINGS: TrackCategory.STRINGS,
    # TrackCategory.DRUMS: TrackCategory.DRUMS,
    TrackCategory.UNCLASSIFIED: TrackCategory.UNCLASSIFIED,
}
CHANNEL_BY_CATEGORY: dict[str, int] = {
    TrackCategory.BASS: 1,
    TrackCategory.KEYS_GUITARS: 2,
    TrackCategory.STRINGS: 3,
}


@dataclass(frozen=True)
class CategoryMeta:
    """Category Meta Information"""

    emoji: str
    label: str
    channel: int
    engine: str


CATEGORY_META: dict[str, CategoryMeta] = {
    TrackCategory.BASS: CategoryMeta(
        emoji="🎸", label="Bass", channel=1, engine="Digital Synth 1"
    ),
    TrackCategory.KEYS_GUITARS: CategoryMeta(
        emoji="🎹", label="Keys/Guitars", channel=2, engine="Digital Synth 2"
    ),
    TrackCategory.STRINGS: CategoryMeta(
        emoji="🎻", label="Strings", channel=3, engine="Analog Synth"
    ),
    # TrackCategory.DRUMS: CategoryMeta(emoji="🥁", label="Drums", channel=10, name="Drums")
}
