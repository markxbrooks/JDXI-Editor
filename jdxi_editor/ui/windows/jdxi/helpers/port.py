"""scan MIDI ports for JD-Xi"""

from decologr import Decologr as log

# Ports to exclude from auto-connection (loopback/virtual ports that cause feedback)
EXCLUDED_PORTS = [
    "midi through",
    "through port",
    "midithru",
    "rtpmidi",  # Network MIDI can cause issues
]


def is_excluded_port(port_name: str) -> bool:
    """Check if a port should be excluded from auto-connection.

    :param port_name: str MIDI port name
    :return: bool True if port should be excluded
    """
    port_lower = port_name.lower()
    return any(excluded in port_lower for excluded in EXCLUDED_PORTS)


def find_jdxi_port(port_list: list[str]) -> str | None:
    """Helper function to find a JD-Xi MIDI port.

    :param port_list: list[str] List of available MIDI port names
    :return: str | None JD-Xi port name or None if not found
    """
    jdxi_names = ["jd-xi", "jdxi", "roland jd-xi"]
    for port in port_list:
        # Skip excluded ports (like MIDI Through which causes feedback loops)
        if is_excluded_port(port):
            log.message(f"Skipping excluded port: {port}", scope="find_jdxi_port")
            continue
        if any(name in port.lower() for name in jdxi_names):
            log.message(f"[find_jdxi_port] Auto-detected JD-Xi: {port}", scope="find_jdxi_port")
            return port

    return None


def filter_excluded_ports(port_list: list[str]) -> list[str]:
    """Filter out problematic ports from a list.

    :param port_list: list[str] List of MIDI port names
    :return: list[str] Filtered list without excluded ports
    """
    return [port for port in port_list if not is_excluded_port(port)]
