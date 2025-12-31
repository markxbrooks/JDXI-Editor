"""
OpenGL Buffer Cleanup Utilities
===============================

This module provides helper functions for safely deleting OpenGL buffer objects,
including vertex buffer objects (VBOs), vertex array objects (VAOs), and dictionaries
of buffer handles. It ensures proper resource cleanup and avoids memory leaks in
graphics applications.

Dependencies:
-------------
- OpenGL (PyOpenGL)
- picogl.backend.modern.core.vertex.base (for VertexBase type)

Functions:
----------

.. autofunction:: delete_dict_buffers
    Deletes all buffer handles stored in a dictionary and clears the dictionary.

.. autofunction:: delete_buffer_object
    Deletes a buffer object if it is valid and has a non-zero handle.

.. autofunction:: delete_buffer
    Deletes a raw buffer handle if it is valid.

.. autofunction:: delete_vao
    Deletes a vertex array object (VAO) if it is valid.

Usage Example:
--------------

.. code-block:: python

    delete_buffer_object(my_vertex_buffer)
    delete_vao(my_vao_id)
    delete_dict_buffers(buffer_map)
"""

from typing import Dict, Optional

from OpenGL.GL import glDeleteBuffers, glDeleteVertexArrays

from picogl.backend.modern.core.vertex.base import VertexBase


def delete_dict_buffers(buffer_dict: Dict[str, int]) -> None:
    """
    delete_dict_buffers

    :param buffer_dict:
    :return:
    """
    for buf in buffer_dict.values():
        delete_buffer(buf)
    buffer_dict.clear()


def delete_buffer_object(buffer: Optional[VertexBase]) -> None:
    """
    delete_buffer_object

    :param buffer: Optional[int]
    :return: None
    """
    if buffer is not None and buffer.handle > 0:
        glDeleteBuffers(1, [buffer.handle])


def delete_buffer(buffer: Optional[int]) -> None:
    """
    delete_buffer

    :param buffer: Optional[int]
    :return: None
    """
    if buffer is not None and buffer > 0:
        glDeleteBuffers(1, [buffer])


def delete_vao(vao: Optional[int]) -> None:
    """
    delete_vao

    :param vao: Optional[int]
    :return: None
    """
    if vao is not None and vao > 0:
        glDeleteVertexArrays(1, [vao])
