""" scan MIDI ports for JD-Xi """

from jdxi_editor.log.message import log_message


def find_jdxi_port(port_list: list):
    """Helper function to find address JD-Xi MIDI port."""
    jdxi_names = ["jd-xi", "jdxi", "roland jd-xi"]
    for port in port_list:
        if any(name in port.lower() for name in jdxi_names):
            log_message(f"Auto-detected JD-Xi: {port}")
            return port

    return None
