import struct
import binascii
from pathlib import Path


def extract_patches(data):
    patches = []
    patch_size = len(data) // 16  # Assuming 16 patches per file
    for i in range(16):
        patch_data = data[i * patch_size: (i + 1) * patch_size]

        # Extracting name (assuming first 16 bytes contain the name)
        raw_name = patch_data[:16]
        try:
            patch_name = raw_name.decode('utf-8', errors='ignore').strip('\x00')
        except UnicodeDecodeError:
            patch_name = "(Invalid UTF-8)"

        patches.append((patch_name, binascii.hexlify(patch_data).decode()))
    return patches


def parse_sysex_file(filename):
    with open(filename, 'rb') as f:
        data = f.read()

    patches = extract_patches(data)
    for i, (name, raw) in enumerate(patches, 1):
        log_message(f"Patch {i}: {name}")
        log_message(f"Raw Data: {raw[:200]}...")  # Show only the first 200 hex characters
        log_message("-" * 40)


def parse_patch(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()

    # Try to decode readable ASCII/UTF-8 text
    readable_text = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)

    # Identify possible header information
    header = data[:16]  # Assuming the first 16 bytes contain metadata

    # Extract patch name (likely found early in the file)
    patch_name_start = readable_text.find("SDZ")
    patch_name = readable_text[patch_name_start:patch_name_start + 32] if patch_name_start != -1 else "Unknown"

    # Find possible SysEx messages (SysEx typically starts with 0xF0 and ends with 0xF7)
    sysex_messages = []
    start = 0
    while True:
        start = data.find(b'\xF0', start)
        if start == -1:
            break
        end = data.find(b'\xF7', start)
        if end == -1:
            break
        sysex_messages.append(data[start:end + 1])
        start = end + 1

    # Convert SysEx messages to hex
    sysex_hex = [binascii.hexlify(msg).decode() for msg in sysex_messages]

    print("Patch Header:", header)
    print("Patch Name:", patch_name.strip())
    print("Readable Text:", readable_text[:200])  # Print first 200 readable characters
    print("SysEx Messages:")
    for msg in sysex_hex:
        print(msg)

    return {
        "patch_name": patch_name.strip(),
        "header": header,
        "readable_text": readable_text,
        "sysex_messages": sysex_hex,
    }


if __name__ == "__main__":
    file_name = Path.home() / "Downloads" / "SDZ040_AnaPlySn_FANTOM-0" / "SDZ040_AnaPlySn.sdz"
    # result = parse_sysex_file(file_name)
    result = parse_patch(file_name)
    print(result)
# Example usage:
# result = parse_jdxi_patch("path_to_patch_file.syx")
