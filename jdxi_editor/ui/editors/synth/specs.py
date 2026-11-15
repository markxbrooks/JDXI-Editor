import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, Optional


@dataclass(frozen=True)
class InstrumentDescriptor:
    """
    Canonical description of a JD-Xi instrument preset.
    """

    category: str  # "synth" | "drum"
    family: Optional[str]  # e.g. "piano", "pad", "bass"; None if unrecognized
    engine: Optional[str]  # e.g. "fm", "jd"
    raw_text: str  # original label (for logging/debug)


@dataclass(frozen=True)
class InstrumentFamilySpec:
    family: str
    keywords: Iterable[str]


@dataclass(frozen=True)
class DrumKitSpec:
    engine: str
    keywords: tuple[str, ...]
    family: str = "kit"


def preset_match_text(text: str) -> str:
    """
    Normalize preset labels for keyword matching.

    Strips a leading program index (e.g. ``001 - Power 3`` → ``power 3``,
    ``101: MKS-50 Bass1`` → ``mks-50 bass1``). The index has to go, otherwise it
    is matched as a model number: ``101`` would detect an SH-101 and ``202`` an
    MC-202.
    """
    text = text.strip()
    for separator in (" - ", ":"):
        if separator in text:
            head, _, tail = text.partition(separator)
            if head.strip().isdigit():
                return tail.strip().lower()
    return text.lower()


DRUM_KIT_SPECS = [
    DrumKitSpec(
        engine="tr",
        keywords=("tr-909", "909"),
    ),
    DrumKitSpec(
        engine="tr",
        keywords=("tr-808", "808"),
    ),
    DrumKitSpec(
        engine="tr",
        keywords=("tr-707", "707"),
    ),
    DrumKitSpec(
        engine="cr",
        keywords=("cr-78", "cr78"),
    ),
    DrumKitSpec(
        engine="tr",
        keywords=("tr-606", "606"),
    ),
    DrumKitSpec(
        engine="tr",
        keywords=("tr-626", "626"),
    ),
    DrumKitSpec(
        engine="tr",
        keywords=("power kit", "power kick"),
    ),
]
INSTRUMENT_FAMILY_SPECS = [
    # Piano/Keyboard - highest priority for keyboard category
    InstrumentFamilySpec(
        "piano",
        [
            "piano",
            "e. piano",
            "e.p",
            "ep",
            "e.piano",
            "grand",
            "wurly",
            "clav",
            "vibraphone",
            "harp",
            "steel drum",
            "trem ep",
        ],
    ),
    InstrumentFamilySpec(
        "jupiter",
        [
            "jp8",
            "jupiter",
            "jupiter8",
        ],
    ),
    # Pad - pad-specific terms (check before strings to prioritize pad when "pad" is in name)
    InstrumentFamilySpec(
        "pad",
        [
            "hollow pad",
            "lfo pad",
            "sweep pad",
            "boreal pad",
            "bright pad",
            "soft pad",
            "hpf pad",
            "organ pad",
            "bell pad",
            "vox pad",
            "s-saw pad",
            "hpf sweep",
            "fltsweep pd",
            "koff pad",
            "trnssweeppad",
            "lfo carvepd",
            "lfo resopad",
            "pls pad",
            "reso s&h pd",
            "sidechainpd",
            "pxzoon",
            "psychoscilo",
            "fantasy",
            "dreaming",
            "syn sniper",
            "pad",  # "pad" at end as fallback
        ],
    ),
    # Strings - specific string terms (after pad to avoid conflicts)
    InstrumentFamilySpec(
        "strings",
        [
            "jp8 strings",
            "strings",
            "string",
            "str",
            "juno str",
            "brite str",
            "oct strings",
            "hybrid str",
            "analog str",
            "d-50 pizz",
            "d-50 stack",
        ],
    ),
    InstrumentFamilySpec(
        "bass guitar",
        [
            "bass guitar",
            "bassgtr",
            "bassgtr1",
            "bassgtr2",
            "bassgtr3",
            "bassgtr4",
            "bassgtr5",
            "bassgtr6",
            "bassgtr7",
            "bassgtr8",
            "bassgtr9",
            "bassgtr10",
            "fretless bass",
            "picked bass",
            "fingerd bs",
        ],
    ),
    # Bass
    InstrumentFamilySpec(
        "bass",
        [
            "bass",
            "bs",
            "bass1",
            "bass2",
            "bass3",
            "bass4",
            "bass5",
            "seq bass",
            "reso bass",
            "tb bass",
            "106 bass",
            "low bass",
            "kick bass",
            "organ bass",
            "growl bass",
            "talking bs",
            "lfo bass",
            "crack bass",
            "wobble bs",
            "sidechainbs",
            "house bass",
            "fm bass",
            "ac. bass",
            "fingerd bs",
            "picked bass",
            "fretless bs",
            "slap bass",
            "r&b bass",
            "wide bass",
            "chow bass",
            "sqrfilterbs",
            "filter bass",
            "seqfltenvbs",
            "dnb bass",
            "unisonsynbs",
            "modular bs",
            "monster bs",
            "square bs",
            "5th stac bs",
            "sqrstacsynbs",
            "mc-202 bs",
            "sh-101 bs",
            "mg bass",
            "tri bass",
            "bpf syn bs",
            "sindetunebs",
            "resrubber bs",
            "resosawsynbs",
            "syn bass",
            "filterenvbs",
            "juno sqr bs",
            "detune bs",
            "mks-50 bass",
            "sweep bass",
            "4op fm bass",
        ],
    ),
    # Lead
    InstrumentFamilySpec(
        "lead",
        [
            "lead",
            "ld",
            "ld1",
            "ld2",
            "ld3",
            "ld4",
            "tekno lead",
            "osc-syncld",
            "waveshapeld",
            "buzz lead",
            "sawbuzz ld",
            "sqr buzz ld",
            "dist flt tb",
            "dist tb sqr",
            "glideator",
            "vintager",
            "hover lead",
            "saw lead",
            "saw+tri lead",
            "portasaw ld",
            "reso saw ld",
            "sawtrap ld",
            "fat gr lead",
            "pulstar ld",
            "slow lead",
            "anavox lead",
            "square ld",
            "sqr lead",
            "sqr trap ld",
            "sine lead",
            "tri lead",
            "tri stac ld",
            "5th sawlead",
            "sweet 5th",
            "4th syn lead",
            "maj stack ld",
            "minstack ld",
            "chubby lead",
            "cuttinglead",
            "s-sawstacld",
            "bend lead",
            "power",
            "power 1",
            "power 2",
            "power 3",
            "power 4",
            "power 5",
        ],
    ),
    # Brass
    InstrumentFamilySpec(
        "brass",
        [
            "brass",
            "brs",
            "analog brass",
            "reso brass",
            "soft brass",
            "fm brass",
            "syn brass",
            "jp8 brass",
            "soft synbrs",
            "epicslow brs",
            "juno brass",
            "poly brass",
        ],
    ),
    # Organ
    InstrumentFamilySpec(
        "organ",
        [
            "organ",
            "org",
            "house org",
            "70's e.organ",
            "e.organ",
            "organ bell",
            "organ bass",
            "organ pad",
        ],
    ),
    # Guitar
    InstrumentFamilySpec(
        "guitar",
        [
            "guitar",
            "gtr",
            "strat",
            "ac. guitar",
            "bright strat",
            "funk guitar",
            "jazz guitar",
            "dist guitar",
            "d. mute gtr",
            "e. sitar",
            "sitar drone",
            "sitar",
        ],
    ),
    # FX/Other - Voc, FX, Hits, etc.
    InstrumentFamilySpec(
        "synth",
        [
            "fx",
            "voc",
            "hit",
            "vox",
            "vp-330",
            "voc:",
            "voc:ensemble",
            "voc:5thstack",
            "voc:robot",
            "voc:saw",
            "voc:sqr",
            "voc:rise up",
            "voc:auto vib",
            "voc:pitchenv",
            "voc:vp-330",
            "voc:noise",
            "orch hit",
            "philly hit",
            "house hit",
            "o'skool hit",
            "punch hit",
            "tao hit",
            "syn vox",
            "jd softvox",
            "vox pad",
            "vp-330 chr",
            "tuned winds",
            "bend lead",
            "riser",
            "rising seq",
            "scream saw",
            "noise seq",
            "init tone",
        ],
    ),
    # Seq/Sequence - plucks, sequences
    InstrumentFamilySpec(
        "synth",
        [
            "seq",
            "pluck",
            "plk",
            "seq saw",
            "seq sqr",
            "seq tri",
            "sqr reso plk",
            "pluck synth",
            "paperclip",
            "sonar pluck",
            "sqrtrapplk",
            "tb saw seq",
            "tb sqr seq",
            "juno key",
            "analog poly",
            "juno octavr",
            "edm synth",
            "super saw",
            "s-saw poly",
            "trance key",
            "s-sawstc syn",
            "7th stac syn",
        ],
    ),
    # General synth/saw
    InstrumentFamilySpec(
        "synth",
        [
            "synth",
            "saw",
            "super saw",
            "s-saw",
            "sawstac",
            "sawstc",
            "sawpoly",
            "saw trap",
            "saw buzz",
            "saw lead",
            "saw seq",
            "sawsynbs",
            "sawsyn",
            "sawpad",
        ],
    ),
]


@dataclass
class EngineKeywordSpec:
    engine: str
    keywords: Iterable[str]


ENGINE_KEYWORDS = {
    "jupiter": ["jupiter", "jp8", "jupiter8"],
    "fm": ["fm", "4op fm"],
    "juno": ["juno", "jn"],
    "jd": ["jd"],
    "tb": ["tb", "tb-303", "303"],
    "mg": ["mg", "minimoog"],
    "sh": ["sh", "sh-101", "101"],
    "d-50": ["d-50", "d50"],
    "vp-330": ["vp-330", "vp330"],
    "mks": ["mks", "mks-50"],
    "mc": ["mc", "mc-202", "202"],
}


# ---------------------------------------------------------------------------
# Image basename aliases
# ---------------------------------------------------------------------------
# The detected engine name (see ENGINE_KEYWORDS) is used to look up an icon
# named "<engine>.png". The shipped artwork is not named consistently across
# the resource folders (e.g. ``digital_synths/tb-303.png`` vs
# ``analog_synths/tb303.png``), so each engine maps to every basename that may
# carry its artwork, in order of preference.
ENGINE_IMAGE_ALIASES: dict[str, tuple[str, ...]] = {
    "jupiter": ("jupiter", "jp8", "jp-8", "jupiter8"),
    "jp8": ("jp8", "jp-8", "jupiter8", "jupiter"),
    "juno": ("juno",),
    "jd": ("jd",),
    "fm": ("fm",),
    "tb": ("tb", "tb-303", "tb303"),
    "mg": ("mg", "minimoog"),
    "sh": ("sh", "sh-101", "sh101"),
    "d-50": ("d-50", "d50"),
    "vp-330": ("vp-330", "vp330"),
    "mks": ("mks", "mks-50", "mks50"),
    "mc": ("mc", "mc-202", "mc202"),
}


def engine_image_basenames(name: str) -> tuple[str, ...]:
    """
    Expand an engine/instrument name into the image basenames to try, in order.

    :param name: Detected engine or instrument name (e.g. ``"tb"``).
    :return: Candidate basenames without extension, most specific first.
    """
    if not name:
        return ()
    key = str(name).strip().lower()
    if not key:
        return ()
    aliases = ENGINE_IMAGE_ALIASES.get(key)
    if not aliases:
        return (key,)
    if key in aliases:
        return aliases
    return (key, *aliases)


# ---------------------------------------------------------------------------
# Keyword matching
# ---------------------------------------------------------------------------
# Most keywords are matched as substrings on purpose: the JD-Xi truncates tone
# names, so "S-SawStacLd1" has to be matched by "sawstac". Short keywords
# cannot afford that -- "ep" would match "Sweep Pad 1" and "sh" would match
# "WaveShapeLd1" -- so anything this short or shorter is matched on letter
# boundaries instead. Digits may still sit next to it, so "tb" keeps matching
# "Dist Flt TB1" and "101" keeps matching "SH-101 Bs".
SHORT_KEYWORD_LENGTH = 3


@lru_cache(maxsize=512)
def _short_keyword_pattern(keyword: str) -> re.Pattern:
    return re.compile(rf"(?<![a-z]){re.escape(keyword)}(?![a-z])")


_CAMEL_SPLIT = (
    re.compile(r"(?<=[a-z])(?=[A-Z])"),  # ResoPulseBs -> Reso Pulse Bs
    re.compile(r"(?<=[A-Za-z])(?=\d)"),  # Bs1 -> Bs 1
)


def preset_match_texts(text: str) -> tuple[str, ...]:
    """
    Normalized forms of a preset label to match keywords against.

    The JD-Xi runs tone names together to fit its display, and the two forms
    pull in opposite directions: ``"S-SawStacLd1"`` needs the glued form for
    the keyword ``sawstac``, while ``"ResoPulseBs1"`` needs the split form for
    the keyword ``bs``. Both are returned, so a keyword matching either counts.

    :param text: Preset label, with or without its index.
    :return: The normalized label, plus its camel-case-split form when that
        differs.
    """
    plain = preset_match_text(text)
    split = text
    for pattern in _CAMEL_SPLIT:
        split = pattern.sub(" ", split)
    split = preset_match_text(split)
    return (plain,) if split == plain else (plain, split)


def keyword_in(texts, keyword: str) -> bool:
    """
    Test whether *keyword* occurs in any of the normalized *texts*.

    Keywords longer than :data:`SHORT_KEYWORD_LENGTH` match as substrings;
    shorter ones have to sit on a letter boundary.

    :param texts: Normalized preset text, or several forms of it (see
        :func:`preset_match_texts`).
    :param keyword: Keyword to look for, lower case.
    :return: True when the keyword matches.
    """
    if isinstance(texts, str):
        texts = (texts,)
    keyword = keyword.lower()
    if len(keyword) > SHORT_KEYWORD_LENGTH:
        return any(keyword in text for text in texts)
    pattern = _short_keyword_pattern(keyword)
    return any(pattern.search(text) for text in texts)


def any_keyword_in(texts, keywords: Iterable[str]) -> bool:
    """
    Test whether any of *keywords* occurs in *texts*.

    :param texts: Normalized preset text, or several forms of it.
    :param keywords: Keywords to look for.
    :return: True when at least one keyword matches.
    """
    return any(keyword_in(texts, keyword) for keyword in keywords)


# ---------------------------------------------------------------------------
# Preset-specific artwork
# ---------------------------------------------------------------------------
_TRAILING_INDEX = re.compile(r"\s*\d+$")
_JOINERS = (" ", "-", "_")


def preset_image_basenames(text: str) -> tuple[str, ...]:
    """
    Candidate image basenames named after the preset itself.

    The preset label, minus its index and trailing variant number, is offered
    in the spellings artwork tends to use: ``"164: Trem EP 1"`` looks for
    ``trem ep``, ``trem-ep``, ``trem_ep`` (and the same without punctuation).
    Dropping a file named after a preset into the icon folder is therefore
    enough to give that preset its own image -- no table to update here.

    Only multi-word phrases are returned. A single word is far too broad to be
    preset-specific ("bass", "lead"), and the engine and family lookups already
    cover that case.

    :param text: Preset label, with or without its index.
    :return: Candidate basenames without extension, most specific first.
    """
    phrase = _TRAILING_INDEX.sub("", preset_match_text(text)).strip()
    if not phrase:
        return ()

    candidates = []
    for tokens in (phrase.split(), re.sub(r"[^a-z0-9\s]", "", phrase).split()):
        if len(tokens) < 2:
            continue
        for joiner in _JOINERS:
            candidate = joiner.join(tokens)
            if candidate and candidate not in candidates:
                candidates.append(candidate)
    return tuple(candidates)
