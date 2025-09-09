"""Modern VBO"""

import numpy as np
from OpenGL.GL import glGenBuffers
from OpenGL.raw.GL.VERSION.GL_1_5 import GL_ARRAY_BUFFER

from picogl.backend.modern.core.vertex.base import VertexBase


class ModernVBO(VertexBase):
    """Vertex Buffer Object"""

    def __init__(
        self,
        handle: int = None,
        data: np.ndarray = None,
        size: int = 3,
        target: int = GL_ARRAY_BUFFER,
        index: int = None,
    ):
        """ """
        if handle is None:
            handle = glGenBuffers(1)
        super().__init__(
            handle=handle, size=size, data=data, target=target, index=index
        )
