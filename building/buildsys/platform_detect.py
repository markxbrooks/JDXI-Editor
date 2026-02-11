import platform

def get_platform() -> str:
    system = platform.system()

    if system == "Linux":
        return "linux"
    if system == "Darwin":
        return "macos"
    if system == "Windows":
        return "windows"

    raise RuntimeError(f"Unsupported OS: {system}")
