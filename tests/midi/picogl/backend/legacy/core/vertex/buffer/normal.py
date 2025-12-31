import numpy as np
from OpenGL.GL import glNormalPointer
from OpenGL.raw.GL._types import GL_FLOAT

from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO


class LegacyNormalVBO(LegacyVBO):
    """Specialized Class for Position Buffers"""

    def __init__(self, handle: int = None, data: np.ndarray = None, size: int = 3):
        """constructor"""
        super().__init__(handle=handle, size=size)
        self.data = data
        if data is not None:
            self.set_data(data)
        self.bind()

    def configure(self):
        """Configure attributes specific to position atoms_buffers"""
        glNormalPointer(GL_FLOAT, 0, None)
