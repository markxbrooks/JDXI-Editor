"""
Abstract render atoms_buffers class
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from OpenGL.arrays import vbo
from OpenGL.GL import (GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER, GL_FLOAT,
                       glBindBuffer, glBindVertexArray, glDeleteVertexArrays,
                       glDisableVertexAttribArray, glEnableVertexAttribArray,
                       glGenVertexArrays, glVertexAttribPointer)

#from picogl.buffers.glcleanup import delete_buffer


@dataclass
class AttributeSpec:
    index: int  # attribute location
    size: int  # number of components (e.g., 3 for vec3)
    type: int  # GL_FLOAT, GL_INT, etc.
    normalized: bool
    stride: int
    offset: int


@dataclass
class LayoutDescriptor:
    attributes: List[AttributeSpec]


# Public façade
class VertexArrayGroup(ABC):
    @abstractmethod
    def bind(self) -> None:
        """Bind the underlying VAO/state for rendering."""
        pass

    @abstractmethod
    def unbind(self) -> None:
        """Optionally unbind the VAO/state."""
        pass

    @abstractmethod
    def delete(self) -> None:
        """Release resources (VAO or equivalent)."""
        pass

    @abstractmethod
    def set_layout(self, layout: LayoutDescriptor) -> None:
        """Define the attribute layout for this VAO/group."""
        pass

    @abstractmethod
    def attach_buffers(self, nbo=None, cbo=None, vbo=None, ebo=None) -> None:
        """Attach the buffers that the VAO/group should coordinate."""
        pass


class AbstractVertexBuffer:
    """Generic OpenGL object interface with binding lifecycle."""

    def __init__(self, handle=None):
        self.handle = handle

    def bind(self):
        raise NotImplementedError

    def unbind(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()


class LegacyVertexArrayGroup(VertexArrayGroup):
    def __init__(self):
        self.layout = None
        self.ebo = None
        self.vbo = None
        self.cbo = None
        self.nbo = None

    def init(self):
        self.nbo = None  # Normal Vertex Buffer Object
        self.cbo = None  # Color Vertex Buffer Object
        self.vbo = None  # Atom Vertex Buffer Object
        self.ebo = None  # Bond Index Buffer Object
        self.layout: Optional[LayoutDescriptor] = None

    def attach_buffers(self, nbo=None, cbo=None, vbo=None, ebo=None) -> None:
        self.nbo = nbo
        self.cbo = cbo
        self.vbo = vbo
        self.ebo = ebo

    def set_layout(self, layout: LayoutDescriptor) -> None:
        """
        set_layout

        In legacy path, we configure attributes on bind (no real VAO)
        Keep layout stored for reapplication on bind.
        """
        self.layout = layout

    def bind(self) -> None:
        """
        bind

        Bind buffers and re-upload attribute pointers per stored layout
        """
        if self.vbo is not None:
            glBindBuffer(GL_ARRAY_BUFFER, getattr(self.vbo, "_id", self.vbo))
        if self.cbo is not None:
            glBindBuffer(GL_ARRAY_BUFFER, getattr(self.cbo, "_id", self.cbo))
        # TODO: choose which buffer binds to GL_ARRAY_BUFFER per attribute
        if self.layout:
            for attr in self.layout.attributes:
                glEnableVertexAttribArray(attr.index)
                glVertexAttribPointer(
                    attr.index,
                    attr.size,
                    attr.type,
                    attr.normalized,
                    attr.stride,
                    ctypes.c_void_p(attr.offset),
                )
        if self.ebo is not None:
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, getattr(self.ebo, "_id", self.ebo))

    def unbind(self) -> None:
        """
        unbind

        Optional: disable attributes or reset state
        """
        if self.layout:
            for attr in self.layout.attributes:
                glDisableVertexAttribArray(attr.index)

        # In legacy, there’s no VAO to unbind; you may unbind buffers as needed
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def delete(self) -> None:
        delete_buffer(self.nbo)
        delete_buffer(self.cbo)
        delete_buffer(self.vbo)
        delete_buffer(self.ebo)
        self.nbo = self.cbo = self.vbo = self.ebo = None
        self.layout = None


class ModernVertexArrayGroup(VertexArrayGroup):
    """Modern backend (uses a real VAO)"""

    def __init__(self):
        self.layout = None
        self.vao = None
        self.nbo = None
        self.cbo = None
        self.vbo = None
        self.ebo = None
        self._configured = None

    def init(self):
        self.vao = glGenVertexArrays(1)
        self.nbo = None
        self.cbo = None
        self.vbo = None
        self.ebo = None
        self.layout: Optional[LayoutDescriptor] = None
        self._configured = False

    def attach_buffers(self, nbo=None, cbo=None, vbo=None, ebo=None) -> None:
        self.nbo = nbo
        self.cbo = cbo
        self.vbo = vbo
        self.ebo = ebo

    def set_layout(self, layout: LayoutDescriptor) -> None:
        """
        set_layout

        :param layout: LayoutDescriptor
        :return: None

        Bind the buffers and set up attributes; this state is stored in the VAO
        Bind a canonical index for the VBO that holds vertex data for this layout
        This example assumes a single VBO holds all position data, but you can adapt.
        """
        self.layout = layout
        glBindVertexArray(self.vao)
        if self.vbo is not None:
            glBindBuffer(GL_ARRAY_BUFFER, getattr(self.vbo, "_id", self.vbo))
        if self.nbo is not None:
            # TODO: If you have multiple buffers, bind as needed per attribute
            pass  # adapt as needed

        if self.layout:
            for attr in self.layout.attributes:
                glEnableVertexAttribArray(attr.index)
                glVertexAttribPointer(
                    attr.index,
                    attr.size,
                    attr.type,
                    attr.normalized,
                    attr.stride,
                    ctypes.c_void_p(attr.offset),
                )
        if self.ebo is not None:
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, getattr(self.ebo, "_id", self.ebo))

        glBindVertexArray(0)
        self._configured = True

    def bind(self) -> None:
        glBindVertexArray(self.vao)

    def unbind(self) -> None:
        glBindVertexArray(0)

    def delete(self) -> None:
        if self.vao:
            glDeleteVertexArrays([self.vao])
            self.vao = 0
        delete_buffer(self.nbo)
        delete_buffer(self.cbo)
        delete_buffer(self.vbo)
        delete_buffer(self.ebo)
        self.nbo = self.cbo = self.vbo = self.ebo = None
        self.layout = None
        self._configured = False
