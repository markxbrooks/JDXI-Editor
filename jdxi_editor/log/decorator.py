from jdxi_editor.log.emoji import LEVEL_EMOJIS


def get_qc_tag(msg: str) -> str:
    """
    get QC emoji etc
    :param msg: str
    :return: str
    """
    msg = f"{msg}".lower()
    if "success rate" in msg:
        return "📊"
    if "updat" in msg or "success" in msg or "passed" in msg:
        return "✅"
    if "fail" in msg or "error" in msg:
        return "❌"
    return " "


def get_midi_tag(msg: str) -> str:
    """
    get Midi emoji etc
    :param msg: str
    :return: str
    """
    msg = f"{msg}".lower()
    if "jdxi" in msg or "jd-xi" in msg:
        return "🎹"
    if "midi" in msg or "sysex" in msg:
        return "🎵"
    return " "


def decorate_log_message(message: str, level: int) -> str:
    """
    Adds emoji decoration to a log message based on its content and log level.
    :param message: The original log message
    :param level: The logging level
    :return: Decorated log message string
    """

    level_emoji_tag = LEVEL_EMOJIS.get(level, "🔔")
    midi_tag = get_midi_tag(message)
    qc_tag = get_qc_tag(message)
    return f"{level_emoji_tag}{qc_tag}{midi_tag} {message}"