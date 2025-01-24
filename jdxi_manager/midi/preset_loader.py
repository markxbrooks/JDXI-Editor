import logging
import time
from typing import Optional

from pubsub import pub

from jdxi_manager.midi import MIDIHelper
from jdxi_manager.midi.constants import (
    DT1_COMMAND_12,
    RQ1_COMMAND_11
)
from jdxi_manager.data.preset_type import PresetType
from jdxi_manager.midi.constants.sysex import DEVICE_ID
from jdxi_manager.midi.sysex import XI_HEADER


class PresetLoader:
    """Utility class for loading presets via MIDI"""

    def __init__(self, midi_helper, dev_nr=DEVICE_ID, debug=False): #, midi_indev):
        self.midi_helper = midi_helper
        self.midi_outdev = midi_helper
        self.midi_indev = midi_helper
        self.dev_nr = dev_nr
        self.debug = debug
        self.midi_lock = 0
        self.midi_last = time.time()
        self.pdm_val = {}
        pub.subscribe(self.load_preset, 'load_preset')

    def send_pa_ch_msg(self, addr, value, nr):
        if self.midi_outdev:
            while self.midi_lock != 0:
                time.sleep(0.001)  # wait until preceding parameter changes are done
            self.midi_lock = 1  # lock out other parameter change attempts

            if self.debug:
                logging.debug(f"par:[{addr}] val:[{value}] len:[{nr}]")

            # Prepare sysex string to send
            data = ''
            if nr > 1:
                data = f"{value:0{nr}X}"
                data = bytes.fromhex(data)
            else:
                data = bytes([value])

            addr_bytes = bytes.fromhex(addr)
            chksum = self.calculate_checksum(addr_bytes + data)
            sysex = XI_HEADER + bytes([DT1_COMMAND_12]) + addr_bytes + data + bytes([chksum, 0xF7])

            # Enforce 2 ms gap since last parameter change message sent
            midinow = time.time()
            gap = midinow - self.midi_last
            if gap < 0.002:
                time.sleep(0.002 - gap)

            # Send the MIDI data to the synth
            self.midi_outdev.send_message(sysex)
            self.midi_last = time.time()  # store timestamp
            self.midi_lock = 0  # allow other parameter changes to proceed

    def calculate_checksum(self, data):
        """Calculate Roland checksum for parameter messages"""
        checksum = sum(data) & 0x7F
        result = (128 - checksum) & 0x7F
        return result

    def load_preset(self, preset_data, type=None):
        response = 'Yes'
        if response == 'Yes' or preset_data['modified'] == 0:
            address = ''
            msb = 0
            lsb = 64
            preset_number = int(preset_data['selpreset'])
            if preset_data['type'] == PresetType.DIGITAL_1:
                address = '18002006'
                msb = 95
                if preset_number > 128:
                    lsb = 65
                    preset_number -= 128
            elif preset_data['type'] == PresetType.DIGITAL_2:
                address = '18002106'
                msb = 95
                if preset_number > 128:
                    lsb = 65
                    preset_number -= 128
            elif preset_data['type'] == PresetType.ANALOG:
                address = '18002206'
                msb = 94
            elif preset_data['type'] == PresetType.DRUMS:
                address = '18002306'
                msb = 86

            # Ensure addr is a string before using fromhex
            if not isinstance(address, str):
                raise ValueError("Address must be a string.")

            # Send the correct SysEx messages
            self.send_pa_ch_msg(address, msb, 1)
            self.send_pa_ch_msg(f"{int(address, 16) + 1:08X}", lsb, 1)
            self.send_pa_ch_msg(f"{int(address, 16) + 2:08X}", preset_number - 1, 1)

            # Additional SysEx messages for loading the preset
            self.send_sysex_message('19', '01', '00', '00', '00', '00', '00', '40')
            self.send_sysex_message('19', '01', '20', '00', '00', '00', '00', '3D')
            self.send_sysex_message('19', '01', '21', '00', '00', '00', '00', '3D')
            self.send_sysex_message('19', '01', '22', '00', '00', '00', '00', '3D')
            self.send_sysex_message('19', '01', '50', '00', '00', '00', '00', '25')

    def send_sysex_message(self, addr1, addr2, addr3, addr4, data1, data2, data3, data4):
        # Construct the SysEx message
        sysex_msg = [
            0xF0,  # Start of SysEx
            0x41,  # Roland ID
            0x10,  # Device ID
            0x00, 0x00, 0x00, 0x0E,  # Model ID
            0x11,  # Command ID (for additional messages)
            int(addr1, 16),  # Address 1
            int(addr2, 16),  # Address 2
            int(addr3, 16),  # Address 3
            int(addr4, 16),  # Address 4
            int(data1, 16),  # Data 1
            int(data2, 16),  # Data 2
            int(data3, 16),  # Data 3
            int(data4, 16),  # Data 4
            0xF7   # End of SysEx
        ]

        # Calculate checksum
        checksum = (0x80 - (sum(sysex_msg[8:-1]) & 0x7F)) & 0x7F
        sysex_msg.insert(-1, checksum)

        # Send the SysEx message
        self.midi_helper.send_message(sysex_msg)
        logging.debug(f"Sent SysEx message: {sysex_msg}")

    def unsaved_changes(self, window, message):
        # Implement the logic to handle unsaved changes
        # Return 'Yes' or 'No' based on user input
        if self.midi_outdev:
            while self.midi_lock != 0:
                time.sleep(0.001)  # wait until preceding parameter changes are done
            self.midi_lock = 1  # lock out other parameter change attempts

            if self.debug:
                logging.debug(f"par:[{addr}] val:[{value}] len:[{nr}]")

            # Prepare sysex string to send
            data = ''
            if nr > 1:
                data = f"{value:0{nr}X}"
                data = bytes.fromhex(data)
            else:
                data = bytes([value])

            addr_bytes = bytes.fromhex(addr)
            chksum = self.calculate_checksum(addr_bytes + data)
            sysex = bytes([0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E]) + addr_bytes + data + bytes([chksum, 0xF7])

            # Enforce 2 ms gap since last parameter change message sent
            midinow = time.time()
            gap = midinow - self.midi_last
            if gap < 0.002:
                time.sleep(0.002 - gap)

            # Send the MIDI data to the synth
            self.midi_outdev.send_message(sysex)
            self.midi_last = time.time()  # store timestamp
            self.midi_lock = 0  # al

    def sysex_pat_receive(self, preset_data):
        # Implement the logic to handle SysEx pattern receive
        tmp_dump = []
        # self.set_busy(True)

        for n in range(len(preset_data['data'])):
            sysex = preset_data['addr'][n] + preset_data['rqlen'][n]
            exp_len = preset_data['datalen'][n] + 14
            sysex_message = self.construct_sysex_message(sysex)
            received_data = self.syx_receive(sysex_message, exp_len, preset_data['window'])

            if not received_data:
                #self.set_busy(False)
                self.error(preset_data['window'], "No Sysex data received from JD-Xi\nCheck your MIDI connections and settings")
                return

            if self.debug:
                print(f"tmp dump[{n}] length {len(received_data)}")

            check = self.validate_pat_data(received_data, preset_data['pattern'][n], exp_len)
            if check != 'ok':
                if self.debug:
                    print(check)
                # self.set_busy(False)
                self.error(preset_data['window'], f"Error while receiving data from JD-Xi\n\n{check}")
                return

            tmp_dump.append(received_data)

        # All data received and checked successfully
        for n in range(len(preset_data['data'])):
            self.read_pat_data(tmp_dump[n][12:12 + preset_data['datalen'][n]], preset_data, n)
            if preset_data['name'][n] != "\x00":
                preset_data['name'][n] = self.pdata_to_name(preset_data['data'][n])

        preset_data['modified'] = 0
        preset_data['filename'] = ''
        preset_data['window'].set_title(preset_data['titlestr'])
        #if preset_data['type'] == 'FX':
        #    self.show_fx_ctrls(0)
        #    self.show_fx_ctrls(1)
        # self.set_busy(False)

    def syx_receive(self, req_sysex, exp_len, window):
        tmp_dump = b''

        if self.midi_outdev and self.midi_indev:
            self.midi_outdev.send_message(req_sysex)
            midinow = time.time()

            while time.time() < (midinow + 2):
                if self.midi_indev.poll():
                    alsa_event = self.midi_indev.read(1)
                    if alsa_event:
                        event_type, data = alsa_event[0]

                        if event_type == 'PORT_UNSUBSCRIBED':
                            self.error(window, f"Error: MIDI connection '{self.midi_indev}' dropped.")
                            return b''

                        elif event_type == 'SYSEX':
                            tmp_dump += data
                            if data[-1] == 0xF7:  # Check if last byte is F7
                                if len(tmp_dump) == exp_len:
                                    break
                                else:
                                    tmp_dump = b''

        return tmp_dump

    def validate_pat_data(self, sysex, pattern, exp_len):
        if self.debug:
            logging.debug(f"received: [{sysex.hex()}]")

        # Check length
        length = len(sysex)
        if length != exp_len:
            return f"sysex length mismatch, received {length} bytes, expected {exp_len} bytes."

        # Check validity of sysex data
        if not re.match(pattern, sysex):
            return "invalid sysex data"

        # Calculate checksum
        calc_sum = self.calculate_checksum(sysex[8:exp_len-2])

        # Expected checksum
        syx_sum = sysex[exp_len-2]

        # Compare
        if calc_sum != syx_sum:
            return f"sysex checksum mismatch, received {syx_sum}, expected {calc_sum}."

        return "ok"

    def error(self, window, message):
        # Implement the logic to display an error message
        logging.error(message)
        # You can add GUI error handling here if needed

    def construct_sysex_message(self, preset_number):
        # Construct the message based on the preset number
        # Ensure the address and data bytes are correct
        return bytes([0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x18, 0x00, 0x20, preset_number, 0xF7])

        # @staticmethod
    def load_preset_old(self, midi_helper: Optional[MIDIHelper], preset_type: str, preset_num: int) -> None:
        """Load a preset using MIDI commands
        
        Args:
            midi_helper: MIDI helper instance
            preset_type: Type of preset (Analog, Digital 1, etc)
            preset_num: Preset number (1-based)
        """
        if not midi_helper:
            logging.error("No MIDI helper available")
            return

        try:
            logging.debug(f"Loading {preset_type} preset {preset_num}")
            
            # Get the appropriate area code for the synth type
            area = PresetType.get_area_code(preset_type)
            if area is None:
                logging.error(f"Unknown preset type: {preset_type}")
                return

            # First message - Set bank and parameters
            data = [0x18, 0x00, area, 0x06, 0x5F]
            checksum = PresetLoader.calculate_checksum(data)
            midi_helper.send_message([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                *data, checksum, 0xF7
            ])

            # Second message - Set additional parameters
            data = [0x18, 0x00, area, 0x07, 0x40]
            checksum = PresetLoader.calculate_checksum(data)
            midi_helper.send_message([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                *data, checksum, 0xF7
            ])

            # Third message - Set preset number (convert to 0-based index)
            data = [0x18, 0x00, area, 0x08, preset_num - 1]
            checksum = PresetLoader.calculate_checksum(data)
            midi_helper.send_message([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                *data, checksum, 0xF7
            ])

            # Send parameter messages only for Digital presets
            if preset_type in [PresetType.DIGITAL_1, PresetType.DIGITAL_2]:
                parameter_addresses = [0x00, 0x20, 0x21, 0x22, 0x50]
                for addr in parameter_addresses:
                    data = [0x19, 0x01, addr, 0x00, 0x00, 0x00, 0x00, 0x40]
                    checksum = PresetLoader.calculate_checksum(data)
                    midi_helper.send_message([
                        0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                        *data, checksum, 0xF7
                    ])
                    time.sleep(0.02)  # Small delay between messages

            logging.debug(f"Successfully loaded {preset_type} preset {preset_num}")
            
        except Exception as e:
            logging.error(f"Error loading {preset_type} preset: {str(e)}", exc_info=True)

    @staticmethod
    def request_current_parameters(midi_helper: Optional[MIDIHelper], preset_type: str) -> None:
        """Request current parameters from the synth
        
        Args:
            midi_helper: MIDI helper instance
            preset_type: Type of preset (Analog, Digital 1, etc)
        """
        if not midi_helper:
            logging.error("No MIDI helper available")
            return

        try:
            # Get the appropriate area code for the synth type
            area = PresetType.get_area_code(preset_type)
            if area is None:
                logging.error(f"Unknown preset type: {preset_type}")
                return

            # Request current program number
            data = [0x18, 0x00, area, 0x08]  # Address for current program number
            checksum = PresetLoader.calculate_checksum(data)
            midi_helper.send_message([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                *data, checksum, 0xF7
            ])

            # For Digital synths, request additional parameters
            if preset_type in [PresetType.DIGITAL_1, PresetType.DIGITAL_2]:
                parameter_addresses = [0x00, 0x20, 0x21, 0x22, 0x50]
                for addr in parameter_addresses:
                    data = [0x19, 0x01, addr]  # Address for parameter data
                    checksum = PresetLoader.calculate_checksum(data)
                    midi_helper.send_message([
                        0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                        *data, checksum, 0xF7
                    ])
                    time.sleep(0.02)  # Small delay between messages

        except Exception as e:
            logging.error(f"Error requesting parameters: {str(e)}", exc_info=True) 


    def read_pat_data(self, sysex, data_dict, n):
        length = len(sysex)

        for i in range(length):
            dv = sysex[i]
            if i in data_dict['transf64'][n]:
                data_dict['data'][n][i] = dv - 64
            elif i in data_dict['transf_01'][n]:
                data_dict['data'][n][i] = dv - 1
            elif i in data_dict['transf_10'][n]:
                data_dict['data'][n][i] = dv - 10
            elif i in data_dict['transf10'][n]:
                data_dict['data'][n][i] = (dv - 64) * 10
            elif i in data_dict['transf4'][n]:
                dv1 = sysex[i + 1]
                dv2 = sysex[i + 2]
                dv3 = sysex[i + 3]
                data_dict['data'][n][i + 1] = dv1
                data_dict['data'][n][i + 2] = dv2
                data_dict['data'][n][i + 3] = dv3
                tmpv = (4096 * dv) + (256 * dv1) + (16 * dv2) + dv3
                if data_dict['type'] == 'FX':
                    data_dict['data'][n][i] = tmpv - 32768
                else:
                    data_dict['data'][n][i] = tmpv
                i += 3
            else:
                data_dict['data'][n][i] = dv

        # Handle specific types
        if data_dict['type'] == 'AN':
            self.pdm_val['19420011'] = sync_notes[data_dict['data'][n][0x11]]
        elif data_dict['type'] in ['SN1', 'SN2']:
            msb = data_dict['msb']
            if n == 0:
                for tone_cat in tone_cats:
                    if tone_cat.startswith(f"{data_dict['data'][n][0x36]}:"):
                        self.pdm_val[f"{msb}0036"] = tone_cat
            elif n == 4:
                self.pdm_val[f"{msb}5005"] = sync_notes[data_dict['data'][n][0x05]]
            elif 0 < n < 4:
                lsb = n - 1
                self.pdm_val[f"{msb}2{lsb}1F"] = sync_notes[data_dict['data'][n][0x1F]]
                self.pdm_val[f"{msb}2{lsb}29"] = sync_notes[data_dict['data'][n][0x29]]
                wavenr = data_dict['data'][n][0x35]
                if wavenr > 160:
                    wavenr = 0
                    data_dict['data'][n][0x35] = wavenr
                self.pdm_val[f"{msb}2{lsb}35"] = PCMwaves[wavenr]
        elif data_dict['type'] == 'DR' and n > 0:
            lo = data_dict['addr'][n][2]
            hi = lo + 1
            lo_hex = f"{lo:02X}"
            hi_hex = f"{hi:02X}"
            self.pdm_val[f"1970{lo_hex}0D"] = mute_grp[data_dict['data'][n][0x0D]]
            self.pdm_val[f"1970{lo_hex}0F"] = coarse_tune[data_dict['data'][n][0x0F]]
            self.pdm_val[f"1970{lo_hex}11"] = rnd_pdepth[data_dict['data'][n][0x11]]
            for t in range(4):
                a = 29 * t
                wavenrL = data_dict['data'][n][0x27 + a]
                wavenrR = data_dict['data'][n][0x2B + a]
                if wavenrL > 453:
                    wavenrL = 0
                    data_dict['data'][n][0x27 + a] = wavenrL
                if wavenrR > 453:
                    wavenrR = 0
                    data_dict['data'][n][0x2B + a] = wavenrR
                self.pdm_val[self.addr(0x27 + a, lo_hex, hi_hex)] = DRMwaves[wavenrL]
                self.pdm_val[self.addr(0x2B + a, lo_hex, hi_hex)] = DRMwaves[wavenrR]
        elif data_dict['type'] == 'FX':
            if n == 0:
                self.pdm_val["18000200"] = fx_type[data_dict['data'][n][0]]
                self.pdm_val["1800022D"] = coarse_tune[data_dict['data'][n][45]]
                self.pdm_val["18000215"] = ratio[data_dict['data'][n][21]]
                self.pdm_val["18000219"] = comp_att[data_dict['data'][n][25]]
                self.pdm_val["1800021D"] = comp_rel[data_dict['data'][n][29]]
            elif n == 1:
                self.pdm_val["18000400"] = fx_type[data_dict['data'][n][0]]
                self.pdm_val["18000415"] = dly_notes[data_dict['data'][n][21]]
                self.pdm_val["18000419"] = dly_notes[data_dict['data'][n][25]]
            elif n == 2:
                self.pdm_val["18000610"] = dly_notes[data_dict['data'][n][16]]
                self.pdm_val["1800061C"] = hf_damp[data_dict['data'][n][28]]
            elif n == 3:
                self.pdm_val["18000803"] = rev_type[data_dict['data'][n][3]]
                self.pdm_val["1800080B"] = hf_damp[data_dict['data'][n][11]]
        elif data_dict['type'] == 'AR':
            self.pdm_val[18004005] = arp_type[data_dict['data'][n][0x05]]
            self.pdm_val[18004006] = arp_motif[data_dict['data'][n][0x06]]
        elif data_dict['type'] == 'VC':
            self.pdm_val[18000113] = vc_hpf[data_dict['data'][n][0x13]]
            self.pdm_val[18000108] = ap_key[data_dict['data'][n][0x08]]

    def addr(self, offset, lo, hi):
        # Implement the logic to calculate the address
        return f"{lo}{offset:02X}{hi}"

    # Other methods...
