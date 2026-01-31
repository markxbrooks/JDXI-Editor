from picomidi.core.parameter.factory import AddressFactory

from jdxi_editor.midi.data.parameter.address.name import ParameterAddressName

parameter_address_table = [  # must be 3-byte addresses
    (ParameterAddressName.SETUP, "01 00 00 00"),
    (ParameterAddressName.SYSTEM, "02 00 00 00"),
    (ParameterAddressName.TEMPORARY_PROGRAM, "18 00 00 00"),
    (ParameterAddressName.TEMPORARY_TONE_DIGITAL1, "19 00 00 00"),
    (ParameterAddressName.TEMPORARY_TONE_DIGITAL2, "19 20 00 00"),
    (ParameterAddressName.TEMPORARY_TONE_ANALOG, "19 40 00 00"),
    (ParameterAddressName.TEMPORARY_DRUM_KIT, "19 60 00 00"),
]
PARAMETER_ADDRESS_TABLE = {
    name: AddressFactory.from_str(address) for name, address in parameter_address_table
}
