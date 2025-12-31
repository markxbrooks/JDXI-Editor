
from picogl.renderer import GLContext
from picogl.ui.backend.glut.window.glut import GlutRendererWindow
from picogl.renderer.texture import TextureRenderer


class TextureWindow(GlutRendererWindow):
    """file with stubs for actions"""
    def __init__(self, width, height, title, data, base_dir, glsl_dir, *args, **kwargs):
        self.context = GLContext()
        self.base_dir = base_dir
        self.data = data
        super().__init__(width, height, title, context=self.context, *args, **kwargs)
        self.renderer = TextureRenderer(
            context=self.context,
            data=self.data,
            base_dir=self.base_dir,
            glsl_dir=glsl_dir,
        )
