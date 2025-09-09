import ctypes

import numpy as np
from OpenGL.GL import glDrawElements
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_LINES, GL_UNSIGNED_INT
from OpenGL.raw.GL.VERSION.GL_1_5 import GL_ELEMENT_ARRAY_BUFFER

from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO


class LegacyEBO(LegacyVBO):
    """Legacy Element Buffer Object (EBO)"""

    def __init__(
        self,
        handle: int = None,
        data: np.ndarray = None,
        target: int = GL_ELEMENT_ARRAY_BUFFER,
        size: int = 3,
    ):
        """constructor"""
        super().__init__(handle=handle, data=data, target=target, size=size)

    def draw(
        self,
        index_count: int,
        index_type: int = GL_UNSIGNED_INT,
        mode: int = GL_LINES,
        pointer: int = ctypes.c_void_p(0),
    ):
        """
        draw

        :param index_count: int
        :param index_type: int e.g. GL_UNSIGNED_INT
        :param mode: int e.g. GL_LINES
        :param pointer: int
        :return: None
        """
        if not index_count:
            index_count = self.index_count
        glDrawElements(mode, index_count, index_type, pointer)

    def configure(self):
        """
        configure
        :return: None
        Element Buffers don't use vertex attributes—nothing to configure."""
        pass
