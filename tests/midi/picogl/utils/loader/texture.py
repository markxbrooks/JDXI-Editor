import os
import struct
from pathlib import Path

from OpenGL.GL import *
from OpenGL.GL.EXT import texture_compression_s3tc
from OpenGL.raw import GL
from PIL import Image

import os
import struct
import numpy as np
from PIL import Image
from OpenGL.GL import *
from OpenGL.GL import shaders

# Ensure an OpenGL S3TC extension loader is available
from OpenGL.GL.EXT.texture_compression_s3tc import *


class TextureLoader:
    """
    Loads a 2D texture from a DDS file or a standard image file using PIL.
    Automatically creates an OpenGL texture ID.
    """

    def __init__(self, file_name: str, mode: str = "RGB") -> None:
        self.texture_glid: Optional[int] = None
        self.width: int = 0
        self.height: int = 0
        self.format: str = mode
        self.buffer: Optional[bytes] = None
        self.inversed_v_coords: bool = False
        if not os.path.isabs(file_name):
            file_name = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", file_name))
        if file_name.lower().endswith(".dds"):
            self.load_dds(file_name)
        else:
            self.load_by_pil(file_name, mode)

    def load_dds(self, file_name: str) -> None:
        """
        Load a DDS texture from file.
        Supports DXT1, DXT3, DXT5 compressed textures.
        """
        with open(file_name, "rb") as f:
            ddstag = f.read(4)
            if ddstag != b"DDS ":
                raise ValueError(f"Invalid DDS file: {file_name}")

            head = f.read(124)
            self.height = struct.unpack("<I", head[8:12])[0]
            self.width = struct.unpack("<I", head[12:16])[0]
            linearSize = struct.unpack("<I", head[16:20])[0]
            mipMapCount = struct.unpack("<I", head[24:28])[0]
            fourCC = head[80:84].decode("ascii")

        supported_DDS = ["DXT1", "DXT3", "DXT5"]
        if fourCC not in supported_DDS:
            raise ValueError(f"Not supported DDS file: {fourCC}")

        self.format = fourCC

        blockSize = 8 if fourCC == "DXT1" else 16
        gl_format = {
            "DXT1": GL_COMPRESSED_RGBA_S3TC_DXT1_EXT,
            "DXT3": GL_COMPRESSED_RGBA_S3TC_DXT3_EXT,
            "DXT5": GL_COMPRESSED_RGBA_S3TC_DXT5_EXT,
        }[fourCC]

        bufferSize = linearSize * 2 if mipMapCount > 1 else linearSize

        with open(file_name, "rb") as f:
            f.seek(128)  # skip DDS header
            ddsbuffer = f.read(bufferSize)

        self.texture_glid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_glid)

        offset = 0
        w, h = self.width, self.height
        for level in range(mipMapCount):
            size = ((w + 3) // 4) * ((h + 3) // 4) * blockSize
            glCompressedTexImage2D(
                GL_TEXTURE_2D,
                level,
                gl_format,
                w,
                h,
                0,
                size,
                ddsbuffer[offset:offset + size],
            )
            offset += size
            w //= 2
            h //= 2
            if w == 0 or h == 0:
                break

        self.inversed_v_coords = True

    def load_by_pil(self, fname: str, mode: str) -> None:
        """
        Load a standard image using PIL and upload as OpenGL texture.
        """
        with Image.open(fname) as image:
            converted = image.convert(mode)
            self.buffer = converted.transpose(Image.FLIP_TOP_BOTTOM).tobytes()
            self.width, self.height = image.size
            self.format = mode

        # Map PIL mode to OpenGL format
        gl_format_map = {"RGB": GL_RGB, "RGBA": GL_RGBA}
        gl_format = gl_format_map.get(mode.upper(), GL_RGB)

        self.texture_glid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_glid)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            gl_format,
            self.width,
            self.height,
            0,
            gl_format,
            GL_UNSIGNED_BYTE,
            self.buffer,
        )

        # Texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glGenerateMipmap(GL_TEXTURE_2D)

    def delete(self) -> None:
        """
        Deletes the OpenGL texture to free GPU memory.
        """
        if self.texture_glid:
            glDeleteTextures([self.texture_glid])
            self.texture_glid = None

    def __len__(self) -> int:
        return len(self.buffer) if self.buffer else 0
    

if __name__ == "__main__":
    texture = TextureLoader(file_name=os.path.join(str(Path.home()),
                                                   "projects/PicoGL/examples/resources/tu02/uvtemplate.tga"))
    print(texture.texture_glid)
    print(texture.width)
    print(texture.height)
    print(texture.format)
    print(texture.buffer)
    print(texture.inversed_v_coords)
    texture.delete()