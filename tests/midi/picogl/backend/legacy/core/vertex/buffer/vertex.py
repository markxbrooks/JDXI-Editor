import ctypes

import numpy as np
from OpenGL.GL import *

from picogl.backend.modern.core.vertex.base import VertexBase


class LegacyVBO(VertexBase):
    """Legacy OpenGL Vertex Buffer Object (VBO) or Element Buffer Object (EBO)."""

    def __init__(
        self,
        handle: int = None,
        data: np.ndarray = None,
        target: int = GL_ARRAY_BUFFER,
        configure: bool = True,
        size: int = 3,
        stride: int = 0,
        dtype: int = GL_FLOAT,
        pointer: ctypes.c_void_p = ctypes.c_void_p(0),
    ):
        if handle is None:
            handle = glGenBuffers(1)

        super().__init__(
            handle=handle,
            data=data,
            target=target,
            size=size,
            stride=stride,
            dtype=dtype,
            pointer=pointer,
        )

        if data is not None:
            self.set_data(data)

        self.bind()
        if configure and type(self) is not LegacyVBO:
            self.configure()

    # Context manager for "with" usage
    def __enter__(self):
        self.bind()
        self.configure()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.unbind()

    def set_data(self, data: np.ndarray, usage: int = GL_STATIC_DRAW) -> None:
        """
        set_data
        :param data:
        :param usage:
        :return: None

        Upload data, binding/unbinding around the call.
        """
        self.data = data
        self.dtype = self._map_dtype_to_gl(data.dtype.type)
        self.bind()
        glBufferData(self.target, data.nbytes, data, usage)
        self.unbind()

    def configure(self):
        """Configure the buffer (must be implemented in subclass)."""
        raise NotImplementedError("Subclasses must implement configure()!")

    def draw(
        self, index_count: int, index_type: int = GL_UNSIGNED_INT, mode: int = GL_LINES
    ):
        """Draw call (must be implemented in subclass)."""
        raise NotImplementedError("To be implemented in subclass")
