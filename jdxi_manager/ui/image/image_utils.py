import base64

from PySide6.QtGui import QPixmap


def base64_to_pixmap(base64_str):
    """Convert base64 string to QPixmap"""
    image_data = base64.b64decode(base64_str)
    image = QPixmap()
    image.loadFromData(image_data)
    return image
