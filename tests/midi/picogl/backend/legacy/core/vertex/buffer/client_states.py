"""
Legacy Client States context manager
"""

from contextlib import contextmanager

from OpenGL.raw.GL.VERSION.GL_1_1 import (glDisableClientState,
                                          glEnableClientState)
from OpenGL.raw.GL.VERSION.GL_1_5 import GL_ARRAY_BUFFER, glBindBuffer, GL_ELEMENT_ARRAY_BUFFER


@contextmanager
def legacy_client_states(*states):
    """Enable/disable fixed-function client states safely."""
    for s in states:
        glEnableClientState(s)
    try:
        yield
    finally:
        # Disable in reverse order and unbind both array buffers
        for s in reversed(states):
            glDisableClientState(s)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)


@contextmanager
def legacy_client_states_old(*states):
    """legacy client states context manager"""
    for state in states:
        glEnableClientState(state)
    try:
        yield
    finally:
        for state in reversed(states):
            glDisableClientState(state)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
