"""
Object Data

Representation of object data from an .loader file.

Example Usage:

# If raw_data.indices exists, keep it; otherwise ObjectData will generate it
self.data = ObjectData(
    vertices=raw_data.vertices,
    texcoords=raw_data.texcoords or [],
    normals=raw_data.normals,
    indices=getattr(raw_data, "indices", None)
)
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ObjectData:
    vertices: List[float]
    texcoords: List[float] = field(default_factory=list)
    normals: List[float] = field(default_factory=list)
    indices: Optional[List[int]] = None

    def __post_init__(self):
        # If indices not provided, generate 0..(vertex_count-1)
        if self.indices is None:
            vertex_count = len(self.vertices) // 3
            self.indices = list(range(vertex_count))