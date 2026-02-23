#!/usr/bin/env python3
"""
Clean SINCO VMX8 Controller Test using Mido

This test uses Mido without any rtmidi compatibility conflicts.
"""

import sys
import time

import mido
from picomidi.message.type import MidoMessageType


def test_with_mido():
    """Test SINCO VMX8 controller using Mido"""
    print("SINCO VMX8 Controller Test using Mido")
    print("=" * 50)

    # List available input ports
    input_ports = mido.get_input_names()
    print(f"Available MIDI input ports: {len(input_ports)}")
    for i, port in enumerate(input_ports):
        print(f"  {i}: {port}")

    # Find SINCO ports
    sinco_ports = []
    for i, port in enumerate(input_ports):
        if "SINCO" in port.upper() or "VMX8" in port.upper():
            sinco_ports.append((i, port))

    if not sinco_ports:
        print("❌ No SINCO VMX8 ports found")
        return False

    print(f"\nFound SINCO VMX8 ports: {[port[1] for port in sinco_ports]}")

    # Test each SINCO port
    for port_index, port_name in sinco_ports:
        print(f"\n=== Testing Port: {port_name} ===")

        try:
            # Open the port
            with mido.open_input(port_name) as inport:
                print(f"✅ Connected to {port_name}")
                print("Move controls on your SINCO VMX8 controller...")
                print("Monitoring for 15 seconds...\n")

                message_count = 0
                start_time = time.time()

                # Monitor for messages
                for message in inport:
                    message_count += 1
                    elapsed = time.time() - start_time

                    # Format timestamp like your working app
                    timestamp_str = f"{elapsed:.3f}"

                    # Decode the message
                    if message.type == MidoMessageType.CONTROL_CHANGE:
                        channel = message.channel + 1
                        controller = message.control
                        value = message.STATUS

                        # Format like your working app
                        if controller == 10:
                            print(
                                f"{timestamp_str:>8}\tFrom {port_name}\tControl\t{channel}\tPan (fine)\t{value}"
                            )
                        elif controller == 41:
                            print(
                                f"{timestamp_str:>8}\tFrom {port_name}\tControl\t{channel}\tController 41\t{value}"
                            )
                        else:
                            print(
                                f"{timestamp_str:>8}\tFrom {port_name}\tControl\t{channel}\tController {controller}\t{value}"
                            )
                    elif message.type == MidoMessageType.NOTE_ON:
                        channel = message.channel + 1
                        note = message.note
                        velocity = message.velocity
                        print(
                            f"{timestamp_str:>8}\tFrom {port_name}\tNote On\t{channel}\tNote {note}\t{velocity}"
                        )
                    elif message.type == MidoMessageType.NOTE_OFF:
                        channel = message.channel + 1
                        note = message.note
                        velocity = message.velocity
                        print(
                            f"{timestamp_str:>8}\tFrom {port_name}\tNote Off\t{channel}\tNote {note}\t{velocity}"
                        )
                    elif message.type == MidoMessageType.PROGRAM_CHANGE:
                        channel = message.channel + 1
                        program = message.program
                        print(
                            f"{timestamp_str:>8}\tFrom {port_name}\tProgram Change\t{channel}\tProgram {program}"
                        )
                    else:
                        print(
                            f"{timestamp_str:>8}\tFrom {port_name}\t{message.type}\t{message}"
                        )

                    # Check if we've been monitoring long enough
                    if time.time() - start_time > 15:
                        break

                if message_count > 0:
                    print(
                        f"\n✅ SUCCESS! Received {message_count} messages from {port_name}"
                    )
                else:
                    print(f"\n❌ No messages received from {port_name}")

        except Exception as e:
            print(f"❌ Error testing {port_name}: {e}")

    return True


def main():
    try:
        success = test_with_mido()
        if success:
            print("\n✅ Mido test completed!")
        else:
            print("\n❌ Mido test failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
