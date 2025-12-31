"""
Calculate aspect
"""


def calculate_aspect(h: int, w: int) -> float:
    """
    calculate_aspect

    :param h: int
    :param w: int
    :return: float
    """
    aspect = w / h if h != 0 else 1
    return aspect
