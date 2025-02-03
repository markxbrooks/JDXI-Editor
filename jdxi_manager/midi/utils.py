import sys
import time
import mido
from jdxi_manager.utils import printdebug  # Assuming you have a utility function for debugging

def send_sysex_RQ1(deviceID, address, size):
    """
    This message requests the other device to transmit data. The address
    and size indicate the type and amount of data that is requested.
    
    Parameters
    ----------
    deviceID : List of data for specific device - [0x41,0x10,0x00,0x00,0x00,0x0e] for Roland JD-Xi
    address : base address where to save data (last byte, base address will be defined in the instrument)
    size : list of four bytes- [MSB, 2nd, 3rd, LSB]
    """
    sysexdata = deviceID + [0x11] + address + size + [0]
    printdebug(sys._getframe().f_lineno, "sysex" + str(sysexdata))
    msg = mido.Message('sysex', data=sysexdata)
    outport.send(msg)

    time.sleep(.2)
    counter = 0
    found = False
    while True:
        counter += 1
        msg = inport.poll()
        if msg is not None:
            if msg.type == 'clock':
                continue
            printdebug(sys._getframe().f_lineno, str("Msg type: " + msg.type))
            if msg.type == 'sysex':
                printdebug(sys._getframe().f_lineno, str("Msg data: " + str(msg.data)))
                printdebug(sys._getframe().f_lineno, str("Msg hex: " + "".join('%02x' % i for i in msg.data)))
                if list(msg.data)[:11] == deviceID + [0x12] + address:
                    printdebug(sys._getframe().f_lineno, "This is good message from Roland JD-Xi.")
                    found = True
                    break
                else:
                    continue
        if counter > 100:
            logger.warning("Waiting too long for status identification.")
            break
    if found:
        return list(msg.data)[11:-1]
    else:
        return 'unknown' 