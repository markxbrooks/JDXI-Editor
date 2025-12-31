""" Texture Renderer class """
import os
from pathlib import Path

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_TRIANGLES

from examples import g_uv_buffer_data
from picogl.utils.loader.texture import TextureLoader
from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
from picogl.logger import Logger as log
from picogl.renderer import GLContext, MeshData, RendererBase
from picogl.utils.gl_init import execute_gl_tasks, paint_gl_list
from picogl.utils.texture import bind_texture_array


class TextureRenderer(RendererBase):
    """Basic renderer class"""

    def __init__(self, context: GLContext, data: MeshData, base_dir: str = None, glsl_dir: str = None):
        super().__init__()
        self.texture_full_path = None
        self.resource_full_path = None
        self.texture = None
        self.context = context
        self.data = data
        self.data.vertex_count = len(self.data.vbo.flatten()) // 3
        self.show_model = True
        self.base_dir = base_dir
        self.base_path = Path(base_dir)
        self.glsl_dir = glsl_dir

        self.initialize_textures()

    def initialize_shaders(self):
        """Load and compile shaders."""
        log.message("Loading shaders...")
        if not self.context:
            self.context = GLContext()
        self.context.create_shader_program(vertex_source_file="vertex.glsl",
                                           fragment_source_file="fragment.glsl",
                                           glsl_dir=self.glsl_dir)

    def initialize_buffers(self):
        """ Initialize Buffers """
        if self.context.vaos is None:
            self.context.vaos = {}
        self.context.vaos["cube"] = cube_vao = VertexArrayObject()
        cube_vao.add_vbo(index=0, data=self.data.vbo, size=3)
        cube_vao.add_vbo(index=1, data=self.data.uvs, size=2)

    def initialize_textures(self):
        # Build paths
        texture_path = self.get_texture_filename()
        self.texture = texture = TextureLoader(texture_path)
        self.context.texture_id = texture.texture_glid
        if texture.inversed_v_coords:
            for index, _ in enumerate(g_uv_buffer_data):
                if index % 2:
                    g_uv_buffer_data[index] = 1.0 - g_uv_buffer_data[index]

    def get_texture_filename(self):
        """
        get texture filename

        :return: texture filename: str
        """
        self.set_resource_path(self.base_path, "tu02")
        self.set_texture_filename("uvtemplate.tga")
        texture_path = str(self.texture_full_path)
        return texture_path

    def set_texture_filename(self, file_name: str = None):
        """
        set_texture_filename

        :param file_name: str = None
        :return: None
        """
        self.texture_full_path = self.resource_full_path / file_name

    def set_resource_path(self, base_path: str | Path, subdir: str):
        """
        set_resource_path

        :param base_path: str | Path
        :param subdir: str
        """
        self.resource_full_path = base_path.absolute() / "resources" / subdir

    def render(self) -> None:
        """render/dispatcher"""
        if self.show_model:
            self._draw_model()
        # Add more conditions and corresponding draw functions as needed
        self._finalize_render()

    def _draw_model(self):
        """Draw the model_matrix"""
        execute_gl_tasks(paint_gl_list)
        cube_vao = self.context.vaos["cube"]
        shader = self.context.shader
        with shader, cube_vao:
            shader.uniform("mvp_matrix", self.context.mvp_matrix)
            bind_texture_array(self.context.texture_id)
            shader.uniform("myTextureSampler", 0)
            cube_vao.draw(
                mode=GL_TRIANGLES, index_count=self.data.vertex_count
            )

    def _draw_selection(self):
        """Draw selection"""
