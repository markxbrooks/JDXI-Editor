"""scan MIDI ports for JD-Xi"""

from decologr import Decologr as log


def find_jdxi_port(port_list: list[str]) -> str | None:
    """Helper function to find address JD-Xi MIDI port."""
    jdxi_names = ["jd-xi", "jdxi", "roland jd-xi"]
    for port in port_list:
        if any(name in port.lower() for name in jdxi_names):
            log.message(f"Auto-detected JD-Xi: {port}")
            return port

    return None
