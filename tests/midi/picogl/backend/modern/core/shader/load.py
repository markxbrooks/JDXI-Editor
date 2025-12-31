from functools import wraps

from picogl.shaders.type import ShaderType


def load_shader(shader_type: ShaderType):
    """
    A decorator to load the shader and set the MVP matrix.

    Args:
        shader_type (ShaderType): The type of shader to use.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract the necessary arguments
            shader_manager = kwargs.get("shader_manager")
            mvp_matrix = kwargs.get("mvp_matrix")
            zoom_scale = kwargs.get("zoom_scale")

            if not shader_manager or not mvp_matrix:
                raise ValueError(
                    "shader_manager and mvp_matrix must be provided as keyword arguments."
                )

            # Use the shader and set the MVP matrix
            shader_manager.use_shader_type(
                shader_type=shader_type, mvp_matrix=mvp_matrix, zoom_scale=zoom_scale
            )

            # Execute the original function
            return func(*args, **kwargs)

        return wrapper

    return decorator
