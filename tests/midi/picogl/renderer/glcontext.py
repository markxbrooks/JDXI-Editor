"""
GL Context Class
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.backend.modern.core.vertex.array.object import VertexArrayObject


@dataclass
class GLContext:
    """
    Stores dynamic OpenGL-related state (VAO, shader, texture handles, etc.).
    Does NOT store raw vertex data.
    """

    vaos: dict[str, VertexArrayObject] = field(default_factory=dict)
    vertex_array: Optional[VertexArrayObject] = None
    shader: Optional[ShaderProgram] = None
    texture_id: Optional[int] = None
    mvp_matrix: np.ndarray = field(
        default_factory=lambda: np.identity(4, dtype=np.float32)
    )
    model_matrix: np.ndarray = field(
        default_factory=lambda: np.identity(4, dtype=np.float32)
    )
    view: np.ndarray = field(
        default_factory=lambda: np.identity(4, dtype=np.float32)
    )
    eye_np: np.ndarray = field(
        default_factory=lambda: np.identity(3, dtype=np.float32)
    )

    def create_shader_program(self, vertex_source_file: str,
                              fragment_source_file: str,
                              glsl_dir: str | Path | None = None) -> None:
        """
        create_shader_program

        :param vertex_source_file: str
        :param fragment_source_file: str
        :param glsl_dir: str
        :return: None
        """
        self.shader = ShaderProgram(
            vertex_source_file=vertex_source_file,
            fragment_source_file=fragment_source_file,
            glsl_dir=glsl_dir,
        )
