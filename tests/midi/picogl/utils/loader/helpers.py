from picogl.logger import Logger as log
#from picogl.utils.loader.object import OBJLoader


def log_properties(loader: "OBJLoader"):
    """ log object properties """
    log.message(f"Loaded OBJ file successfully")
    log.message(f"Total vertices: {len(loader.vertices) // 3}")
    log.message(f"Total normals: {len(loader.normals) // 3}")
    log.message(f"Total texcoords: {len(loader.texcoords) // 2}")
    log.message(f"Total face indices: {len(loader.indices) // 3}")

    log.message(f"First few vertices: {loader.vertices[:9]}")
    log.message(f"First few indices: {loader.indices[:9]}")
    log.message(f"First few normals: {loader.normals[:9]}")
    log.message(f"First few texcoords: {loader.texcoords[:6]}")

    single_index_obj = loader.to_single_index_style()
    log.message(f"Single Index Style:")
    log.message(f"Vertices: {len(single_index_obj.vertices) // 3}")
    log.message(f"Indices: {len(single_index_obj.indices)}")
    log.message(f"Normals: {len(single_index_obj.normals) // 3}")
    log.message(f"Texcoords: {len(single_index_obj.texcoords) // 2}")