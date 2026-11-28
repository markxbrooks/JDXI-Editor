"""Project metadata and version information for JD-Xi Editor."""

__version__ = "1.0.2"
__program__ = "JD-Xi Editor"
__project__ = "JD-Xi Editor"
__author__ = "JDXi Editor Team"
__package_name__ = "jdxi_editor"
__organization_name__ = "mabsoft"


def package_version(version: str = __version__) -> str:
    """
    The version for the Linux packages (.deb, .rpm, AppImage names).

    dpkg and rpm order «1.0.0rc1» and «1.0.0b2» *after* «1.0.0»: a release
    candidate or a beta installed from a package would never be offered the
    finished release. A «~» sorts before anything, so a pre-release becomes
    «1.0.0~rc1», «1.0.0~b2», «1.0.0~dev3»; a final version stays as it is.

    :param version: a PEP 440 version (default: this one)
    :return: str the same version, pre-releases with «~»
    """
    import re

    match = re.fullmatch(
        r"(\d+(?:\.\d+)*)((?:a|b|rc)\d+)?(\.post\d+)?(\.dev\d+)?", version
    )
    if match is None:
        return version
    base, pre, post, dev = match.groups()
    result = base
    if pre:
        result += "~" + pre
    if post:
        result += "+" + post[1:]
    if dev:
        result += "~" + dev[1:]
    return result
