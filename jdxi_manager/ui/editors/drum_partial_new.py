import logging
import os
import re
from typing import Dict

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QGridLayout,
    QGroupBox,
    QFormLayout,
    QSpinBox,
    QComboBox,
    QTabWidget,
    QCheckBox,
)
from jdxi_manager.data.drums import get_address_for_partial, get_address_for_partial_new, DRUM_ADDRESSES
from jdxi_manager.data.parameter.drums import DrumParameter
from jdxi_manager.midi.constants import (
    TEMPORARY_DRUM_KIT_AREA)
from jdxi_manager.midi.constants.sysex import (
    TEMPORARY_TONE_AREA, DRUM_KIT_AREA
)
from jdxi_manager.data.parameter.drums import get_address_for_partial_name
from jdxi_manager.midi.preset.loader import PresetLoader
from jdxi_manager.ui.widgets.slider import Slider

instrument_icon_folder = "drum_kits"


RMwaves = (
    "000: --- OFF ---",
    "001: 78 Kick P",
    "002: 606 Kick P",
    "003: 808 Kick 1aP",
    "004: 808 Kick 1bP",
    "005: 808 Kick 1cP",
    "006: 808 Kick 2aP",
    "007: 808 Kick 2bP",
    "008: 808 Kick 2cP",
    "009: 808 Kick 3aP",
    "010: 808 Kick 3bP",
    "011: 808 Kick 3cP",
    "012: 808 Kick 4aP",
    "013: 808 Kick 4bP",
    "014: 808 Kick 4cP",
    "015: 808 Kick 1Lp",
    "016: 808 Kick 2Lp",
    "017: 909 Kick 1aP",
    "018: 909 Kick 1bP",
    "019: 909 Kick 1cP",
    "020: 909 Kick 2bP",
    "021: 909 Kick 2cP",
    "022: 909 Kick 3P",
    "023: 909 Kick 4",
    "024: 909 Kick 5",
    "025: 909 Kick 6",
    "026: 909 DstKickP",
    "027: 909 Kick Lp",
    "028: 707 Kick 1 P",
    "029: 707 Kick 2 P",
    "030: 626 Kick 1 P",
    "031: 626 Kick 2 P",
    "032: Analog Kick1",
    "033: Analog Kick2",
    "034: Analog Kick3",
    "035: Analog Kick4",
    "036: Analog Kick5",
    "037: PlasticKick1",
    "038: PlasticKick2",
    "039: Synth Kick 1",
    "040: Synth Kick 2",
    "041: Synth Kick 3",
    "042: Synth Kick 4",
    "043: Synth Kick 5",
    "044: Synth Kick 6",
    "045: Synth Kick 7",
    "046: Synth Kick 8",
    "047: Synth Kick 9",
    "048: Synth Kick10",
    "049: Synth Kick11",
    "050: Synth Kick12",
    "051: Synth Kick13",
    "052: Synth Kick14",
    "053: Synth Kick15",
    "054: Vint Kick P",
    "055: Jungle KickP",
    "056: HashKick 1 P",
    "057: HashKick 2 P",
    "058: Lite Kick P",
    "059: Dry Kick 1",
    "060: Dry Kick 2",
    "061: Tight Kick P",
    "062: Old Kick",
    "063: Warm Kick P",
    "064: Hush Kick P",
    "065: Power Kick",
    "066: Break Kick",
    "067: Turbo Kick",
    "068: TM-2 Kick 1",
    "069: TM-2 Kick 2",
    "070: PurePhatKckP",
    "071: Bright KickP",
    "072: LoBit Kick1P",
    "073: LoBit Kick2P",
    "074: Dance Kick P",
    "075: Hip Kick P",
    "076: HipHop Kick",
    "077: Mix Kick 1",
    "078: Mix Kick 2",
    "079: Wide Kick P",
    "080: LD Kick P",
    "081: SF Kick 1 P",
    "082: SF Kick 2 P",
    "083: TY Kick P",
    "084: WD Kick P",
    "085: Reg.Kick P",
    "086: Rock Kick P",
    "087: Jz Dry Kick",
    "088: Jazz Kick P",
    "089: 78 Snr",
    "090: 606 Snr 1 P",
    "091: 606 Snr 2 P",
    "092: 808 Snr 1a P",
    "093: 808 Snr 1b P",
    "094: 808 Snr 1c P",
    "095: 808 Snr 2a P",
    "096: 808 Snr 2b P",
    "097: 808 Snr 2c P",
    "098: 808 Snr 3a P",
    "099: 808 Snr 3b P",
    "100: 808 Snr 3c P",
    "101: 909 Snr 1a P",
    "102: 909 Snr 1b P",
    "103: 909 Snr 1c P",
    "104: 909 Snr 1d P",
    "105: 909 Snr 2a P",
    "106: 909 Snr 2b P",
    "107: 909 Snr 2c P",
    "108: 909 Snr 2d P",
    "109: 909 Snr 3a P",
    "110: 909 Snr 3b P",
    "111: 909 Snr 3c P",
    "112: 909 Snr 3d P",
    "113: 909 DstSnr1P",
    "114: 909 DstSnr2P",
    "115: 909 DstSnr3P",
    "116: 707 Snr 1a P",
    "117: 707 Snr 2a P",
    "118: 707 Snr 1b P",
    "119: 707 Snr 2b P",
    "120: 626 Snr 1",
    "121: 626 Snr 2",
    "122: 626 Snr 3",
    "123: 626 Snr 1a P",
    "124: 626 Snr 3a P",
    "125: 626 Snr 1b P",
    "126: 626 Snr 2 P",
    "127: 626 Snr 3b P",
    "128: Analog Snr 1",
    "129: Analog Snr 2",
    "130: Analog Snr 3",
    "131: Synth Snr 1",
    "132: Synth Snr 2",
    "133: 106 Snr",
    "134: Sim Snare",
    "135: Jungle Snr 1",
    "136: Jungle Snr 2",
    "137: Jungle Snr 3",
    "138: Lite Snare",
    "139: Lo-Bit Snr1P",
    "140: Lo-Bit Snr2P",
    "141: HphpJazzSnrP",
    "142: PurePhatSnrP",
    "143: DRDisco SnrP",
    "144: Ragga Snr",
    "145: Lo-Fi Snare",
    "146: drums_data Snare",
    "147: DanceHallSnr",
    "148: Break Snr",
    "149: Piccolo SnrP",
    "150: TM-2 Snr 1",
    "151: TM-2 Snr 2",
    "152: WoodSnr RS",
    "153: LD Snr",
    "154: SF Snr P",
    "155: TY Snr",
    "156: WD Snr P",
    "157: Tight Snr",
    "158: Reg.Snr1 P",
    "159: Reg.Snr2 P",
    "160: Ballad Snr P",
    "161: Rock Snr1 P",
    "162: Rock Snr2 P",
    "163: LD Rim",
    "164: SF Rim",
    "165: TY Rim",
    "166: WD Rim P",
    "167: Jazz Snr P",
    "168: Jazz Rim P",
    "169: Jz BrshSlapP",
    "170: Jz BrshSwshP",
    "171: Swish&Trn P",
    "172: 78 Rimshot",
    "173: 808 RimshotP",
    "174: 909 RimshotP",
    "175: 707 Rimshot",
    "176: 626 Rimshot",
    "177: Vint Stick P",
    "178: Lo-Bit Stk P",
    "179: Hard Stick P",
    "180: Wild Stick P",
    "181: LD Cstick",
    "182: TY Cstick",
    "183: WD Cstick",
    "184: 606 H.Tom P",
    "185: 808 H.Tom P",
    "186: 909 H.Tom P",
    "187: 707 H.Tom P",
    "188: 626 H.Tom 1",
    "189: 626 H.Tom 2",
    "190: SimV Tom 1 P",
    "191: LD H.Tom P",
    "192: SF H.Tom P",
    "193: TY H.Tom P",
    "194: 808 M.Tom P",
    "195: 909 M.Tom P",
    "196: 707 M.Tom P",
    "197: 626 M.Tom 1",
    "198: 626 M.Tom 2",
    "199: SimV Tom 2 P",
    "200: LD M.Tom P",
    "201: SF M.Tom P",
    "202: TY M.Tom P",
    "203: 606 L.Tom P",
    "204: 808 L.Tom P",
    "205: 909 L.Tom P",
    "206: 707 L.Tom P",
    "207: 626 L.Tom 1",
    "208: 626 L.Tom 2",
    "209: SimV Tom 3 P",
    "210: SimV Tom 4 P",
    "211: LD L.Tom P",
    "212: SF L.Tom P",
    "213: TY L.Tom P",
    "214: 78 CHH",
    "215: 606 CHH",
    "216: 808 CHH",
    "217: 909 CHH 1",
    "218: 909 CHH 2",
    "219: 909 CHH 3",
    "220: 909 CHH 4",
    "221: 707 CHH",
    "222: 626 CHH",
    "223: HipHop CHH",
    "224: Lite CHH",
    "225: Reg.CHH",
    "226: Rock CHH",
    "227: S13 CHH Tip",
    "228: S14 CHH Tip",
    "229: 606 C&OHH",
    "230: 808 C&OHH S",
    "231: 808 C&OHH L",
    "232: Hip PHH",
    "233: Reg.PHH",
    "234: Rock PHH",
    "235: S13 PHH",
    "236: S14 PHH",
    "237: 606 OHH",
    "238: 808 OHH S",
    "239: 808 OHH L",
    "240: 909 OHH 1",
    "241: 909 OHH 2",
    "242: 909 OHH 3",
    "243: 707 OHH",
    "244: 626 OHH",
    "245: HipHop OHH",
    "246: Lite OHH",
    "247: Reg.OHH",
    "248: Rock OHH",
    "249: S13 OHH Shft",
    "250: S14 OHH Shft",
    "251: 78 Cymbal",
    "252: 606 Cymbal",
    "253: 808 Cymbal 1",
    "254: 808 Cymbal 2",
    "255: 808 Cymbal 3",
    "256: 909 CrashCym",
    "257: 909 Rev Cym",
    "258: MG Nz Cym",
    "259: 707 CrashCym",
    "260: 626 CrashCym",
    "261: Crash Cym 1",
    "262: Crash Cym 2",
    "263: Rock Crash 1",
    "264: Rock Crash 2",
    "265: P17 CrashTip",
    "266: S18 CrashTip",
    "267: Z18kCrashSft",
    "268: Jazz Crash",
    "269: 909 RideCym",
    "270: 707 RideCym",
    "271: 626 RideCym",
    "272: Ride Cymbal",
    "273: 626 ChinaCym",
    "274: China Cymbal",
    "275: Splash Cym",
    "276: 626 Cup",
    "277: Rock Rd Cup",
    "278: 808 ClapS1 P",
    "279: 808 ClapS2 P",
    "280: 808 ClapL1 P",
    "281: 808 ClapL2 P",
    "282: 909 Clap 1 P",
    "283: 909 Clap 2 P",
    "284: 909 Clap 3 P",
    "285: 909 DstClapP",
    "286: 707 Clap P",
    "287: 626 Clap",
    "288: R8 Clap",
    "289: Cheap Clap",
    "290: Old Clap P",
    "291: Hip Clap",
    "292: Dist Clap",
    "293: Hand Clap",
    "294: Club Clap",
    "295: Real Clap",
    "296: Funk Clap",
    "297: Bright Clap",
    "298: TM-2 Clap",
    "299: Amb Clap",
    "300: Disc Clap",
    "301: Claptail",
    "302: Gospel Clap",
    "303: 78 Tamb",
    "304: 707 Tamb P",
    "305: 626 Tamb",
    "306: TM-2 Tamb",
    "307: Tamborine 1",
    "308: Tamborine 2",
    "309: Tamborine 3",
    "310: 808 CowbellP",
    "311: 707 Cowbell",
    "312: 626 Cowbell",
    "313: Cowbell Mute",
    "314: 78 H.Bongo P",
    "315: 727 H.Bongo",
    "316: Bongo Hi Mt",
    "317: Bongo Hi Slp",
    "318: Bongo Hi Op",
    "319: 78 L.Bongo P",
    "320: 727 L.Bongo",
    "321: Bongo Lo Op",
    "322: Bongo Lo Slp",
    "323: 808 H.CongaP",
    "324: 727 H.CngOpP",
    "325: 727 H.CngMtP",
    "326: 626 H.CngaOp",
    "327: 626 H.CngaMt",
    "328: Conga Hi Mt",
    "329: Conga 2H Mt",
    "330: Conga Hi Slp",
    "331: Conga 2H Slp",
    "332: Conga Hi Op",
    "333: Conga 2H Op",
    "334: 808 M.CongaP",
    "335: 78 L.Conga P",
    "336: 808 L.CongaP",
    "337: 727 L.CongaP",
    "338: 626 L.Conga",
    "339: Conga Lo Mt",
    "340: Conga Lo Slp",
    "341: Conga Lo Op",
    "342: Conga 2L Mt",
    "343: Conga 2L Op",
    "344: Conga Slp Op",
    "345: Conga Efx",
    "346: Conga Thumb",
    "347: 727 H.Timbal",
    "348: 626 H.Timbal",
    "349: 727 L.Timbal",
    "350: 626 L.Timbal",
    "351: Timbale 1",
    "352: Timbale 2",
    "353: Timbale 3",
    "354: Timbale 4",
    "355: Timbles LoOp",
    "356: Timbles LoMt",
    "357: TimbalesHand",
    "358: Timbales Rim",
    "359: TmbSideStick",
    "360: 727 H.Agogo",
    "361: 626 H.Agogo",
    "362: 727 L.Agogo",
    "363: 626 L.Agogo",
    "364: 727 Cabasa P",
    "365: Cabasa Up",
    "366: Cabasa Down",
    "367: Cabasa Cut",
    "368: 78 Maracas P",
    "369: 808 MaracasP",
    "370: 727 MaracasP",
    "371: Maracas",
    "372: 727 WhistleS",
    "373: 727 WhistleL",
    "374: Whistle",
    "375: 78 Guiro S",
    "376: 78 Guiro L",
    "377: Guiro",
    "378: Guiro Long",
    "379: 78 Claves P",
    "380: 808 Claves P",
    "381: 626 Claves",
    "382: Claves",
    "383: Wood Block",
    "384: Triangle",
    "385: 78 MetalBt P",
    "386: 727 StrChime",
    "387: 626 Shaker",
    "388: Shaker",
    "389: Finger Snap",
    "390: Club FinSnap",
    "391: Snap",
    "392: Group Snap",
    "393: Op Pandeiro",
    "394: Mt Pandeiro",
    "395: PandeiroOp",
    "396: PandeiroMt",
    "397: PandeiroHit",
    "398: PandeiroRim",
    "399: PandeiroCrsh",
    "400: PandeiroRoll",
    "401: 727 Quijada",
    "402: TablaBayam 1",
    "403: TablaBayam 2",
    "404: TablaBayam 3",
    "405: TablaBayam 4",
    "406: TablaBayam 5",
    "407: TablaBayam 6",
    "408: TablaBayam 7",
    "409: Udo",
    "410: Udu Pot Hi",
    "411: Udu Pot Slp",
    "412: Scratch 1",
    "413: Scratch 2",
    "414: Scratch 3",
    "415: Scratch 4",
    "416: Scratch 5",
    "417: Dance M",
    "418: Ahh M",
    "419: Let's Go M",
    "420: Hah F",
    "421: Yeah F",
    "422: C'mon Baby F",
    "423: Wooh F",
    "424: White Noise",
    "425: Pink Noise",
    "426: Atmosphere",
    "427: PercOrgan 1",
    "428: PercOrgan 2",
    "429: TB Blip",
    "430: D.Mute Gtr",
    "431: Flute Fx",
    "432: Pop Brs Atk",
    "433: Strings Hit",
    "434: Smear Hit",
    "435: O'Skool Hit",
    "436: Orch. Hit",
    "437: Punch Hit",
    "438: Philly Hit",
    "439: ClassicHseHt",
    "440: Tao Hit",
    "441: MG S Zap 1",
    "442: MG S Zap 2",
    "443: MG S Zap 3",
    "444: SH2 S Zap 1",
    "445: SH2 S Zap 2",
    "446: SH2 S Zap 3",
    "447: SH2 S Zap 4",
    "448: SH2 S Zap 5",
    "449: SH2 U Zap 1",
    "450: SH2 U Zap 2",
    "451: SH2 U Zap 3",
    "452: SH2 U Zap 4",
    "453: SH2 U Zap 5",
)

"""
For reference:
|-------------+-----------+----------------------------------------------------|
| 00 20 | 0000 00aa |                             WMT Velocity Control (0 - 2) |
|       |                                                    | OFF, ON, RANDOM |
|-------------+-----------+----------------------------------------------------|
| 00 21 | 0000 000a | WMT1 Wave Switch (0 - 1) |
| | | OFF, ON |
| 00 22 | 0000 00aa | WMT1 Wave Group Type (0) |
|# 00 23 | 0000 aaaa | |
| | 0000 bbbb | |
| | 0000 cccc | |
| | 0000 dddd | WMT1 Wave Group ID (0 - 16384) |
| | | OFF, 1 - 16384 |
|# 00 27 | 0000 aaaa | |
| | 0000 bbbb | |
| | 0000 cccc | |
| | 0000 dddd | WMT1 Wave Number L (Mono) (0 - 16384) |
| | | OFF, 1 - 16384 |
|# 00 2B | 0000 aaaa | |
| | 0000 bbbb | |
| | 0000 cccc | |
| | 0000 dddd | WMT1 Wave Number R (0 - 16384) |
| | | OFF, 1 - 16384 |
| 00 2F | 0000 00aa | WMT1 Wave Gain (0 - 3) |
| | | -6, 0, +6, +12 [dB] |
| 00 30 | 0000 000a | WMT1 Wave FXM Switch (0 - 1) |
| | | OFF, ON |
| 00 31 | 0000 00aa | WMT1 Wave FXM Color (0 - 3) |
| | | 1 - 4 |
| 00 32 | 000a aaaa | WMT1 Wave FXM Depth (0 - 16) |
| 00 33 | 0000 000a | WMT1 Wave Tempo Sync (0 - 1) |
| | | OFF, ON |
| 00 34 | 0aaa aaaa | WMT1 Wave Coarse Tune (16 - 112) |
| | | -48 - +48 |
| 00 35 | 0aaa aaaa | WMT1 Wave Fine Tune (14 - 114) |
| | | -50 - +50 |
| 00 36 | 0aaa aaaa | WMT1 Wave Pan (0 - 127) |
| | | L64 - 63R |
| 00 37 | 0000 000a | WMT1 Wave Random Pan Switch (0 - 1) |
| | | OFF, ON |
| 00 38 | 0000 00aa | WMT1 Wave Alternate Pan Switch (0 - 2) |
| | | OFF, ON, REVERSE |
| 00 39 | 0aaa aaaa | WMT1 Wave Level (0 - 127) |
| 00 3A | 0aaa aaaa | WMT1 Velocity Range Lower (1 - 127) |
| | | 1 - UPPER |
| 00 3B | 0aaa aaaa | WMT1 Velocity Range Upper (1 - 127) |
| | | LOWER - 127 |
| 00 3C | 0aaa aaaa | WMT1 Velocity Fade Width Lower (0 - 127) |
| 00 3D | 0aaa aaaa | WMT1 Velocity Fade Width Upper (0 - 127) |
|-------------+-----------+----------------------------------------------------|
"""

class DrumPartialEditor(QWidget):
    """Editor for address single partial"""

    def __init__(self, midi_helper=None, partial_num=0, partial_name=None, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.partial_num = partial_num  # This is now the numerical index
        self.partial_name = partial_name  # This is now the numerical index

        # Calculate the address for this partial
        try:
            from jdxi_manager.data.drums import get_address_for_partial

            self.partial_address = get_address_for_partial_name(self.partial_name)
            logging.info(
                f"Initialized partial {partial_num} with address: {hex(self.partial_address)}"
            )
        except Exception as e:
            logging.error(
                f"Error calculating address for partial {partial_num}: {str(e)}"
            )
            self.partial_address = 0x00

        # Store parameter controls for easy access
        self.controls: Dict[DrumParameter, QWidget] = {}

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)

        # Create grid layout for parameter groups
        grid_layout = QGridLayout()
        scroll_layout.addLayout(grid_layout)

        # Add parameter groups
        pitch_group = self._create_pitch_group()
        grid_layout.addWidget(pitch_group, 0, 0)

        output_group = self._create_output_group()
        grid_layout.addWidget(output_group, 0, 2)

        tvf_group = self._create_tvf_group()
        grid_layout.addWidget(tvf_group, 1, 2)

        pitch_env_group = self._create_pitch_env_group()
        grid_layout.addWidget(pitch_env_group, 0, 1)

        wmt_group = self._create_wmt_group()
        grid_layout.addWidget(wmt_group, 1, 0)

        tva_group = self._create_tva_group()
        grid_layout.addWidget(tva_group, 1, 1)

        # scroll_area.setLayout(scroll_layout)
        main_layout.addWidget(scroll_area)

    def _create_pitch_group(self) -> QGroupBox:
        """Create and return the pitch control group"""
        group = QGroupBox("Pitch")
        layout = QFormLayout()

        # Coarse Tune control
        self.coarse_tune = QSpinBox()
        self.coarse_tune.setRange(-48, 48)
        self.coarse_tune.valueChanged.connect(self._on_coarse_tune_changed)
        layout.addRow("Coarse Tune", self.coarse_tune)

        # Fine Tune control
        self.fine_tune = QSpinBox()
        self.fine_tune.setRange(-50, 50)
        self.fine_tune.valueChanged.connect(self._on_fine_tune_changed)
        layout.addRow("Fine Tune", self.fine_tune)

        group.setLayout(layout)
        return group

    def _create_output_group(self) -> QGroupBox:
        """Create and return the output control group"""
        group = QGroupBox("Output")
        layout = QFormLayout()

        # Level control
        self.level = QSpinBox()
        self.level.setRange(0, 127)
        self.level.valueChanged.connect(self._on_level_changed)
        layout.addRow("Level", self.level)

        # Pan control
        self.pan = QSpinBox()
        self.pan.setRange(-64, 63)
        self.pan.valueChanged.connect(self._on_pan_changed)
        layout.addRow("Pan", self.pan)

        group.setLayout(layout)
        return group

    def _create_tvf_group(self) -> QGroupBox:
        """Create and return the TVF control group"""
        group = QGroupBox("TVF")
        layout = QFormLayout()

        # Cutoff control
        self.cutoff = QSpinBox()
        self.cutoff.setRange(0, 127)
        self.cutoff.valueChanged.connect(self._on_cutoff_changed)
        layout.addRow("Cutoff", self.cutoff)

        # Resonance control
        self.resonance = QSpinBox()
        self.resonance.setRange(0, 127)
        self.resonance.valueChanged.connect(self._on_resonance_changed)
        layout.addRow("Resonance", self.resonance)

        group.setLayout(layout)
        return group

    def _create_pitch_env_group(self) -> QGroupBox:
        """Create and return the pitch envelope control group"""
        group = QGroupBox("Pitch Envelope")
        layout = QFormLayout()

        # Attack Time control
        self.pitch_env_attack = QSpinBox()
        self.pitch_env_attack.setRange(0, 127)
        self.pitch_env_attack.valueChanged.connect(self._on_pitch_env_attack_changed)
        layout.addRow("Attack Time", self.pitch_env_attack)

        # Decay Time control
        self.pitch_env_decay = QSpinBox()
        self.pitch_env_decay.setRange(0, 127)
        self.pitch_env_decay.valueChanged.connect(self._on_pitch_env_decay_changed)
        layout.addRow("Decay Time", self.pitch_env_decay)

        group.setLayout(layout)
        return group

    def _create_tva_group(self) -> QGroupBox:
        """Create and return the TVA control group"""
        group = QGroupBox("TVA")
        layout = QFormLayout()

        # Attack Time control
        self.tva_attack = QSpinBox()
        self.tva_attack.setRange(0, 127)
        self.tva_attack.valueChanged.connect(self._on_tva_attack_changed)
        layout.addRow("Attack Time", self.tva_attack)

        # Decay Time control
        self.tva_decay = QSpinBox()
        self.tva_decay.setRange(0, 127)
        self.tva_decay.valueChanged.connect(self._on_tva_decay_changed)
        layout.addRow("Decay Time", self.tva_decay)

        group.setLayout(layout)
        return group

    def _create_wmt_group(self) -> QGroupBox:
        """Create and return the WMT control group"""
        group = QGroupBox("Wave Mix Table")
        layout = QVBoxLayout()

        # WMT1 controls
        wmt1_group = QGroupBox("WMT1")
        wmt1_layout = QFormLayout()

        self.wmt1_wave_switch = QCheckBox()
        self.wmt1_wave_switch.stateChanged.connect(self._on_wmt1_wave_switch_changed)
        wmt1_layout.addRow("Wave Switch", self.wmt1_wave_switch)

        self.wmt1_wave_l = QSpinBox()
        self.wmt1_wave_l.setRange(0, 16384)
        self.wmt1_wave_l.valueChanged.connect(self._on_wmt1_wave_number_l_changed)
        wmt1_layout.addRow("Wave L", self.wmt1_wave_l)

        self.wmt1_wave_r = QSpinBox()
        self.wmt1_wave_r.setRange(0, 16384)
        self.wmt1_wave_r.valueChanged.connect(self._on_wmt1_wave_number_r_changed)
        wmt1_layout.addRow("Wave R", self.wmt1_wave_r)

        wmt1_group.setLayout(wmt1_layout)
        layout.addWidget(wmt1_group)

        # WMT2 controls
        wmt2_group = QGroupBox("WMT2")
        wmt2_layout = QFormLayout()

        self.wmt2_wave_switch = QCheckBox()
        self.wmt2_wave_switch.stateChanged.connect(self._on_wmt2_wave_switch_changed)
        wmt2_layout.addRow("Wave Switch", self.wmt2_wave_switch)

        self.wmt2_wave_l = QSpinBox()
        self.wmt2_wave_l.setRange(0, 16384)
        self.wmt2_wave_l.valueChanged.connect(self._on_wmt2_wave_number_l_changed)
        wmt2_layout.addRow("Wave L", self.wmt2_wave_l)

        self.wmt2_wave_r = QSpinBox()
        self.wmt2_wave_r.setRange(0, 16384)
        self.wmt2_wave_r.valueChanged.connect(self._on_wmt2_wave_number_l_changed)
        wmt2_layout.addRow("Wave R", self.wmt2_wave_r)

        wmt2_group.setLayout(wmt2_layout)
        layout.addWidget(wmt2_group)

        group.setLayout(layout)
        return group

    def _on_wmt1_wave_switch_changed(self, value: int):
        """ change wmt1 wave switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address, 
            param=DrumParameter.WMT1_WAVE_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_group_type_changed(self, value: int):
        """ change wmt1 wave group type value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GROUP_TYPE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_group_id_changed(self, value: int):
        """ change wmt1 wave group id value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GROUP_ID.value[0],
            value=value
        )           
    
    def _on_wmt1_wave_number_l_changed(self, value: int):
        """ change wmt1 wave number l value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address, 
            param=DrumParameter.WMT1_WAVE_NUMBER_L.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt1_wave_number_r_changed(self, value: int):
        """ change wmt1 wave number r value """ 
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )           
    
    def _on_wmt1_wave_gain_changed(self, value: int):
        """ change wmt1 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_switch_changed(self, value: int):
        """ change wmt1 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_SWITCH.value[0],
            value=value
        )                   
    
    def _on_wmt1_wave_fxm_color_changed(self, value: int):
        """ change wmt1 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address, 
            param=DrumParameter.WMT1_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_depth_changed(self, value: int):
        """ change wmt1 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_DEPTH.value[0],
            value=value
        )   
    
    def _on_wmt1_wave_coarse_tune_changed(self, value: int):
        """ change wmt1 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_tempo_sync_changed(self, value: int):
        """ change wmt1 wave tempo sync value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_TEMPO_SYNC.value[0],
            value=value
        )

    def _on_wmt1_wave_fine_tune_changed(self, value: int):
        """ change wmt1 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FINE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_pan_changed(self, value: int):
        """ change wmt1 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_PAN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_random_pan_switch_changed(self, value: int):
        """ change wmt1 wave random pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt1 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_level_changed(self, value: int):
        """ change wmt1 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_LEVEL.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_range_lower_changed(self, value: int):
        """ change wmt1 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_range_upper_changed(self, value: int):
        """ change wmt1 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt1 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address, 
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt1 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address, 
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_wave_r_changed(self, value: int):
        """Handle WMT1 Wave R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,  # Use self.group instead of partial_address
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )

    def _on_wmt1_wave_r_changed(self, value: int):
        """Handle WMT1 Wave R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,  # Use self.group instead of partial_address
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt1_wave_gain_changed(self, value: int):
        """ change wmt1 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_switch_changed(self, value: int):
        """ change wmt1 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_color_changed(self, value: int):
        """ change wmt1 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_depth_changed(self, value: int):  
        """ change wmt1 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_DEPTH.value[0],
            value=value 
        )
    
    def _on_wmt1_wave_coarse_tune_changed(self, value: int):
        """ change wmt1 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fine_tune_changed(self, value: int):
        """ change wmt1 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FINE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_pan_changed(self, value: int):    
        """ change wmt1 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_PAN.value[0],
            value=value 
        )
    
    def _on_wmt1_wave_random_pan_switch_changed(self, value: int):
        """ change wmt1 wave random pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt1 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_level_changed(self, value: int):  
        """ change wmt1 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_LEVEL.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_range_lower_changed(self, value: int):
        """ change wmt1 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )

    def _on_wmt1_velocity_range_upper_changed(self, value: int):
        """ change wmt1 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
                group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt1 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt1 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_wave_r_changed(self, value: int):
        """Handle WMT1 Wave R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,  # Use self.group instead of partial_address
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt1_wave_gain_changed(self, value: int):
        """ change wmt1 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_switch_changed(self, value: int):
        """ change wmt1 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_color_changed(self, value: int):
        """ change wmt1 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_depth_changed(self, value: int):  
        """ change wmt1 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_DEPTH.value[0],
            value=value 
        )
    
    def _on_wmt1_wave_coarse_tune_changed(self, value: int):
        """ change wmt1 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fine_tune_changed(self, value: int):
        """ change wmt1 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FINE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_pan_changed(self, value: int):    
        """ change wmt1 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_PAN.value[0],
            value=value 
        )
    
    def _on_wmt1_wave_random_pan_switch_changed(self, value: int):
        """ change wmt1 wave random pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt1 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_level_changed(self, value: int):  
        """ change wmt1 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_LEVEL.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_range_lower_changed(self, value: int):
        """ change wmt1 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )

    def _on_wmt1_velocity_range_upper_changed(self, value: int):
        """ change wmt1 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
                group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt1 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt1 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_wave_r_changed(self, value: int):
        """Handle WMT1 Wave R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,  # Use self.group instead of partial_address
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt1_wave_gain_changed(self, value: int):
        """ change wmt1 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_switch_changed(self, value: int):
        """ change wmt1 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_color_changed(self, value: int):
        """ change wmt1 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_depth_changed(self, value: int):
        """ change wmt1 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_DEPTH.value[0],
            value=value
        )   
    
    def _on_wmt1_wave_coarse_tune_changed(self, value: int):
        """ change wmt1 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fine_tune_changed(self, value: int):
        """ change wmt1 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FINE_TUNE.value[0],       
            value=value
        )
    
    def _on_wmt1_wave_pan_changed(self, value: int):
        """ change wmt1 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_PAN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_random_pan_switch_changed(self, value: int):
        """ change wmt1 wave random pan switch value """
        return self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt1 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_level_changed(self, value: int):
        """ change wmt1 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_LEVEL.value[0],
            value=value
        )   
    
    def _on_wmt1_velocity_range_lower_changed(self, value: int):
        """ change wmt1 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )
        
    def _on_wmt1_velocity_range_upper_changed(self, value: int):
        """ change wmt1 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt1 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt1 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_wave_r_changed(self, value: int):
        """Handle WMT1 Wave R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,  # Use self.group instead of partial_address
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt1_wave_gain_changed(self, value: int):
        """ change wmt1 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_switch_changed(self, value: int):
        """ change wmt1 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_color_changed(self, value: int):
        """ change wmt1 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_depth_changed(self, value: int):
        """ change wmt1 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_DEPTH.value[0],
            value=value
        )   
    
    def _on_wmt1_wave_coarse_tune_changed(self, value: int):
        """ change wmt1 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fine_tune_changed(self, value: int):
        """ change wmt1 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FINE_TUNE.value[0],       
            value=value
        )
    
    def _on_wmt1_wave_pan_changed(self, value: int):
        """ change wmt1 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_PAN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_random_pan_switch_changed(self, value: int):
        """ change wmt1 wave random pan switch value """
        return self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt1 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_level_changed(self, value: int):
        """ change wmt1 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_LEVEL.value[0],
            value=value
        )   
    
    def _on_wmt1_velocity_range_lower_changed(self, value: int):
        """ change wmt1 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )
        
    def _on_wmt1_velocity_range_upper_changed(self, value: int):
        """ change wmt1 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt1 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt1 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_wave_r_changed(self, value: int):
        """Handle WMT1 Wave R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,  # Use self.group instead of partial_address
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt1_wave_gain_changed(self, value: int):
        """ change wmt1 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_switch_changed(self, value: int):
        """ change wmt1 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_color_changed(self, value: int):
        """ change wmt1 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_depth_changed(self, value: int):
        """ change wmt1 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_DEPTH.value[0],
            value=value
        )   
    
    def _on_wmt1_wave_coarse_tune_changed(self, value: int):
        """ change wmt1 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fine_tune_changed(self, value: int):
        """ change wmt1 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FINE_TUNE.value[0],       
            value=value
        )
    
    def _on_wmt1_wave_pan_changed(self, value: int):
        """ change wmt1 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_PAN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_random_pan_switch_changed(self, value: int):
        """ change wmt1 wave random pan switch value """
        return self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt1 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_level_changed(self, value: int):
        """ change wmt1 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_LEVEL.value[0],
            value=value
        )   
    
    def _on_wmt1_velocity_range_lower_changed(self, value: int):
        """ change wmt1 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )
        
    def _on_wmt1_velocity_range_upper_changed(self, value: int):
        """ change wmt1 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt1 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt1 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_wave_r_changed(self, value: int):
        """Handle WMT1 Wave R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,  # Use self.group instead of partial_address
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt1_wave_gain_changed(self, value: int):
        """ change wmt1 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_switch_changed(self, value: int):
        """ change wmt1 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_color_changed(self, value: int):
        """ change wmt1 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_depth_changed(self, value: int):
        """ change wmt1 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_DEPTH.value[0],
            value=value
        )   
    
    def _on_wmt1_wave_coarse_tune_changed(self, value: int):
        """ change wmt1 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fine_tune_changed(self, value: int):
        """ change wmt1 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FINE_TUNE.value[0],       
            value=value
        )
    
    def _on_wmt1_wave_pan_changed(self, value: int):
        """ change wmt1 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_PAN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_random_pan_switch_changed(self, value: int):
        """ change wmt1 wave random pan switch value """
        return self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt1 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_level_changed(self, value: int):
        """ change wmt1 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_LEVEL.value[0],
            value=value
        )   
    
    def _on_wmt1_velocity_range_lower_changed(self, value: int):
        """ change wmt1 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )
        
    def _on_wmt1_velocity_range_upper_changed(self, value: int):
        """ change wmt1 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt1 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt1 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_wave_r_changed(self, value: int):
        """Handle WMT1 Wave R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,  # Use self.group instead of partial_address
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt1_wave_gain_changed(self, value: int):
        """ change wmt1 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_switch_changed(self, value: int):
        """ change wmt1 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_color_changed(self, value: int):
        """ change wmt1 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_depth_changed(self, value: int):
        """ change wmt1 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_DEPTH.value[0],
            value=value
        )   
    
    def _on_wmt1_wave_coarse_tune_changed(self, value: int):
        """ change wmt1 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fine_tune_changed(self, value: int):
        """ change wmt1 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FINE_TUNE.value[0],       
            value=value
        )
    
    def _on_wmt1_wave_pan_changed(self, value: int):
        """ change wmt1 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_PAN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_random_pan_switch_changed(self, value: int):
        """ change wmt1 wave random pan switch value """
        return self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt1 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_level_changed(self, value: int):
        """ change wmt1 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_LEVEL.value[0],
            value=value
        )   
    
    def _on_wmt1_velocity_range_lower_changed(self, value: int):
        """ change wmt1 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )
        
    def _on_wmt1_velocity_range_upper_changed(self, value: int):
        """ change wmt1 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt1 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt1 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_wave_r_changed(self, value: int):
        """Handle WMT1 Wave R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,  # Use self.group instead of partial_address
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt1_wave_gain_changed(self, value: int):
        """ change wmt1 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_switch_changed(self, value: int):
        """ change wmt1 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_color_changed(self, value: int):
        """ change wmt1 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_depth_changed(self, value: int):
        """ change wmt1 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_DEPTH.value[0],
            value=value
        )   
    
    def _on_wmt1_wave_coarse_tune_changed(self, value: int):
        """ change wmt1 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fine_tune_changed(self, value: int):
        """ change wmt1 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FINE_TUNE.value[0],       
            value=value
        )
    
    def _on_wmt1_wave_pan_changed(self, value: int):
        """ change wmt1 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_PAN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_random_pan_switch_changed(self, value: int):
        """ change wmt1 wave random pan switch value """
        return self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt1 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_level_changed(self, value: int):
        """ change wmt1 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_LEVEL.value[0],
            value=value
        )   
    
    def _on_wmt1_velocity_range_lower_changed(self, value: int):
        """ change wmt1 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )
        
    def _on_wmt1_velocity_range_upper_changed(self, value: int):
        """ change wmt1 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt1 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt1 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_wave_r_changed(self, value: int):
        """Handle WMT1 Wave R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,  # Use self.group instead of partial_address
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt1_wave_gain_changed(self, value: int):
        """ change wmt1 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_switch_changed(self, value: int):
        """ change wmt1 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_color_changed(self, value: int):
        """ change wmt1 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_depth_changed(self, value: int):
        """ change wmt1 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_DEPTH.value[0],
            value=value
        )   
    
    def _on_wmt1_wave_coarse_tune_changed(self, value: int):
        """ change wmt1 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fine_tune_changed(self, value: int):
        """ change wmt1 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FINE_TUNE.value[0],       
            value=value
        )
    
    def _on_wmt1_wave_pan_changed(self, value: int):
        """ change wmt1 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_PAN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_random_pan_switch_changed(self, value: int):
        """ change wmt1 wave random pan switch value """
        return self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt1 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_level_changed(self, value: int):
        """ change wmt1 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_LEVEL.value[0],
            value=value
        )   
    
    def _on_wmt1_velocity_range_lower_changed(self, value: int):
        """ change wmt1 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )
        
    def _on_wmt1_velocity_range_upper_changed(self, value: int):
        """ change wmt1 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt1 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt1 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_wave_r_changed(self, value: int):
        """Handle WMT1 Wave R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,  # Use self.group instead of partial_address
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt1_wave_gain_changed(self, value: int):
        """ change wmt1 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_switch_changed(self, value: int):
        """ change wmt1 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_color_changed(self, value: int):
        """ change wmt1 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_depth_changed(self, value: int):
        """ change wmt1 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_DEPTH.value[0],
            value=value
        )   
    
    def _on_wmt1_wave_coarse_tune_changed(self, value: int):
        """ change wmt1 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fine_tune_changed(self, value: int):
        """ change wmt1 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FINE_TUNE.value[0],       
            value=value
        )
    
    def _on_wmt1_wave_pan_changed(self, value: int):
        """ change wmt1 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_PAN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_random_pan_switch_changed(self, value: int):
        """ change wmt1 wave random pan switch value """
        return self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt1 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_level_changed(self, value: int):
        """ change wmt1 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_LEVEL.value[0],
            value=value
        )   
    
    def _on_wmt1_velocity_range_lower_changed(self, value: int):
        """ change wmt1 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )
        
    def _on_wmt1_velocity_range_upper_changed(self, value: int):
        """ change wmt1 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt1 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt1 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_wave_r_changed(self, value: int):
        """Handle WMT1 Wave R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,  # Use self.group instead of partial_address
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt1_wave_gain_changed(self, value: int):
        """ change wmt1 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_switch_changed(self, value: int):
        """ change wmt1 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_color_changed(self, value: int):
        """ change wmt1 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_depth_changed(self, value: int):
        """ change wmt1 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_DEPTH.value[0],
            value=value
        )   
    
    def _on_wmt1_wave_coarse_tune_changed(self, value: int):
        """ change wmt1 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fine_tune_changed(self, value: int):
        """ change wmt1 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FINE_TUNE.value[0],       
            value=value
        )
    
    def _on_wmt1_wave_pan_changed(self, value: int):
        """ change wmt1 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_PAN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_random_pan_switch_changed(self, value: int):
        """ change wmt1 wave random pan switch value """
        return self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt1 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_level_changed(self, value: int):
        """ change wmt1 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_LEVEL.value[0],
            value=value
        )   
    
    def _on_wmt1_velocity_range_lower_changed(self, value: int):
        """ change wmt1 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )
        
    def _on_wmt1_velocity_range_upper_changed(self, value: int):
        """ change wmt1 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt1 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt1 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_wave_r_changed(self, value: int):
        """Handle WMT1 Wave R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,  # Use self.group instead of partial_address
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt1_wave_gain_changed(self, value: int):
        """ change wmt1 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_switch_changed(self, value: int):
        """ change wmt1 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_color_changed(self, value: int):
        """ change wmt1 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_depth_changed(self, value: int):
        """ change wmt1 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_DEPTH.value[0],
            value=value
        )   
    
    def _on_wmt1_wave_coarse_tune_changed(self, value: int):
        """ change wmt1 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fine_tune_changed(self, value: int):
        """ change wmt1 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FINE_TUNE.value[0],       
            value=value
        )
    
    def _on_wmt1_wave_pan_changed(self, value: int):
        """ change wmt1 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_PAN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_random_pan_switch_changed(self, value: int):
        """ change wmt1 wave random pan switch value """
        return self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt1 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_level_changed(self, value: int):
        """ change wmt1 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_LEVEL.value[0],
            value=value
        )   
    
    def _on_wmt1_velocity_range_lower_changed(self, value: int):
        """ change wmt1 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )
        
    def _on_wmt1_velocity_range_upper_changed(self, value: int):
        """ change wmt1 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt1 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt1 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_wave_r_changed(self, value: int):
        """Handle WMT1 Wave R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,  # Use self.group instead of partial_address
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt1_wave_gain_changed(self, value: int):
        """ change wmt1 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_switch_changed(self, value: int):
        """ change wmt1 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_color_changed(self, value: int):
        """ change wmt1 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_depth_changed(self, value: int):
        """ change wmt1 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_DEPTH.value[0],
            value=value
        )   
    
    def _on_wmt1_wave_coarse_tune_changed(self, value: int):
        """ change wmt1 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fine_tune_changed(self, value: int):
        """ change wmt1 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FINE_TUNE.value[0],       
            value=value
        )
    
    def _on_wmt1_wave_pan_changed(self, value: int):
        """ change wmt1 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_PAN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_random_pan_switch_changed(self, value: int):
        """ change wmt1 wave random pan switch value """
        return self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt1 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_level_changed(self, value: int):
        """ change wmt1 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_LEVEL.value[0],
            value=value
        )   
    
    def _on_wmt1_velocity_range_lower_changed(self, value: int):
        """ change wmt1 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )
        
    def _on_wmt1_velocity_range_upper_changed(self, value: int):
        """ change wmt1 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt1 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt1 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_wave_r_changed(self, value: int):
        """Handle WMT1 Wave R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,  # Use self.group instead of partial_address
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt1_wave_gain_changed(self, value: int):
        """ change wmt1 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_switch_changed(self, value: int):
        """ change wmt1 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_color_changed(self, value: int):
        """ change wmt1 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_depth_changed(self, value: int):
        """ change wmt1 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_DEPTH.value[0],
            value=value
        )   
    
    def _on_wmt1_wave_coarse_tune_changed(self, value: int):
        """ change wmt1 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fine_tune_changed(self, value: int):
        """ change wmt1 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FINE_TUNE.value[0],       
            value=value
        )
    
    def _on_wmt1_wave_pan_changed(self, value: int):
        """ change wmt1 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_PAN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_random_pan_switch_changed(self, value: int):
        """ change wmt1 wave random pan switch value """
        return self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt1 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_level_changed(self, value: int):
        """ change wmt1 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_LEVEL.value[0],
            value=value
        )   
    
    def _on_wmt1_velocity_range_lower_changed(self, value: int):
        """ change wmt1 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )
        
    def _on_wmt1_velocity_range_upper_changed(self, value: int):
        """ change wmt1 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt1 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt1 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_wave_r_changed(self, value: int):
        """Handle WMT1 Wave R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,  # Use self.group instead of partial_address
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt1_wave_gain_changed(self, value: int):
        """ change wmt1 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_switch_changed(self, value: int):
        """ change wmt1 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_color_changed(self, value: int):
        """ change wmt1 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_depth_changed(self, value: int):
        """ change wmt1 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_DEPTH.value[0],
            value=value
        )   
    
    def _on_wmt1_wave_coarse_tune_changed(self, value: int):
        """ change wmt1 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fine_tune_changed(self, value: int):
        """ change wmt1 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FINE_TUNE.value[0],       
            value=value
        )
    
    def _on_wmt1_wave_pan_changed(self, value: int):
        """ change wmt1 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_PAN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_random_pan_switch_changed(self, value: int):
        """ change wmt1 wave random pan switch value """
        return self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt1 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_level_changed(self, value: int):
        """ change wmt1 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_LEVEL.value[0],
            value=value
        )   
    
    def _on_wmt1_velocity_range_lower_changed(self, value: int):
        """ change wmt1 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )
        
    def _on_wmt1_velocity_range_upper_changed(self, value: int):
        """ change wmt1 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt1 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt1 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_wave_r_changed(self, value: int):
        """Handle WMT1 Wave R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,  # Use self.group instead of partial_address
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt1_wave_gain_changed(self, value: int):
        """ change wmt1 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_switch_changed(self, value: int):
        """ change wmt1 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_color_changed(self, value: int):
        """ change wmt1 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_depth_changed(self, value: int):
        """ change wmt1 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_DEPTH.value[0],
            value=value
        )   
    
    def _on_wmt1_wave_coarse_tune_changed(self, value: int):
        """ change wmt1 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fine_tune_changed(self, value: int):
        """ change wmt1 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FINE_TUNE.value[0],       
            value=value
        )
    
    def _on_wmt1_wave_pan_changed(self, value: int):
        """ change wmt1 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_PAN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_random_pan_switch_changed(self, value: int):
        """ change wmt1 wave random pan switch value """
        return self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt1 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_level_changed(self, value: int):
        """ change wmt1 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_LEVEL.value[0],
            value=value
        )   
    
    def _on_wmt1_velocity_range_lower_changed(self, value: int):
        """ change wmt1 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )
        
    def _on_wmt1_velocity_range_upper_changed(self, value: int):
        """ change wmt1 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt1 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt1 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_wave_r_changed(self, value: int):
        """Handle WMT1 Wave R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,  # Use self.group instead of partial_address
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt1_wave_gain_changed(self, value: int):
        """ change wmt1 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_switch_changed(self, value: int):
        """ change wmt1 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_color_changed(self, value: int):
        """ change wmt1 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fxm_depth_changed(self, value: int):
        """ change wmt1 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_DEPTH.value[0],
            value=value
        )   
    
    def _on_wmt1_wave_coarse_tune_changed(self, value: int):
        """ change wmt1 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt1_wave_fine_tune_changed(self, value: int):
        """ change wmt1 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FINE_TUNE.value[0],       
            value=value
        )
    
    def _on_wmt1_wave_pan_changed(self, value: int):
        """ change wmt1 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_PAN.value[0],
            value=value
        )
    
    def _on_wmt1_wave_random_pan_switch_changed(self, value: int):
        """ change wmt1 wave random pan switch value """
        return self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt1 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt1_wave_level_changed(self, value: int):
        """ change wmt1 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_LEVEL.value[0],
            value=value
        )   
    
    def _on_wmt1_velocity_range_lower_changed(self, value: int):
        """ change wmt1 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )
        
    def _on_wmt1_velocity_range_upper_changed(self, value: int):
        """ change wmt1 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt1 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt1_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt1 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt2_wave_switch_changed(self, value: int):
        """Handle WMT2 Wave Switch parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT2_WAVE_SWITCH.value[0],
            value=value,
            size=1
        )

    def _on_wmt2_wave_group_type_changed(self, value: int):
        """Handle WMT2 Wave Group Type parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT2_WAVE_GROUP_TYPE.value[0],
            value=value,
            size=1
        )

    def _on_wmt2_wave_group_id_changed(self, value: int):
        """Handle WMT2 Wave Group ID parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT2_WAVE_GROUP_ID.value[0],
            value=value,
            size=4
        )

    def _on_wmt2_wave_number_l_changed(self, value: int):
        """Handle WMT2 Wave Number L parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT2_WAVE_NUMBER_L.value[0],
            value=value,
            size=4
        )

    def _on_wmt2_wave_number_r_changed(self, value: int):
        """Handle WMT2 Wave Number R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT2_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )

    def _on_wmt2_wave_gain_changed(self, value: int):
        """ change wmt2 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT2_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt2_wave_fxm_switch_changed(self, value: int):
        """ change wmt2 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT2_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt2_wave_fxm_color_changed(self, value: int):
        """ change wmt2 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT2_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt2_wave_fxm_depth_changed(self, value: int):
        """ change wmt2 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT2_WAVE_FXM_DEPTH.value[0],
            value=value
        )   
    
    def _on_wmt2_wave_coarse_tune_changed(self, value: int):
        """ change wmt2 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT2_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt2_wave_fine_tune_changed(self, value: int):
        """ change wmt2 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT2_WAVE_FINE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt2_wave_pan_changed(self, value: int):
        """ change wmt2 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT2_WAVE_PAN.value[0],
            value=value
        )
    
    def _on_wmt2_wave_random_pan_switch_changed(self, value: int):
        """ change wmt2 wave random pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT2_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt2_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt2 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT2_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt2_wave_level_changed(self, value: int):
        """ change wmt2 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT2_WAVE_LEVEL.value[0],
            value=value
        )
    
    def _on_wmt2_velocity_range_lower_changed(self, value: int):
        """ change wmt2 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT2_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )
    
    def _on_wmt2_velocity_range_upper_changed(self, value: int):
        """ change wmt2 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT2_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt2_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt2 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT2_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt2_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt2 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT2_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt3_wave_switch_changed(self, value: int):
        """ change wmt3 wave switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT3_WAVE_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt3_wave_group_type_changed(self, value: int):
        """ change wmt3 wave group type value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT3_WAVE_GROUP_TYPE.value[0],
            value=value
        )
    
    def _on_wmt3_wave_group_id_changed(self, value: int):
        """ change wmt3 wave group id value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT3_WAVE_GROUP_ID.value[0],
            value=value
        )
    
    def _on_wmt3_wave_number_l_changed(self, value: int):
        """ change wmt3 wave number l value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT3_WAVE_NUMBER_L.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt3_wave_number_r_changed(self, value: int):
        """ change wmt3 wave number r value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT3_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt3_wave_gain_changed(self, value: int):
        """ change wmt3 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT3_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt3_wave_fxm_switch_changed(self, value: int):
        """ change wmt3 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT3_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt3_wave_fxm_color_changed(self, value: int):
        """ change wmt3 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT3_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt3_wave_fxm_depth_changed(self, value: int):
        """ change wmt3 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT3_WAVE_FXM_DEPTH.value[0],
            value=value
        )   
    
    def _on_wmt3_wave_coarse_tune_changed(self, value: int):
        """ change wmt3 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT3_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt3_wave_fine_tune_changed(self, value: int):
        """ change wmt3 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT3_WAVE_FINE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt3_wave_pan_changed(self, value: int):
        """ change wmt3 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT3_WAVE_PAN.value[0],
            value=value
        )
    
    def _on_wmt3_wave_random_pan_switch_changed(self, value: int):
        """ change wmt3 wave random pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT3_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt3_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt3 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT3_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt3_wave_level_changed(self, value: int):
        """ change wmt3 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT3_WAVE_LEVEL.value[0],
            value=value
        )
    
    def _on_wmt3_velocity_range_lower_changed(self, value: int):
        """ change wmt3 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT3_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )
    
    def _on_wmt3_velocity_range_upper_changed(self, value: int):
        """ change wmt3 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT3_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt3_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt3 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT3_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt3_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt3 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT3_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_wmt4_wave_switch_changed(self, value: int):
        """ change wmt4 wave switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_WAVE_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt4_wave_group_type_changed(self, value: int):
        """ change wmt4 wave group type value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_WAVE_GROUP_TYPE.value[0],
            value=value
        )
    
    def _on_wmt4_wave_group_id_changed(self, value: int):
        """ change wmt4 wave group id value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_WAVE_GROUP_ID.value[0],
            value=value
        )
    
    def _on_wmt4_wave_number_l_changed(self, value: int):
        """ change wmt4 wave number l value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_WAVE_NUMBER_L.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt4_wave_number_r_changed(self, value: int):
        """ change wmt4 wave number r value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )
    
    def _on_wmt4_wave_gain_changed(self, value: int):
        """ change wmt4 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_WAVE_GAIN.value[0],
            value=value
        )
    
    def _on_wmt4_wave_fxm_switch_changed(self, value: int):
        """ change wmt4 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_WAVE_FXM_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt4_wave_fxm_color_changed(self, value: int):
        """ change wmt4 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_WAVE_FXM_COLOR.value[0],
            value=value
        )
    
    def _on_wmt4_wave_fxm_depth_changed(self, value: int):
        """ change wmt4 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_WAVE_FXM_DEPTH.value[0],
            value=value
        )   
    
    def _on_wmt4_wave_tempo_sync_changed(self, value: int):
        """ change wmt4 wave tempo sync value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_WAVE_TEMPO_SYNC.value[0],
            value=value
        )
    
    def _on_wmt4_wave_coarse_tune_changed(self, value: int):
        """ change wmt4 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_WAVE_COARSE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt4_wave_fine_tune_changed(self, value: int):
        """ change wmt4 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_WAVE_FINE_TUNE.value[0],
            value=value
        )
    
    def _on_wmt4_wave_pan_changed(self, value: int):
        """ change wmt4 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_WAVE_PAN.value[0],
            value=value
        )
    
    def _on_wmt4_wave_random_pan_switch_changed(self, value: int):
        """ change wmt4 wave random pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt4_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt4 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )
    
    def _on_wmt4_wave_level_changed(self, value: int):
        """ change wmt4 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_WAVE_LEVEL.value[0],
            value=value
        )
    
    def _on_wmt4_velocity_range_lower_changed(self, value: int):
        """ change wmt4 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )
    
    def _on_wmt4_velocity_range_upper_changed(self, value: int):
        """ change wmt4 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )
    
    def _on_wmt4_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt4 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )
    
    def _on_wmt4_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt4 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.WMT4_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )
    
    def _on_tva_level_velocity_sens_slider_changed(self, value: int):
        """Handle TVA Level Velocity Sens change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVA_LEVEL_VELOCITY_SENS.value[0],
                value=value,
            )
            print(f"TVA Level Velocity Sens changed to {value}")

    def _on_tva_env_time1_velocity_sens_slider_changed(self, value: int):
        """Handle TVA Env Time 1 Velocity Sens change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVA_ENV_TIME_1_VELOCITY_SENS.value[0],
                value=value,
            )
            print(f"TVA Env Time 1 Velocity Sens changed to {value}")

    def _on_tva_env_time4_velocity_sens_slider_changed(self, value: int):
        """Handle TVA Env Time 4 Velocity Sens change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVA_ENV_TIME_4_VELOCITY_SENS.value[0],
                value=value,
            )
            print(f"TVA Env Time 4 Velocity Sens changed to {value}")

    def _on_tva_env_time1_slider_changed(self, value: int):
        """Handle TVA Env Time 1 change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVA_ENV_TIME_1.value[0],
                value=value,
            )
            print(f"TVA Env Time 1 changed to {value}")

    def _on_tva_env_time2_slider_changed(self, value: int):
        """Handle TVA Env Time 2 change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVA_ENV_TIME_2.value[0],
                value=value,
            )
            print(f"TVA Env Time 2 changed to {value}")

    def _on_tva_env_time3_slider_changed(self, value: int):
        """Handle TVA Env Time 3 change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVA_ENV_TIME_3.value[0],
                value=value,
            )
            print(f"TVA Env Time 3 changed to {value}")

    def _on_tva_env_level1_slider_changed(self, value: int):
        """Handle TVA Env Level 1 change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVA_ENV_LEVEL_1.value[0],
                value=value,
            )
            print(f"TVA Env Level 1 changed to {value}")

    def _on_tva_env_level2_slider_changed(self, value: int):
        """Handle TVA Env Level 2 change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVA_ENV_LEVEL_2.value[0],
                value=value,
            )
            print(f"TVA Env Level 2 changed to {value}")

    def _on_tva_env_level3_slider_changed(self, value: int):
        """Handle TVA Env Level 3 change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVA_ENV_LEVEL_3.value[0],
                value=value,
            )
            print(f"TVA Env Level 3 changed to {value}")

    def _on_tvf_filter_type_combo_changed(self, index: int):
        """Handle TVF Filter Type change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVF_FILTER_TYPE.value[0],
                value=index,
            )
            print(f"TVF Filter Type changed to {index}")

    def _on_tvf_cutoff_frequency_slider_changed(self, value: int):
        """Handle TVF Cutoff Frequency change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVF_CUTOFF_FREQUENCY.value[0],
                value=value,
            )
            print(f"TVF Cutoff Frequency changed to {value}")

    def _on_tvf_cutoff_velocity_curve_spin_changed(self, value: int):
        """Handle TVF Cutoff Velocity Curve change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVF_CUTOFF_VELOCITY_CURVE.value[0],
                value=value,
            )
            print(f"TVF Cutoff Velocity Curve changed to {value}")

    def _on_tvf_cutoff_velocity_sens_slider_changed(self, value: int):
        """Handle TVF Cutoff Velocity Sens change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVF_CUTOFF_VELOCITY_SENS.value[0],
                value=value,
            )
            print(f"TVF Cutoff Velocity Sens changed to {value}")

    def _on_tvf_env_depth_slider_changed(self, value: int):
        """Handle TVF Env Depth change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVF_ENV_DEPTH.value[0],
                value=value,
            )
            print(f"TVF Env Depth changed to {value}")

    def _on_tvf_env_velocity_curve_type_spin_changed(self, value: int):
        """Handle TVF Env Velocity Curve Type change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVF_ENV_VELOCITY_CURVE_TYPE.value[0],
                value=value,
            )
            print(f"TVF Env Velocity Curve Type changed to {value}")

    def _on_tvf_env_velocity_sens_slider_changed(self, value: int):
        """Handle TVF Env Velocity Sens change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVF_ENV_VELOCITY_SENS.value[0],
                value=value,
            )
            print(f"TVF Env Velocity Sens changed to {value}")

    def _on_tvf_env_time1_velocity_sens_slider_changed(self, value: int):
        """Handle TVF Env Time 1 Velocity Sens change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVF_ENV_TIME_1_VELOCITY_SENS.value[0],
                value=value,
            )
            print(f"TVF Env Time 1 Velocity Sens changed to {value}")

    def _create_parameter_slider(
        self, param: DrumParameter, label: str = None
    ) -> Slider:
        """Create address slider for address parameter with proper display conversion"""
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val
        slider = Slider(label, display_min, display_max)

        if isinstance(param, DrumParameter) and param in [
            DrumParameter.PARTIAL_FINE_TUNE,
            # Add other bipolar parameters as needed
        ]:
            if self.midi_helper:
                midi_value = self.midi_helper.get_parameter(
                    area=TEMPORARY_TONE_AREA,
                    part=DRUM_KIT_AREA,
                    group=self.partial_address,
                    param=param.address,
                )
                if midi_value is not None:
                    display_value = param.convert_from_midi(midi_value)
                    slider.setValue(display_value)

        # Connect value changed signal
        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))

        # Store control reference
        self.controls[param] = slider
        return slider

    def send_midi_parameter(self, param, value) -> bool:
        """Send MIDI parameter with error handling"""
        if not self.midi_helper:
            logging.debug("No MIDI helper available - parameter change ignored")
            return False
        try:
            # Ensure value is included in the MIDI message
            return self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DRUM_KIT_AREA,
                group=self.partial_address,
                param=param.format_address,
                value=value,  # Make sure this value is being sent
            )
        except Exception as ex:
            logging.error(f"MIDI error setting {param}: {str(ex)}")
            return False

    def _on_parameter_changed(self, param: DrumParameter, display_value: int):
        """Handle parameter value changes from UI controls"""
        try:
            # Convert display value to MIDI value if needed
            if hasattr(param, "convert_from_display"):
                midi_value = param.convert_from_display(display_value)
            else:
                midi_value = param.validate_value(display_value)

            # Send MIDI message
            if not self.send_midi_parameter(param, midi_value):
                logging.warning(f"Failed to send parameter {param.name}")

        except Exception as ex:
            logging.error(f"Error handling parameter {param.name}: {str(ex)}")

    def set_partial_num(self, partial_num: int):
        """Set the current partial number"""
        if 0 <= partial_num < len(DRUM_ADDRESSES):
            self.partial_num = partial_num
        else:
            raise ValueError(f"Invalid partial number: {partial_num}")

    def update_partial_num(self, index: int):
        """Update the partial number based on the current tab index"""
        self.set_partial_num(index)

        # Validate partial_name
        if self.partial_num < 0 or self.partial_num >= len(DRUM_ADDRESSES):
            logging.error(f"Invalid partial number: {self.partial_num}")
            return

        # Get the address for the current partial
        try:
            self.group, self.partial_address = get_address_for_partial(self.partial_num)
            logging.info(
                f"Updated partial number to {self.partial_num}, group: {hex(self.group)}, address: {hex(self.partial_address)}"
            )
            print(
                f"Updated partial number to {self.partial_num}, group: {hex(self.group)}, address: {hex(self.partial_address)}"
            )
        except Exception as e:
            logging.error(
                f"Error getting address for partial {self.partial_num}: {str(e)}"
            )

    def _on_coarse_tune_changed(self, value: int):
        """Handle Coarse Tune parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.COARSE_TUNE.value[0],
            value=value,
            size=1
        )

    def _on_fine_tune_changed(self, value: int):
        """Handle Fine Tune parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.FINE_TUNE.value[0],
            value=value,
            size=1
        )

    def _on_level_changed(self, value: int):
        """Handle Level parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.LEVEL.value[0],
            value=value,
            size=1
        )

    def _on_pan_changed(self, value: int):
        """Handle Pan parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.PAN.value[0],
            value=value,
            size=1
        )

    def _on_cutoff_changed(self, value: int):
        """Handle Cutoff parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.TVF_CUTOFF.value[0],
            value=value,
            size=1
        )

    def _on_resonance_changed(self, value: int):
        """Handle Resonance parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.TVF_RESONANCE.value[0],
            value=value,
            size=1
        )

    def _on_pitch_env_attack_changed(self, value: int):
        """Handle Pitch Envelope Attack parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.PITCH_ENV_ATTACK.value[0],
            value=value,
            size=1
        )

    def _on_pitch_env_decay_changed(self, value: int):
        """Handle Pitch Envelope Decay parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.PITCH_ENV_DECAY.value[0],
            value=value,
            size=1
        )

    def _on_tva_attack_changed(self, value: int):
        """Handle TVA Attack parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.TVA_ATTACK.value[0],
            value=value,
            size=1
        )

    def _on_tva_decay_changed(self, value: int):
        """Handle TVA Decay parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.group,
            param=DrumParameter.TVA_DECAY.value[0],
            value=value,
            size=1
        )
