import numpy as np
from OpenGL.GL import glDrawElements, glVertexPointer
from OpenGL.raw.GL._types import GL_BYTE, GL_FLOAT, GL_INT, GL_SHORT
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_TRIANGLES, GL_UNSIGNED_INT
from OpenGL.raw.GL.VERSION.GL_1_1 import (GL_DOUBLE, GL_VERTEX_ARRAY,
                                          glEnableClientState)
from OpenGL.raw.GL.VERSION.GL_1_5 import GL_ARRAY_BUFFER

from picogl.backend.legacy.core.vertex.buffer.client_states import \
    legacy_client_states
from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO


class LegacyPositionVBO(LegacyVBO):
    """
    OpenGL buffer class specialized for storing and managing position data,
    commonly used for rendering ribbons_legacy-like geometry.

    Inherits from LegacyVBO and adds behavior specific to position data,
    such as setting up the vertex pointer and handling data uploads.
    """

    def __init__(
        self,
        handle: int = None,
        data: np.ndarray = None,
        size: int = 3,
        target: int = GL_ARRAY_BUFFER,
    ):
        """constructor"""
        super().__init__(handle=handle, size=size, data=data, target=target)
        self.size = size
        self.data = data
        if data is not None:
            self.set_data(data)
        self.bind()

    def draw(
        self,
        index_count: int = None,
        index_type: int = GL_UNSIGNED_INT,
        mode: int = GL_TRIANGLES,
    ):
        """
        draw

        :param index_count: int
        :param index_type: int e.g. GL_UNSIGNED_INT
        :param mode: int e.g. GL_LINES
        :param pointer: int
        :return: None
        """
        if not index_count or index_count is None:
            index_count = self.index_count
        with legacy_client_states(GL_VERTEX_ARRAY):
            glDrawElements(mode, index_count, index_type, self.pointer)

    def configure(self):
        """
        Configure the vertex pointer for position buffer.
        """
        self.bind()

        # Validate
        if self.dtype not in (GL_FLOAT, GL_DOUBLE, GL_INT, GL_SHORT, GL_BYTE):
            raise ValueError("Unsupported GL data type.")

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(self.size, self.dtype, self.stride, self.pointer)

        self.unbind()
