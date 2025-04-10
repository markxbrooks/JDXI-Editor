import logging


def _find_jdxi_port(ports, port_type):
    """Helper function to find address JD-Xi MIDI port."""
    jdxi_names = ["jd-xi", "jdxi", "roland jd-xi"]
    for port in ports:
        if any(name in port.lower() for name in jdxi_names):
            logging.info(f"Auto-detected JD-Xi {port_type}: {port}")
            return port
    return None
