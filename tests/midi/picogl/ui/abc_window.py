"""
ABC Window
"""


from abc import ABC, abstractmethod
from typing import Optional

from OpenGL.GLUT import ( glutMainLoop, glutSwapBuffers)


class AbstractGLWindow(ABC):
    """
    A strict ABC base class for a GLUT/OpenGL window.

    Subclasses must implement:
      - initializeGL
      - paintGL
      - resizeGL
      - on_keyboard
      - on_special_key
      - on_mouse
      - on_mousemove
    """

    def __init__(
        self, width: int = 800, height: int = 480, title: bytes = b"GL Window"
    ):
        self.controller: Optional[object] = None
        self.width = width
        self.height = height
        self.window = None

    @abstractmethod
    def initializeGL(self) -> None:
        """Set up OpenGL state. Must be implemented by subclass."""

    @abstractmethod
    def paintGL(self) -> None:
        """Render the scene. Must be implemented by subclass."""

    @abstractmethod
    def resizeGL(self, width: int, height: int) -> None:
        """Handle window resize. Must be implemented by subclass."""

    def display(self) -> None:
        """Default display path calls paintGL, then swaps buffers"""
        self.paintGL()
        glutSwapBuffers()

    def idle(self) -> None:
        """Optional idle hook (override if needed)."""

    @abstractmethod
    def on_keyboard(self, key, x, y) -> None:
        """Handle ASCII keyboard input. Must be implemented by subclass."""

    @abstractmethod
    def on_special_key(self, key, x, y) -> None:
        """Handle special keys (arrows, function keys). Must be implemented by subclass."""

    @abstractmethod
    def mousePressEvent(self, *args, **kwargs) -> None:
        """Handle mouse button events. Must be implemented by subclass."""

    @abstractmethod
    def mouseMoveEvent(self, *args, **kwargs) -> None:
        """Handle mouse movement events. Must be implemented by subclass."""

    def run(self) -> None:
        glutMainLoop()
