"""
GLBase Qt Widget
"""
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from OpenGL.GL import glGetIntegerv
from OpenGL.raw.GL.ARB.viewport_array import GL_VIEWPORT
from OpenGL.raw.GL.VERSION.GL_1_0 import glViewport, GL_MODELVIEW, glLoadIdentity
from OpenGL.raw.GLU import gluPerspective
from PySide6.QtGui import QMouseEvent, QOpenGLFunctions, Qt, QWheelEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QWidget

from picogl.backend.legacy.core.camera.lighting import set_background_color
from picogl.backend.legacy.core.camera.matrices.setup import setup_matrices
from picogl.backend.legacy.core.camera.matrix import update_camera_matrix
from picogl.backend.legacy.core.camera.setup import calculate_aspect
from picogl.error import check_errors
from picogl.frame import prepare_viewport
from picogl.logger import Logger as log
from picogl.utils.gl_init import execute_gl_tasks, initialize_gl_list


@dataclass
class MvpParameters:
    """ MVP Parameters """
    rotation_x = None
    rotation_y = None
    pan_x = None
    pan_y = None

@dataclass
class CameraParameters:
    """ camera parameters"""
    rotation_x_axis = None
    rotation_y_axis = None
    rotation_z_axis = None
    translation_x_axis = None
    translation_y_axis = None
    translation_zoom = None
    rotation: np.ndarray = field(
        default_factory=lambda: np.array([0.0, 0.0, 0.0], dtype=np.float32)
    )  # x, y, z
    translation: np.ndarray = field(
        default_factory=lambda: np.array([0.0, 0.0], dtype=np.float32)
    )  # x_pan, y_pan
    # zoom: CameraParameterZoom = field(default_factory=CameraParameterZoom)

class GLBase(QOpenGLWidget, QOpenGLFunctions):
    """
    OpenGL Qt Widget
    """

    def __init__(self, parent: QWidget = None, gl_use_legacy: bool = True):
        """
        constructor

        :param parent: QWidget
        """
        super().__init__(parent)
        self.aspect_ratio = None
        self.gl_use_legacy = gl_use_legacy
        self.last_mouse_pos = None
        self.zoom_value = None
        self.mvp_parameters = MvpParameters()
        self.camera_parameters = CameraParameters()

    def initializeGL(self):
        """
        initializeGL

        Initializes the OpenGL rendering context for this widget.

        This includes:
        - Enabling depth testing and multisampling
        - Configuring blending for transparency
        - Initializing lighting and material properties
        - Setting the viewport to match widget size
        - Clearing any legacy buffer state

        Called automatically by Qt when the GL context is first created.
        """
        # Viewport setup
        glViewport(0, 0, self.width(), self.height())
        execute_gl_tasks(initialize_gl_list)

    def resizeGL(self, w: int, h: int) -> None:
        """
        resizeGL(w, h)

        Handles resizing the OpenGL viewport and updates the projection matrix.

        :param w: int - New width of the OpenGL widget
        :param h: int - New height of the OpenGL widget
        """
        if not self.context().isValid():
            log.warning("OpenGL context invalid during resize. Skipping resizeGL.")
            return
        # Prevent division by zero
        h = max(h, 1)
        # Update viewport
        glViewport(0, 0, w, h)
        self.aspect_ratio = calculate_aspect(h, w)
        gluPerspective(45.0, self.aspect_ratio, 1.0, 1000.0)
        setup_matrices(self.aspect_ratio)
        # Return to modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Update camera matrix using legacy pipeline
        """update_camera_matrix(
            translation=self.camera_parameters.translation,
            rotation=self.camera_parameters.rotation,
            zoom_value=self.camera_parameters.zoom.value,
        )"""
        log.message(
            f"✅ Resized OpenGL viewport to {w}x{h}, aspect {self.aspect_ratio:.2f}"
        )

    def update_mvp(self) -> None:
        """Update model-view-projection matrix."""

    def paintGL(self):
        """
        paintGL

        :return: None
        OpenGL rendering entry point. Calls the appropriate rendering method based g.
        Modern OpenGL rendering entry point.
        """
        check_errors()
        width, height = self.width(), self.height()
        prepare_viewport(width, height)
        set_background_color(show_white_background=False)  # Then set visuals
        check_errors()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        mousePressEvent

        :param event: QMouseEvent
        Handle mouse press events, including atom picking and coordinate un-projection.
        """
        # log.message("Mouse press")
        self.last_mouse_pos = event.position()

        if event.button() != Qt.LeftButton:
            return

        x, y = event.x(), event.y()
        log.message(f"Clicked position: x={x}, y={y}")

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        mouseMoveEvent

        :param event: QMouseEvent
        Handle mouse movement for X/Y axis rotation.
        """
        if self.last_mouse_pos is None:
            return
        delta = event.position() - self.last_mouse_pos
        buttons = event.buttons()

        if buttons & Qt.LeftButton:
            self.mvp_parameters.rotation_x += delta.x() * 0.5
            self.mvp_parameters.rotation_y += delta.y() * 0.5
        elif buttons & Qt.RightButton:
            self.mvp_parameters.pan_x += delta.x() * 0.01
            self.mvp_parameters.pan_y -= delta.y() * 0.01

        dx = event.position().x() - self.last_mouse_pos.x()
        dy = event.position().y() - self.last_mouse_pos.y()

        self._apply_camera_rotation(dx, dy)
        self.last_mouse_pos = event.position()
        self.update_mvp()
        self.update()

        self._emit_rotation_feedback()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        wheelEvent

        :param event: QWheelEvent
        :return: None
        Sets zoom level
        """
        delta = event.angleDelta().y()
        step = 5  # You can adjust sensitivity
        new_val = (
            self.zoom_value - step if delta > 0 else self.zoom_value + step
        )  # Negative zoom increases
        log.message(f"zoom level: {new_val}", silent=True)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        mouseReleaseEvent

        :param event: QMouseEvent
        :return: None
        """
        log.parameter("event", event)
        self.last_mouse_pos = None

    def _compute_clicked_position(
        self, x: int, y: int, z: int, viewport: np.ndarray
    ) -> Optional[np.ndarray]:
        """
        _compute_clicked_position

        :param x: int
        :param y: int
        :param z: int
        :param viewport: np.ndarray
        :return: np.ndarray or None
        """

        raise NotImplementedError("Should be implemented in subclass")

    def _get_viewport(self) -> np.ndarray:
        """
        _get_viewport

        :return: np.ndarray: Array containing viewport dimensions.
        Retrieve the current OpenGL viewport dimensions.
        """
        viewport = np.zeros(4, dtype=np.int32)
        glGetIntegerv(GL_VIEWPORT, viewport)
        return viewport

    def _apply_camera_rotation(self,
                               dx: float,
                               dy: float) -> None:
        """
        _apply_camera_rotation

        :param dx: float
        :param dy: float
        :return: None
        Apply delta rotation based on mouse movement
        """
        self.camera_parameter.rotation_x_axis += dy * 0.5
        self.camera_parameter.rotation_y_axis += dx * 0.5
