from pyglm import glm
from OpenGL.GL import *
from typing import Optional

from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.renderer import RendererBase


class UvRenderer(RendererBase):
    """
    2D UV Renderer that draws a mesh using UV coordinates and indices.
    Follows the RendererBase interface.
    """

    def __init__(self, parent: object = None,
                 vertex_shader_file: str = "glsl/utils/uv2d/vertex.glsl",
                 fragment_shader_file: str = "glsl/utils/uv2d/fragment.glsl"):
        super().__init__(parent)
        self.uv_buffer: Optional[int] = None
        self.indices_buffer: Optional[int] = None
        self.index_count: int = 0
        self.shader: Optional[ShaderProgram] = ShaderProgram(
            vertex_source_file=vertex_shader_file,
            fragment_source_file=fragment_shader_file
        )

    def initialize(self):
        """
        Initialize OpenGL resources. Overrides RendererBase.initialize().
        """
        if self.initialized:
            return

        # Any additional initialization logic can go here
        self.initialized = True

    def initialize_buffers(self, uv_buffer: int, indices_buffer: int, index_count: int) -> None:
        """
        Bind the UV and index buffers to the renderer.

        :param uv_buffer: OpenGL buffer ID containing UVs
        :param indices_buffer: OpenGL buffer ID containing indices
        :param index_count: Number of indices to draw
        """
        if not all(isinstance(x, int) for x in (uv_buffer, indices_buffer, index_count)):
            raise ValueError("uv_buffer, indices_buffer, and index_count must be integers")

        self.uv_buffer = uv_buffer
        self.indices_buffer = indices_buffer
        self.index_count = index_count

    def _draw_model(self) -> None:
        """
        Draw the UV mesh. Called by RendererBase.render().
        """
        if self.uv_buffer is None or self.indices_buffer is None or self.index_count == 0:
            # Nothing to draw
            return

        # Save previous polygon mode
        prev_mode = glGetIntegerv(GL_POLYGON_MODE)
        prev_front_mode, prev_back_mode = prev_mode[0], prev_mode[1]

        with self.shader:
            # Assume shader attribute location 0 for UVs
            uv_loc = 0  # Alternatively, query dynamically with glGetAttribLocation
            glEnableVertexAttribArray(uv_loc)
            glBindBuffer(GL_ARRAY_BUFFER, self.uv_buffer)
            glVertexAttribPointer(uv_loc, 2, GL_FLOAT, GL_FALSE, 0, None)

            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indices_buffer)

            # Wireframe rendering
            glPolygonMode(GL_FRONT, GL_LINE)
            glPolygonMode(GL_BACK, GL_LINE)

            glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_SHORT, None)

            glDisableVertexAttribArray(uv_loc)

        # Restore previous polygon mode
        glPolygonMode(GL_FRONT, prev_front_mode)
        glPolygonMode(GL_BACK, prev_back_mode)

