"""
Object Window for displaying Mesh Data
"""
from pathlib import Path

from picogl.renderer import GLContext, MeshData
from picogl.renderer.object import ObjectRenderer
from picogl.ui.backend.glut.window.glut import GlutRendererWindow


class ObjectWindow(GlutRendererWindow):
    """colored with no texture"""
    def __init__(self,
                 width: int = 800,
                 height: int = 600,
                 title = "Window",  data: MeshData = None,
                 glsl_dir: str | Path = None,
                 *args,
                 **kwargs):
        super().__init__(width=width, height=height, title=title, *args, **kwargs)
        self.context = GLContext()
        self.data = data
        self.glsl_dir = glsl_dir
        self.renderer = ObjectRenderer(
            context=self.context,
            data=self.data,
            glsl_dir=self.glsl_dir,
        )
        self.renderer.show_model = True  # set here whether to show the cube

