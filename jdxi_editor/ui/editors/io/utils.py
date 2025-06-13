"""
Editor IO Utils
"""


def format_time(seconds: float) -> str:
    """
    Format a time in seconds to a string

    :param seconds: float
    :return: str
    """
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{mins}:{secs:02}"
