import sys
import time
import mido
from jdxi_manager.utils import printdebug  # Assuming you have a utility function for debugging

class AnalogSynth:
    def __init__(self, deviceID, address, datalength, attributes):
        self.deviceID = deviceID
        self.address = address
        self.datalength = datalength
        self.attributes = attributes
        self.devicestatus = 'unknown'

    def get_data(self):
        data = send_sysex_RQ1(self.deviceID, self.address + [0x00], self.datalength)
        printdebug(sys._getframe().f_lineno, "Data received: " + str(data))
        if data == 'unknown':
            self.devicestatus = 'unknown'
            return '7OF9'
        else:
            self.devicestatus = 'OK'
        for attr in self.attributes:
            if attr != 'Name':
                self.attributes[attr][0] = data[self.attributes[attr][1]]
            else:
                name = ''
                for c in data[self.attributes[attr][1]:self.attributes[attr][1] + 12]:
                    name += chr(c)
                self.attributes[attr][0] = name
        return 'OK' 