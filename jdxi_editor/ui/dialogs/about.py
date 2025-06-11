"""
btk_dialog for about box
"""

import os
from typing import Optional
from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QDialogButtonBox,
    QGroupBox,
    QWidget,
)
from PySide6.QtCore import QSettings, QRect

from jdxi_editor.project import __version__, __program__, __package_name__
from jdxi_editor.resources import resource_path
from jdxi_editor.jdxi.style import JDXiStyle


class UiAboutDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.version_label = None
        self.settings = QSettings("mabsoft", __package_name__)

    def setup_ui(self, parent: QWidget = None) -> None:
        """
        setup_ui

        :param parent: QWidget
        :return: None
        """
        self.resize(508, 300)
        self.setWindowTitle(f"about {__program__}")
        self.setStyleSheet(JDXiStyle.SPLASH_SCREEN + JDXiStyle.CREDITS_LABEL_STYLE)
        main_layout = QVBoxLayout(self)
        group_box_layout = QVBoxLayout(self)
        group_box = QGroupBox(__program__)
        group_box_layout.addWidget(group_box)
        image_layout = QVBoxLayout(self)
        group_box.setLayout(image_layout)
        image_label = QLabel()
        image_pixmap = QPixmap(
            resource_path(os.path.join("resources", "jdxi_cartoon_600.png"))
        )

        # Scale the pixmap to 200x200 while keeping aspect ratio
        scaled_pixmap = image_pixmap.scaled(
            200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        image_label.setPixmap(scaled_pixmap)
        image_label.setFixedSize(200, 200)  # Optional: set the label size as well
        image_label.setAlignment(Qt.AlignHCenter)
        image_layout.addWidget(image_label, alignment=Qt.AlignHCenter)

        version_label = QLabel()
        version_label.setText(f"{__program__}\nversion:\t{__version__}")
        image_layout.addWidget(version_label)

        button_box = QDialogButtonBox(self)
        button_box.setGeometry(QRect(150, 250, 341, 32))
        button_box.setOrientation(Qt.Horizontal)
        button_box.setStandardButtons(QDialogButtonBox.Ok)
        button_box.setObjectName("buttonBox")
        button_box.accepted.connect(self.close)
        credits_label = QLabel()
        credits_label.setTextFormat(Qt.RichText)
        credits_label.setText(
            "<br><b>Credits:</b><br>"
            "This application uses the following libraries:<br>"
            "&bull; <a style='color: blue' href='https://mido.readthedocs.io/'>Mido</a> – MIDI message parsing and sending<br>"
            "&bull; <a style='color: blue' href='https://www.music.mcgill.ca/~gary/rtmidi/'>RtMidi</a> – Low-level MIDI communication<br>"
            "&bull; <a style='color: blue' href='https://www.qt.io/'>Qt</a> – Cross-platform application framework<br>"
            "Source code available on <a style='color: blue' href='https://github.com/markxbrooks/jdxi-editor'>GitHub</a><br>"
            "Licensed under the <a style='color: blue' href='https://opensource.org/licenses/MIT'>MIT License</a><br>"
            "'Roland' and 'JD-Xi' are Trademarks of the Roland Corporation <br> in the United States and/or other countries<br>"
        )
        credits_label.setStyleSheet(
            JDXiStyle.CREDITS_LABEL_STYLE
        )
        credits_label.setOpenExternalLinks(True)
        credits_label.setAlignment(Qt.AlignCenter)
        divider = QLabel("<hr>")
        group_box_layout.addWidget(divider)
        group_box_layout.addWidget(credits_label)
        main_layout.addLayout(group_box_layout)
        group_box_layout.addWidget(button_box)

        # show all the widgets
        self.show()
