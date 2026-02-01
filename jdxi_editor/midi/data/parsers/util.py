from jdxi_editor.midi.sysex.sections import SysExSection

COMMON_IGNORED_KEYS = {
    SysExSection.JD_XI_HEADER,
    SysExSection.ADDRESS,
    SysExSection.TEMPORARY_AREA,
    SysExSection.SYNTH_TONE,
    SysExSection.TONE_NAME,
    SysExSection.TONE_NAME_1,
    SysExSection.TONE_NAME_2,
    SysExSection.TONE_NAME_3,
    SysExSection.TONE_NAME_4,
    SysExSection.TONE_NAME_5,
    SysExSection.TONE_NAME_6,
    SysExSection.TONE_NAME_7,
    SysExSection.TONE_NAME_8,
    SysExSection.TONE_NAME_9,
    SysExSection.TONE_NAME_10,
    SysExSection.TONE_NAME_11,
    SysExSection.TONE_NAME_12,
}

OUTBOUND_MESSAGE_IGNORED_KEYS = {
    SysExSection.JD_XI_HEADER,
    SysExSection.ADDRESS,
    SysExSection.TONE_NAME,
    SysExSection.TONE_NAME_1,
    SysExSection.TONE_NAME_2,
    SysExSection.TONE_NAME_3,
    SysExSection.TONE_NAME_4,
    SysExSection.TONE_NAME_5,
    SysExSection.TONE_NAME_6,
    SysExSection.TONE_NAME_7,
    SysExSection.TONE_NAME_8,
    SysExSection.TONE_NAME_9,
    SysExSection.TONE_NAME_10,
    SysExSection.TONE_NAME_11,
    SysExSection.TONE_NAME_12,
}
