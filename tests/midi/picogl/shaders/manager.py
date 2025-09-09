"""
ShaderManager
=============

Example Usage:
==============
>>>shader_manager = ShaderManager()
...
...# Load all src
...for shader_type_value in ShaderType:
...    shader_manager.load_shader_source_string(shader_type_value)
...
...# Use a shader_manager.current_shader_program
...if shader_manager.use_shader_type(ShaderType.ATOMS):
...    shader_manager.current_shader_program = shader_manager.get(ShaderType.ATOMS)
...    set_common_uniforms(
...        shader_manager.current_shader_program,
...        mvp_matrix=my_mvp_matrix,
...        point_size=15.0,
...        highlight=True,
...        highlight_color=(1.0, 1.0, 0.0)
...    )


File naming convention:
=======================
Ensure GLSL files follow the naming pattern:

atoms_vert.glsl
atoms_frag.glsl
bonds_vert.glsl
bonds_frag.glsl
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Union

import numpy as np
from pyglm import glm

from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.backend.modern.core.uniform.mvp import shader_uniform_set_mvp
from picogl.backend.modern.core.uniform.set_location import \
    set_uniform_name_value
from picogl.logger import Logger as log
from picogl.shaders.compile import compile_shaders
from picogl.shaders.generate import generate_shader_programs
from picogl.shaders.load import load_fragment_and_vertex_for_shader_type
from picogl.shaders.type import ShaderType


@dataclass
class ShaderManager:
    shaders: Dict[ShaderType, ShaderProgram] = field(default_factory=dict)
    fallback_shader: Optional[ShaderProgram] = None
    default_shader_type: ShaderType = ShaderType.DEFAULT
    current_shader_type: ShaderType = ShaderType.DEFAULT
    current_shader: Optional[ShaderProgram] = None
    current_shader_program: Optional[int] = None
    initialized: bool = False
    shader_directory: str = ""
    fallback_shader_directory: str = ""

    def use_shader_program(self, shader_program: ShaderProgram) -> None:
        """
        use_shader_program

        :param shader_program: PicoGLShader
        :return: None
        Bind the given shader shader_program and update current_shader/shader_program ID
        """

        if not shader_program:
            log.error("❌ Cannot bind: shader_program is None or invalid")
            return
        try:
            shader_program.bind()
            self.current_shader = shader_program
            self.current_shader_program = shader_program.program_id()
        except Exception as ex:
            log.error(f"❌ Failed to bind shader shader_program: {ex}")

    def get_shader_type(
        self, shader_type: ShaderType
    ) -> Optional[ShaderProgram | ShaderProgram]:
        """
        Return the shader shader_program for the given ShaderType, loading if necessary.
        """
        if shader_type not in self.shaders:
            self.load_shader(shader_type)
        return self.shaders.get(shader_type)

    def use_shader_type(
        self,
        shader_type: ShaderType,
        mvp_matrix: np.ndarray | glm.mat4 = None,
        zoom_scale: int = None,
    ) -> None:
        """
        use_shader_type

        :param zoom_scale: int
        :param shader_type: ShaderType
        :param mvp_matrix: np.ndarray | glm.mat4 = None
        :return: None
        Load (if needed) and bind the shader of the given type
        """
        self.current_shader = self.get_shader_type(shader_type)
        if self.current_shader:
            self.current_shader_type = shader_type
            self.use_shader_program(self.current_shader)
            if mvp_matrix is not None:
                self.update_mvp_uniform(mvp_matrix=mvp_matrix)
            if zoom_scale is not None:
                if self.current_shader_type == ShaderType.ATOMS:
                    self.set_uniform_value("zoom_scale", zoom_scale)
        else:
            log.error(f"❌ Shader type {shader_type} could not be loaded or bound.")

    def update_mvp_uniform(self, mvp_matrix: np.ndarray | glm.mat4) -> None:
        """
        update_mvp_uniform

        :param mvp_matrix: np.ndarray | glm.mat4:
        :return: None
        """
        shader_uniform_set_mvp(
            shader_program=self.current_shader.program_id(), mvp_matrix=mvp_matrix
        )

    def set_uniform_value(
        self,
        uniform_name: str,
        uniform_value: Union[
            float, int, glm.vec2, glm.vec3, glm.vec4, glm.mat4, np.ndarray
        ],
    ) -> None:
        """
        set_uniform_value

        :param uniform_name: str
        :param uniform_value: Union[float, int, glm.vec2, glm.vec3, glm.vec4, glm.mat4, np.ndarray]
        :return: None
        """
        set_uniform_name_value(
            shader_program=self.current_shader.program_id(),
            uniform_name=uniform_name,
            uniform_value=uniform_value,
        )

    def use_default_shader(self, mvp_matrix: np.ndarray | glm.mat4 = None) -> None:
        """
        use_default_shader

        :param mvp_matrix: np.ndarray | glm.mat4
        :return:
        Bind the default shader type.
        """
        self.use_shader_type(
            shader_type=self.default_shader_type, mvp_matrix=mvp_matrix
        )

    def initialize_shaders(self, shader_dir: str = None):
        """Initialize src and mark GL state as ready."""
        # Load src into the manager
        self.shader_directory = shader_dir

        failed = []
        for shader_number, shader_type in enumerate(ShaderType):
            log.message(
                f"Loading shader type: '{shader_type.value} from {self.shader_directory}'",
                silent=True,
            )
            self.load_shader(shader_type, shader_number)
            if self.shaders[shader_type] is self.fallback_shader:
                failed.append(shader_type)

        if failed:
            log.warning(
                f"⚠️ Shader fallback used for: {', '.join(st.value for st in failed)}"
            )

        self.initialized = True
        log.message("✅ GLState initialized and src loaded (including fallback).")
        self.use_default_shader()
        self.current_shader_program = self.current_shader.program_id()
        self.current_shader.bind()

    def load_shader(self, shader_type: str, shader_number: int) -> None:
        """
        load_shader

        :param shader_type: ShaderType
        :return: None
        """
        try:
            log.message(f"Loading shaders from {self.shader_directory}", silent=True)
            fragment_src, vertex_src = load_fragment_and_vertex_for_shader_type(
                shader_type.value, self.shader_directory
            )
            picogl_shader_program = generate_shader_programs(
                vertex_src, fragment_src, shader_type
            )
            if picogl_shader_program:
                log.message(
                    f"[{shader_number}/{len(ShaderType)}] ✅ Shader type `{shader_type}` compiled and registered"
                )
                self.shaders[shader_type] = picogl_shader_program
            else:
                log.warning(f"⚠️ Falling back for {shader_type}")
                self._ensure_fallback()
                self.shaders[shader_type] = self.fallback_shader
        except Exception as ex:
            log.warning(f"⚠️ Shader load failed for {shader_type}: {ex}")
            self._ensure_fallback()
            self.shaders[shader_type] = self.fallback_shader

    def _ensure_fallback(self):
        """
        _ensure_fallback

        :return: None
        """
        if self.fallback_shader is None:
            try:
                vert, frag = load_fragment_and_vertex_for_shader_type(
                    "fragment", self.shader_directory
                )
                self.fallback_shader = compile_shaders(vert, frag, "fallback")
                log.message(
                    "✅ Fallback shader_manager.current_shader_program compiled"
                )
            except Exception as ex:
                log.error(
                    f"❌ Fallback shader_manager.current_shader_program setup failed: {ex}"
                )

    def get(self, shader_type: ShaderType) -> Optional[ShaderProgram | ShaderProgram]:
        return self.shaders.get(shader_type)

    def release_shaders(self):
        """
        release_shaders

        :return: None
        """
        for key, shader in self.shaders.items():
            try:
                shader.release()
            except (Exception,):
                pass
        self.shaders.clear()
        if self.fallback_shader:
            try:
                self.fallback_shader.release()
            except (Exception,):
                pass
            self.fallback_shader = None
