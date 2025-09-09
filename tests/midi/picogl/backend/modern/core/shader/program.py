from pathlib import Path

from OpenGL import GL as gl

from picogl.backend.modern.core.shader.compile import compile_shader
from picogl.backend.modern.core.shader.helpers import (log_gl_error,
                                                       read_shader_source)
from picogl.backend.modern.core.uniform.location_value import \
    set_uniform_location_value
from picogl.logger import Logger as log
from picogl.shaders.uniform import get_uniform_location


class ShaderProgram:
    """OpenGL Shader program manager for vertex and fragment shaders."""

    def __init__(
        self,
        shader_name: str = None,
        vertex_source_file: str = None,
        fragment_source_file: str = None,
        glsl_dir: str | Path | None = None,
    ):
        """constructor"""
        self.shader_name = shader_name
        self.vertex_source_file = vertex_source_file
        self.fragment_source_file = fragment_source_file
        self.base_dir = glsl_dir
        self.vertex_shader = None
        self.fragment_shader = None
        self.program = None
        self.uniforms = {}

        if vertex_source_file is not None and vertex_source_file is not None:
            self.init_shader_from_glsl_files(
                vertex_source_file=vertex_source_file,
                fragment_source_file=fragment_source_file,
                glsl_dir=glsl_dir,
            )

    def __str__(self):
        return f"PicoGLShader(name={self.shader_name}, program={self.program})"

    def __enter__(self):
        self.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def program_id(self):
        return self.program

    def init_shader_from_glsl_files(
        self, vertex_source_file: str, fragment_source_file: str, glsl_dir: str | Path | None = None
    ) -> None:
        """
        init_shader_from_glsl_files

        :param glsl_dir: directory containing vertex shaders
        :param vertex_source_file: list of paths to vertex shaders
        :param fragment_source_file: list of paths to fragment shaders
        :return: None
        """
        vertex_sources = read_shader_source(vertex_source_file, glsl_dir=glsl_dir)
        fragment_sources = read_shader_source(fragment_source_file, glsl_dir=glsl_dir)
        self.init_shader_from_glsl(vertex_sources, fragment_sources)

    def init_shader_from_glsl(self, vertex_source: str, fragment_source: str) -> None:
        """
        init_shader_from_glsl

        :param vertex_source: list of paths to vertex shaders
        :param fragment_source: list of paths to fragment shaders
        :return: None
        """
        self.init_shader(vertex_source, fragment_source)

    def init_shader(self, vertex_source: str, fragment_source: str):
        """
        init_shader

        :param vertex_source: list of paths to vertex shaders
        :param fragment_source: list of paths to fragment shaders
        :return: None

        Create, compile, and link shaders into a program.
        """
        self.create_shader_program()
        log.parameter("self.program", self.program, silent=True)
        log.parameter("vertex_source", vertex_source, silent=True)
        log.parameter("fragment_source", fragment_source, silent=True)
        self.vertex_shader = compile_shader(
            self.program, gl.GL_VERTEX_SHADER, vertex_source
        )
        self.fragment_shader = compile_shader(
            self.program, gl.GL_FRAGMENT_SHADER, fragment_source
        )
        self.link_shader_program()

    def uniform(self, name: str, value):
        """
        uniform

        :param name: str - uniform name
        :param value: value to set (float, int, vec2, vec3, vec4, mat4, or np.ndarray)
        :return: self - for chaining
        Set uniform value (auto-detect type)
        """
        loc = self.uniforms.get(name) or self.get_uniform_location(name)
        self.uniforms[name] = loc
        set_uniform_location_value(loc, value)
        return self  # allow chaining

    def create_shader_program(self):
        """
        create_shader_program
        """
        self.program = gl.glCreateProgram()
        log.message(f"Created shader program {self.program}", silent=True)
        log_gl_error()

    def link_shader_program(self):
        """
        link_shader_program
        """
        log.message("Linking shader program...", silent=True)
        gl.glLinkProgram(self.program)
        if gl.GL_TRUE != gl.glGetProgramiv(self.program, gl.GL_LINK_STATUS):
            err = gl.glGetProgramInfoLog(self.program)
            raise RuntimeError(f"Shader link failed: {err}")
        log_gl_error()

    def get_uniform_location(self, uniform_name):
        """get_uniform_location"""
        mvp_id = get_uniform_location(
            shader_program=self.program, uniform_name=uniform_name
        )
        return mvp_id

    def begin(self):
        """begin"""
        gl.glUseProgram(self.program)
        log_gl_error()

    def end(self):
        """end"""
        gl.glUseProgram(0)

    def bind(self):
        """begin"""
        gl.glUseProgram(self.program)
        log_gl_error()

    def unbind(self):
        gl.glUseProgram(0)

    def release(self):
        gl.glUseProgram(0)
