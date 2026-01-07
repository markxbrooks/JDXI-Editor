"""
Map range

Convert value to range
"""


def map_range(
    value: int,
    in_min: int = -100,
    in_max: int = 100,
    out_min: int = 54,
    out_max: int = 74,
) -> int:
    """
    Map range
    Convert value to range
    :param value: int, float
    :param in_min: int
    :param in_max: int
    :param out_min: int
    :param out_max: int
    :return: int
    """
    return int(out_min + (value - in_min) * (out_max - out_min) / (in_max - in_min))
