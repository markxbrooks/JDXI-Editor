"""
vertex_base.py

This module defines the `VertexBase` class, a foundational abstraction for
OpenGL objects that require explicit binding and unbinding during rendering.

`VertexBase` provides a common interface and context management protocol for derived classes such as
`VertexArrayObject`, `ModernVBO`, and `ModernEBO`.
It ensures consistent handling of OpenGL object lifetimes and usage patterns by enforcing the
implementation of `bind()` and `unbind()` methods.

Features:
- Stores a raw OpenGL object handle (ID)
- Provides `bind()` / `unbind()` interface to be implemented by subclasses
- Supports Python context manager protocol (`with` statement)
- Useful for any OpenGL object that must be bound/unbound during draw calls

Example Usage:
==============
class MyBuffer(VertexBase):
...def bind(self): glBindBuffer(GL_ARRAY_BUFFER, self.handle)
...def unbind(self): glBindBuffer(GL_ARRAY_BUFFER, 0)
...
...with MyBuffer(handle) as buf:
...   # buffer is bound
        ...
...# buffer is unbound

Note:
This base class is abstract and cannot be used directly;
`bind` and `unbind` must be implemented in subclasses.

"""

import ctypes

import numpy as np
from OpenGL.raw.GL._types import GL_FLOAT, GL_UNSIGNED_INT
from OpenGL.raw.GL.VERSION.GL_1_5 import (GL_ARRAY_BUFFER, GL_STATIC_DRAW,
                                          glBindBuffer, glBufferData,
                                          glIsBuffer)
from OpenGL.raw.GL.VERSION.GL_2_0 import (glEnableVertexAttribArray,
                                          glVertexAttribPointer)

from picogl.buffers.abstract import AbstractVertexBuffer


class VertexBase(AbstractVertexBuffer):
    """
    Base class for OpenGL vertex-related buffers (VBO, VAO, EBO).

    This handles:
        - Buffer binding/unbinding
        - Data upload (glBufferData)
        - Vertex attribute configuration
        - Type mapping from NumPy dtype to GL constants
    """

    _GL_TYPE_MAP = {
        np.float32: GL_FLOAT,
        np.uint32: GL_UNSIGNED_INT,
    }

    def __init__(
        self,
        handle: int = None,
        data: np.ndarray = None,
        target: int = GL_ARRAY_BUFFER,
        size: int = 3,
        stride: int = 0,
        dtype: int = GL_FLOAT,
        index: int = None,
        pointer: ctypes.c_void_p = ctypes.c_void_p(0),
    ):
        super().__init__(handle=handle)
        self.index = index
        self.normalized = False
        self.target = target
        self.size = size
        self.stride = stride
        self.dtype = dtype
        self.pointer = pointer
        self.data = data
        self.offset = 0

    # ----------------------------
    # OpenGL binding / unbinding
    # ----------------------------
    def bind(self) -> None:
        """Bind this buffer."""
        glBindBuffer(self.target, self.handle)

    def unbind(self) -> None:
        """Unbind this buffer, ensuring the handle is valid."""
        if not glIsBuffer(self.handle):
            raise RuntimeError(f"Invalid buffer handle: {self.handle}")
        glBindBuffer(self.target, 0)

    def update(self, data: np.ndarray):
        self.data = data
        if data is not None:
            self.set_data(data)

    # ----------------------------
    # Data upload
    # ----------------------------
    def set_data(self, data: np.ndarray, usage: int = GL_STATIC_DRAW) -> None:
        """
        Upload data to the GPU.

        :param data: NumPy array containing buffer data.
        :param usage: GL usage hint (e.g., GL_STATIC_DRAW, GL_DYNAMIC_DRAW).
        """
        if not isinstance(data, np.ndarray):
            raise TypeError(f"Expected np.ndarray, got {type(data).__name__}")
        self.data = data
        self.dtype = self._map_dtype_to_gl(data.dtype.type)
        glBufferData(self.target, data.nbytes, data, usage)

    # ----------------------------
    # Vertex attribute state
    # ----------------------------
    def set_vertex_attributes(
        self,
        index: int,
        data: np.ndarray = None,
        size: int = None,
        normalized: bool = False,
        stride: int = 0,
        offset: int = 0,
        dtype: int = None,
        pointer: ctypes.c_void_p = None,
    ) -> None:
        """
        Set the vertex attribute pointer configuration.

        :param index: Attribute index in the VAO.
        :param data: Optional data array to store alongside attribute info.
        :param size: Number of components per vertex (1-4).
        :param normalized: Whether values should be normalized.
        :param stride: Byte offset between consecutive attributes.
        :param offset: Byte offset of the first attribute.
        :param dtype: GL data type (e.g., GL_FLOAT).
        :param pointer: Offset pointer for glVertexAttribPointer.
        """
        self.index = index
        if data is not None:
            self.data = data
        self.size = size or self.size
        self.normalized = normalized
        self.stride = stride
        self.offset = offset
        self.dtype = dtype or self.dtype
        self.pointer = pointer if pointer is not None else ctypes.c_void_p(0)

    def configure(self) -> None:
        """Enable and configure the vertex attribute array."""
        if self.index is None:
            raise ValueError("Vertex attribute index is not set.")
        glEnableVertexAttribArray(self.index)
        glVertexAttribPointer(
            self.index,
            self.size,
            self.dtype,
            self.normalized,
            self.stride,
            self.pointer,
        )

    # ----------------------------
    # Helpers
    # ----------------------------
    @property
    def index_count(self) -> int:
        """Number of vertices/indices in this buffer."""
        return len(self.data) if self.data is not None else 0

    @classmethod
    def _map_dtype_to_gl(cls, dtype) -> int:
        """Map a NumPy dtype to the corresponding GL constant."""
        return cls._GL_TYPE_MAP.get(dtype, GL_FLOAT)

    # ----------------------------
    # Debug
    # ----------------------------
    def __repr__(self) -> str:
        classname = self.__class__.__name__
        data_preview = repr(self.data)
        if len(data_preview) > 100:
            data_preview = data_preview[:97] + "..."
        return (
            f"{classname}(index={self.index}, handle={self.handle}, pointer={self.pointer}, "
            f"target={self.target}, size={self.size}, stride={self.stride}, offset={self.offset}, "
            f"dtype={self.dtype}, normalized={self.normalized}, data={data_preview})"
        )
