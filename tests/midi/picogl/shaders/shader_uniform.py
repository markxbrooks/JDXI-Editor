from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Sequence, Union

import numpy as np


class UniformKind(Enum):
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    VEC2 = "vec2"
    VEC3 = "vec3"
    VEC4 = "vec4"
    MAT3 = "mat3"
    MAT4 = "mat4"


@dataclass
class ShaderUniform:
    name: str
    location: int
    value: Union[int, float, Sequence[float], np.ndarray, bool, None] = None
    uniform_type: Optional[UniformKind] = None

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("name must be a non-empty string")
        if not isinstance(self.location, int) or self.location < -1:
            raise ValueError("location must be an int >= -1")

        if self.uniform_type is None and self.value is not None:
            self.uniform_type = self.infer_type(self.value)

    @staticmethod
    def infer_type(v: Any) -> UniformKind:
        # Basic Python types
        if isinstance(v, bool):
            return UniformKind.BOOL
        if isinstance(v, int):
            return UniformKind.INT
        if isinstance(v, float):
            return UniformKind.FLOAT

        # Sequences
        if isinstance(v, (list, tuple)):
            l = len(v)
            if l == 2:
                return UniformKind.VEC2
            if l == 3:
                return UniformKind.VEC3
            if l == 4:
                return UniformKind.VEC4

        # NumPy arrays
        if isinstance(v, np.ndarray):
            if v.ndim == 1:
                l = v.shape[0]
                if l == 2:
                    return UniformKind.VEC2
                if l == 3:
                    return UniformKind.VEC3
                if l == 4:
                    return UniformKind.VEC4
            elif v.ndim == 2:
                if v.shape == (3, 3):
                    return UniformKind.MAT3
                if v.shape == (4, 4):
                    return UniformKind.MAT4

        raise ValueError(f"Cannot infer uniform type from value: {v!r}")

    def upload(self, gl_module=None) -> None:
        """
        Upload the current value to the bound GL program using PyOpenGL-like calls.
        If location < 0 (GL returns -1 when not found/used), this is a no-op.

        - gl_module: optional OpenGL.GL-like module. If None, will try to import PyOpenGL
          (from OpenGL import GL as GL) at call time.
        """
        # Resolve GL module (PyOpenGL)
        if gl_module is None:
            try:
                from OpenGL import GL as gl
            except Exception as e:
                raise RuntimeError(
                    "PyOpenGL is required to upload uniforms (pass gl_module or install PyOpenGL)"
                ) from e
        else:
            gl = gl_module

        if self.location < 0:
            # Uniform not active; skip uploading.
            return

        t = self.uniform_type
        v = self.value

        if t == UniformKind.FLOAT:
            gl.glUniform1f(self.location, float(v))
        elif t == UniformKind.INT:
            gl.glUniform1i(self.location, int(v))
        elif t == UniformKind.BOOL:
            gl.glUniform1i(self.location, int(bool(v)))
        elif t == UniformKind.VEC2:
            arr = np.asarray(v, dtype=np.float32)
            gl.glUniform2f(self.location, float(arr[0]), float(arr[1]))
        elif t == UniformKind.VEC3:
            arr = np.asarray(v, dtype=np.float32)
            gl.glUniform3f(self.location, float(arr[0]), float(arr[1]), float(arr[2]))
        elif t == UniformKind.VEC4:
            arr = np.asarray(v, dtype=np.float32)
            gl.glUniform4f(
                self.location,
                float(arr[0]),
                float(arr[1]),
                float(arr[2]),
                float(arr[3]),
            )
        elif t == UniformKind.MAT3:
            mat = np.asarray(v, dtype=np.float32)
            if mat.shape == (3, 3):
                gl.glUniformMatrix3fv(self.location, 1, gl.GL_FALSE, mat)
            elif mat.size == 9:
                gl.glUniformMatrix3fv(
                    self.location, 1, gl.GL_FALSE, mat.reshape((3, 3))
                )
            else:
                raise ValueError("mat3 must be a 3x3 matrix or a 9-element vector")
        elif t == UniformKind.MAT4:
            mat = np.asarray(v, dtype=np.float32)
            if mat.shape == (4, 4):
                gl.glUniformMatrix4fv(self.location, 1, gl.GL_FALSE, mat)
            elif mat.size == 16:
                gl.glUniformMatrix4fv(
                    self.location, 1, gl.GL_FALSE, mat.reshape((4, 4))
                )
            else:
                raise ValueError("mat4 must be a 4x4 matrix or a 16-element vector")
        else:
            raise ValueError(f"Unsupported uniform type: {t}")

    def __str__(self) -> str:
        return f"ShaderUniform(name={self.name!r}, location={self.location}, type={self.uniform_type}, value={self.value})"
