"""
Element Buffer Object (EBO) Management for Modern OpenGL Rendering.

This module defines the `ElementBufferObject` class, which encapsulates the
OpenGL element data buffer (also known as an index buffer). It is used to
store indices that OpenGL uses to decide which vertices to draw, allowing
for efficient reuse of vertex data in complex models.

The class handles:
- Creation and deletion of the EBO on the GPU.
- Binding and unbinding of the buffer.
- Storage of element/index data along with configuration parameters.
- Uploading the data to the GPU with `glBufferData`.

Example usage:
==============
>>>ebo = ModernEBO(data=data)
...ebo.bind()
...ebo.set_element_attributes(indices, indices.nbytes)
...ebo.configure()
...ebo.unbind()
"""

import numpy as np
from OpenGL.GL import glBufferData, glGenBuffers
from OpenGL.raw.GL.VERSION.GL_1_5 import (GL_ELEMENT_ARRAY_BUFFER,
                                          GL_STATIC_DRAW)

from picogl.backend.modern.core.vertex.base import VertexBase


class ModernEBO(VertexBase):
    """
    OpenGL element data buffer (also known as an index buffer)
    """

    def __init__(
        self,
        handle: int = None,
        data: np.ndarray = None,
        size: int = 3,
        target: int = GL_ELEMENT_ARRAY_BUFFER,
    ):
        """ """
        if handle is None:
            handle = glGenBuffers(1)
        super().__init__(handle=handle, size=size, data=data, target=target)

    def set_element_attributes(
        self, data: np.ndarray, size: int, dtype: int = GL_STATIC_DRAW
    ):
        """
        set_element_attributes

        :param data: np.ndarray
        :param size: int
        :param dtype: int
        :return: None
        """
        self.data = data
        self.size = size
        self.dtype = dtype

    def configure(self):
        """
        configure

        :return: None
        """
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.size, self.data, self.dtype)
