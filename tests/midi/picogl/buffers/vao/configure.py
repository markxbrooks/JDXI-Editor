"""
VAO attribute configuration
"""

from picogl.backend.modern.core.vertex.buffer.object import ModernVBO


def vao_configure_attributes(
    attributes: list[tuple[int, int, int, int, bool, int, int]],
):
    """
    Enable all vertex attributes associated with this VAO.

    :param attributes: A list of tuples where each tuple contains:
        - index (int): The attribute index.
        - vbo_handle (int): The ID of the vertex buffer object.
        - size (int): The number of components per vertex attribute.
        - dtype (str): The data type of each component (e.g., 'float').
        - normalized (bool): Whether fixed-point data values should be normalized.
        - stride (int): The byte offset between consecutive attributes.
        - offset (int): The byte offset of the first component.
    :raises ValueError: If the structure of any attribute tuple is invalid.
    """

    for attribute in attributes:
        if len(attribute) != 7:
            raise ValueError(
                f"Invalid attribute tuple: {attribute}. Expected 7 elements."
            )
        index, vbo, size, dtype, normalized, stride, offset = attribute
        try:
            with ModernVBO(vbo) as vbo_object:
                vbo_object.set_vertex_attributes(
                    index=index,
                    size=size,
                    dtype=dtype,
                    normalized=normalized,
                    stride=stride,
                    offset=offset,
                )
                vbo_object.configure()
        except Exception as ex:
            # Log or re-raise the exception with more context
            raise RuntimeError(
                f"Failed to configure vertex attribute at index {index}"
            ) from ex
