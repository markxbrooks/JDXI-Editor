__version__ = "0.1.0"

__all__ = ["__version__", "RendererBase", "GLContext", "GLData", "VertexArrayObject"]


def __getattr__(name):
    if name in {"RendererBase", "GLContext", "GLData"}:
        from importlib import import_module

        mod = import_module("picogl.renderer")
        return getattr(mod, name)
    if name == "VertexArrayObject":
        from importlib import import_module

        mod = import_module("picogl.backend.modern.core.vertex.array.object")
        return getattr(mod, name)
    raise AttributeError(name)
