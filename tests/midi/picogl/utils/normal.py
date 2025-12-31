import numpy as np


def compute_vertex_normals(vertices, indices):
    normals = np.zeros_like(vertices)
    for i in range(0, len(indices), 3):
        i0, i1, i2 = indices[i:i+3]
        v0, v1, v2 = vertices[i0*3:i0*3+3], vertices[i1*3:i1*3+3], vertices[i2*3:i2*3+3]
        edge1 = np.subtract(v1, v0)
        edge2 = np.subtract(v2, v0)
        n = np.cross(edge1, edge2)
        n /= np.linalg.norm(n) + 1e-8
        for idx in (i0, i1, i2):
            normals[idx*3:idx*3+3] += n
    # Normalize
    norms = np.linalg.norm(normals.reshape(-1, 3), axis=1)
    normals = (normals.reshape(-1, 3).T / (norms + 1e-8)).T
    return normals.flatten()


def compute_normals_from_vbo(vbo):
    vertices = np.array(vbo, dtype=np.float32).reshape(-1, 3)
    normals = np.zeros_like(vertices)
    for i in range(0, len(vertices), 3):
        if i+2 >= len(vertices):
            break
        v0, v1, v2 = vertices[i], vertices[i+1], vertices[i+2]
        n = np.cross(v1 - v0, v2 - v0)
        n /= np.linalg.norm(n) + 1e-8
        normals[i] = normals[i+1] = normals[i+2] = n
    return normals.flatten