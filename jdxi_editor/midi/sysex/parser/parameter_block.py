"""
Parameter block decoding and encoding for parsed JD-Xi SysEx messages.
"""

from dataclasses import dataclass
from typing import Any, Callable, Optional

from jdxi_editor.midi.data.address.address import (
    JDXiSysExOffsetSuperNATURALLMB,
    JDXiSysExOffsetTemporaryToneUMB,
)
from jdxi_editor.midi.data.parameter.digital.common import DigitalCommonParam
from jdxi_editor.midi.data.parameter.digital.modify import DigitalModifyParam
from jdxi_editor.midi.sysex.parser.model import JDXiSysExMessage


@dataclass(frozen=True, slots=True)
class ParameterSpec:
    name: str
    offset: int
    length: int
    parser: Optional[Callable[[bytes], Any]] = None
    bitmask: Optional[int] = None
    shift: int = 0


@dataclass(slots=True)
class JDXiParameterBlock:
    address: bytes
    raw_data: bytes
    parameters: dict[str, Any]
    block_name: Optional[str] = None
    address_info: Optional["ParameterAddressInfo"] = None


@dataclass(frozen=True, slots=True)
class ParameterAddressInfo:
    address: bytes
    area: str
    part: str
    block: str
    display_name: str
    layout_name: Optional[str] = None


class ParameterLayoutBuilder:
    """Build decoder layouts from existing JD-Xi parameter classes."""

    @staticmethod
    def from_parameter_class(parameter_cls: Any, block_name: str) -> Any:
        specs = []
        for name, value in vars(parameter_cls).items():
            address = getattr(value, "address", None)
            if not isinstance(address, int):
                continue
            specs.append(ParameterSpec(name, address, 1, lambda raw: raw[0]))

        specs.sort(key=lambda spec: spec.offset)
        return type(
            f"{parameter_cls.__name__}GeneratedLayout",
            (),
            {"block_name": block_name, "PARAMETERS": tuple(specs)},
        )


class JDXiParameterLayoutRegistry:
    _digital_common_layout = ParameterLayoutBuilder.from_parameter_class(
        DigitalCommonParam, "digital_synth_common"
    )
    _digital_modify_layout = ParameterLayoutBuilder.from_parameter_class(
        DigitalModifyParam, "digital_synth_modify"
    )
    _digital_1_common_address = bytes(
        [
            0x19,
            JDXiSysExOffsetTemporaryToneUMB.DIGITAL_SYNTH_1,
            JDXiSysExOffsetSuperNATURALLMB.COMMON,
            0x00,
        ]
    )
    _digital_2_common_address = bytes(
        [
            0x19,
            JDXiSysExOffsetTemporaryToneUMB.DIGITAL_SYNTH_2,
            JDXiSysExOffsetSuperNATURALLMB.COMMON,
            0x00,
        ]
    )
    _digital_1_modify_address = bytes(
        [
            0x19,
            JDXiSysExOffsetTemporaryToneUMB.DIGITAL_SYNTH_1,
            JDXiSysExOffsetSuperNATURALLMB.MODIFY,
            0x00,
        ]
    )
    _digital_2_modify_address = bytes(
        [
            0x19,
            JDXiSysExOffsetTemporaryToneUMB.DIGITAL_SYNTH_2,
            JDXiSysExOffsetSuperNATURALLMB.MODIFY,
            0x00,
        ]
    )
    _registry: dict[bytes, Any] = {
        _digital_1_common_address: _digital_common_layout,
        _digital_2_common_address: _digital_common_layout,
        _digital_1_modify_address: _digital_modify_layout,
        _digital_2_modify_address: _digital_modify_layout,
    }
    _address_info: dict[bytes, ParameterAddressInfo] = {
        _digital_1_common_address: ParameterAddressInfo(
            address=_digital_1_common_address,
            area="temporary_tone",
            part="digital_synth_1",
            block="common",
            display_name="Temporary Tone / Digital Synth 1 / Common",
            layout_name="digital_synth_common",
        ),
        _digital_2_common_address: ParameterAddressInfo(
            address=_digital_2_common_address,
            area="temporary_tone",
            part="digital_synth_2",
            block="common",
            display_name="Temporary Tone / Digital Synth 2 / Common",
            layout_name="digital_synth_common",
        ),
        _digital_1_modify_address: ParameterAddressInfo(
            address=_digital_1_modify_address,
            area="temporary_tone",
            part="digital_synth_1",
            block="modify",
            display_name="Temporary Tone / Digital Synth 1 / Modify",
            layout_name="digital_synth_modify",
        ),
        _digital_2_modify_address: ParameterAddressInfo(
            address=_digital_2_modify_address,
            area="temporary_tone",
            part="digital_synth_2",
            block="modify",
            display_name="Temporary Tone / Digital Synth 2 / Modify",
            layout_name="digital_synth_modify",
        ),
    }

    @classmethod
    def register(
        cls,
        address: bytes,
        layout: Any,
        address_info: Optional[ParameterAddressInfo] = None,
    ) -> None:
        address = bytes(address)
        cls._registry[address] = layout
        if address_info is not None:
            cls._address_info[address] = address_info

    @classmethod
    def get_layout(cls, address: Optional[bytes]) -> Optional[Any]:
        if address is None:
            return None
        return cls._registry.get(bytes(address))

    @classmethod
    def get_address_info(cls, address: Optional[bytes]) -> Optional[ParameterAddressInfo]:
        if address is None:
            return None
        return cls._address_info.get(bytes(address))

    @classmethod
    def list_address_info(cls) -> tuple[ParameterAddressInfo, ...]:
        return tuple(cls._address_info[address] for address in sorted(cls._address_info))


class JDXiParameterDecoder:
    """Decode domain messages into address-specific parameter blocks."""

    @staticmethod
    def decode(message: JDXiSysExMessage) -> Optional[JDXiParameterBlock]:
        if not message.is_parameter or message.address is None:
            return None

        layout = JDXiParameterLayoutRegistry.get_layout(message.address)
        if layout is None:
            return JDXiParameterBlock(
                address=message.address,
                raw_data=message.payload,
                parameters={},
                block_name="unknown",
                address_info=JDXiParameterLayoutRegistry.get_address_info(
                    message.address
                ),
            )

        parameters: dict[str, Any] = {}
        for spec in layout.PARAMETERS:
            if message.payload is not None:
                raw = message.payload[spec.offset : spec.offset + spec.length]
                if len(raw) < spec.length:
                    continue
                parameters[spec.name] = JDXiParameterDecoder._decode_spec(spec, raw)

        return JDXiParameterBlock(
            address=message.address,
            raw_data=message.payload,
            parameters=parameters,
            block_name=getattr(layout, "block_name", layout.__name__),
            address_info=JDXiParameterLayoutRegistry.get_address_info(message.address),
        )

    @staticmethod
    def _decode_spec(spec: ParameterSpec, raw: bytes) -> Any:
        if spec.bitmask is not None:
            return (raw[0] & spec.bitmask) >> spec.shift
        if spec.parser is not None:
            return spec.parser(raw)
        return raw


class JDXiParameterEncoder:
    """Encode edited parameter blocks back into payload bytes."""

    @staticmethod
    def encode(block: JDXiParameterBlock) -> bytes:
        layout = JDXiParameterLayoutRegistry.get_layout(block.address)
        if layout is None:
            return block.raw_data

        data = bytearray(block.raw_data)
        for spec in layout.PARAMETERS:
            if spec.name not in block.parameters:
                continue
            JDXiParameterEncoder._encode_spec(data, spec, block.parameters[spec.name])
        return bytes(data)

    @staticmethod
    def _encode_spec(data: bytearray, spec: ParameterSpec, value: Any) -> None:
        end = spec.offset + spec.length
        if end > len(data):
            data.extend(b"\x00" * (end - len(data)))

        if spec.bitmask is not None:
            byte_value = data[spec.offset]
            byte_value &= ~spec.bitmask
            byte_value |= (int(value) << spec.shift) & spec.bitmask
            data[spec.offset] = byte_value
            return

        if isinstance(value, (bytes, bytearray)):
            encoded = bytes(value)[: spec.length]
        elif spec.length == 1:
            encoded = bytes([int(value) & 0xFF])
        else:
            encoded = int(value).to_bytes(spec.length, byteorder="big")
        data[spec.offset:end] = encoded.ljust(spec.length, b"\x00")
