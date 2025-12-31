"""
Object Loader
Loader of object data from an .loader file.
"""

import os

from picogl.logger import Logger as log
from picogl.utils.loader.helpers import log_properties
from picogl.utils.loader.object_data import ObjectData


class OBJLoader:
    def __init__(self, path: str):
        # Resolve the path relative to the current working directory
        if not os.path.isabs(path):
            # Try to find the file relative to the current working directory
            if os.path.exists(path):
                path = os.path.abspath(path)
            else:
                # Fallback to relative to this script's directory
                script_dir = os.path.dirname(os.path.abspath(__file__))
                path = os.path.abspath(os.path.join(script_dir, "..", path))

        if not os.path.exists(path):
            raise FileNotFoundError(f"OBJ file not found: {path}")

        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.indices = []

        with open(path, "r") as f:
            for line in f:
                if not line.strip() or line.startswith("#"):
                    continue

                parts = line.split()
                code = parts[0]

                if code == "v":
                    self.vertices.extend(map(float, parts[1:4]))

                elif code == "vn":
                    self.normals.extend(map(float, parts[1:4]))

                elif code == "vt":
                    self.texcoords.extend(map(float, parts[1:3]))

                elif code == "f":
                    # Faces can be v, v/t, v//n, or v/t/n
                    face_indices = []
                    for ref in parts[1:]:
                        # split() result length can be 1, 2, or 3
                        subs = ref.split("/")
                        while len(subs) < 3:
                            subs.append("")  # pad to 3 elements
                        
                        # Parse indices (OBJ uses 1-based indexing)
                        v_idx = int(subs[0]) if subs[0] else 0
                        t_idx = int(subs[1]) if subs[1] else 0
                        n_idx = int(subs[2]) if subs[2] else 0
                        
                        face_indices.append((v_idx, t_idx, n_idx))
                    
                    # Store the face indices
                    self.indices.extend([idx for face in face_indices for idx in face])

                elif code in ("s", "mtllib", "usemtl"):
                    # Optional properties
                    setattr(self, code, parts[1] if len(parts) > 1 else None)

                elif code == "g":
                    # Group name — skip for now
                    continue

                else:
                    print(f"Skipping unknown line: {line.strip()}")
        self.log_properties()

    def log_properties(self):
        """ log object properties """
        log_properties(self)

    def to_array_style(self) -> ObjectData:
        """Convert to array-style where each vertex attribute is stored separately"""
        vertices, texcoords, normals = [], [], []

        for i in range(0, len(self.indices), 3):
            v_idx, t_idx, n_idx = self.indices[i:i + 3]

            # Get vertex position (1-based to 0-based)
            if v_idx > 0:
                v_start = 3 * (v_idx - 1)
                vertices.extend(self.vertices[v_start:v_start + 3])
            else:
                vertices.extend([0.0, 0.0, 0.0])  # Default vertex

            # Get texture coordinates (1-based to 0-based)
            if t_idx > 0 and self.texcoords:
                t_start = 2 * (t_idx - 1)
                texcoords.extend(self.texcoords[t_start:t_start + 2])
            else:
                texcoords.extend([0.0, 0.0])  # Default texcoord

            # Get normal (1-based to 0-based)
            if n_idx > 0 and self.normals:
                n_start = 3 * (n_idx - 1)
                normals.extend(self.normals[n_start:n_start + 3])
            else:
                normals.extend([0.0, 0.0, 1.0])  # Default normal

        data = ObjectData(vertices, texcoords, normals)
        return data

    def to_single_index_style(self) -> ObjectData:
        """Convert to single-index style where each unique vertex attribute combination is stored once"""
        vertices, texcoords, normals, indices = [], [], [], []
        combinations = {}

        for i in range(0, len(self.indices), 3):
            v_idx, t_idx, n_idx = self.indices[i:i + 3]
            key = (v_idx, t_idx, n_idx)

            if key not in combinations:
                combinations[key] = len(combinations)

                # Get vertex position (1-based to 0-based)
                if v_idx > 0:
                    v_start = 3 * (v_idx - 1)
                    vertices.extend(self.vertices[v_start:v_start + 3])
                else:
                    vertices.extend([0.0, 0.0, 0.0])  # Default vertex

                # Get texture coordinates (1-based to 0-based)
                if t_idx > 0 and self.texcoords:
                    t_start = 2 * (t_idx - 1)
                    texcoords.extend(self.texcoords[t_start:t_start + 2])
                else:
                    texcoords.extend([0.0, 0.0])  # Default texcoord

                # Get normal (1-based to 0-based)
                if n_idx > 0 and self.normals:
                    n_start = 3 * (n_idx - 1)
                    normals.extend(self.normals[n_start:n_start + 3])
                else:
                    normals.extend([0.0, 0.0, 1.0])  # Default normal

            indices.append(combinations[key])

        return ObjectData(vertices, texcoords, normals, indices)


if __name__ == "__main__":
    # Test with the teapot model_matrix
    try:
        obj = OBJLoader("data/teapot.loader")
        log_properties(obj)
    except FileNotFoundError as e:
        log.message(f"Error: {e}")
        log.message("Make sure the teapot.loader file exists in the data/ directory")
    except Exception as e:
        log.message(f"Error loading OBJ file: {e}")
