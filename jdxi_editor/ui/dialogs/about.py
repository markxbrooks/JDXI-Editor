"""
btk_dialog for about biotoolkit
"""
import os
from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QGroupBox
from PySide6.QtCore import QSettings, QRect

from jdxi_editor.project import __version__, __program__

from jdxi_editor.resources import resource_path
from jdxi_editor.ui.style import JDXIStyle


class UiAboutDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.version_label = None
        self.settings = QSettings('mabsoft', 'jdxi_editor')

    def setup_ui(self, parent=None):
        """
        setup_ui
        :param parent: QWidget
        :return: None
        """
        self.resize(508, 300)
        self.setWindowTitle(f"about {__program__}")
        self.setStyleSheet(JDXIStyle.SPLASH_SCREEN)
        main_layout = QVBoxLayout(self)
        group_box_layout = QVBoxLayout(self)
        group_box = QGroupBox("JDXI Editor")
        group_box_layout.addWidget(group_box)
        image_layout = QVBoxLayout(self)
        group_box.setLayout(image_layout)
        image_label = QLabel()
        image_pixmap = QPixmap(resource_path(os.path.join('resources', 'jdxi_cartoon_600.png')))

        # Scale the pixmap to 200x200 while keeping aspect ratio
        scaled_pixmap = image_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)

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

        main_layout.addLayout(group_box_layout)
        group_box_layout.addWidget(button_box)

        # show all the widgets
        self.show()


