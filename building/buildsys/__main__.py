from .platform_detect import get_platform
from .context import BuildContext

def main():
    ctx = BuildContext()
    platform = get_platform()

    print(f"Building on: {platform}")
    print(f"Project root: {ctx.project_root}")

    if platform == "linux":
        from .linux import build
    elif platform == "macos":
        from .macos import build
    elif platform == "windows":
        from .windows import build
    else:
        raise RuntimeError(platform)

    build(ctx)

if __name__ == "__main__":
    main()
