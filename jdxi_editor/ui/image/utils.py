"""
Module: base64_image_converter
==============================

This module provides a utility function for converting a Base64-encoded image string into a QPixmap.

Functions:
----------
- base64_to_pixmap(base64_str: str) -> QPixmap
    Decodes a Base64 string into a QPixmap image.

Dependencies:
-------------
- base64 (Standard Library)
- PySide6.QtGui (QPixmap)

Usage:
------
This module is useful for handling image data stored in Base64 format, such as images transmitted over networks
or embedded in JSON responses.

Example:
--------
>>> from base64_image_converter import base64_to_pixmap
>>> base64_string = "iVBORw0KGgoAAAANSUhEUgAA..."
>>> pixmap = base64_to_pixmap(base64_string)
"""

import base64

from PySide6.QtGui import QPixmap


def base64_to_pixmap(base64_str: str = None) -> QPixmap:
    """
    Convert a Base64-encoded string into a QPixmap object.

    :param base64_str: Base64 string representing an image.
    :type base64_str: str
    :return: Decoded image as a QPixmap.
    :rtype: QPixmap

    :raises ValueError: If the Base64 string is invalid or cannot be decoded.

    Example:
    --------
    >>> pixmap = base64_to_pixmap("iVBORw0KGgoAAAANSUhEUgAA...")
    >>> isinstance(pixmap, QPixmap)
    True
    """
    image_data = base64.b64decode(base64_str)
    image = QPixmap()
    image.loadFromData(image_data)
    return image
