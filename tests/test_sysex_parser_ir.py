from jdxi_editor.midi.data.address.address import RolandID
from jdxi_editor.midi.sysex.parser.sysex import (
    JDXiMessageFactory,
    JDXiMessageDeduplicator,
    JDXiMessageJsonAdapter,
    JDXiParameterBlock,
    JDXiParameterDecoder,
    JDXiParameterEncoder,
    JDXiParameterLayoutRegistry,
    ParameterLayoutBuilder,
    JDXiSysExParser,
    JDXiSysExMessage,
    JDXiSysExService,
    JsonSysExLogSink,
    MidiMessageFactory,
    ParameterAddressInfo,
    ParameterSpec,
    ParseResult,
    ParsedSysExMessage,
)
from jdxi_editor.midi.message.sysex.offset import (
    FieldSpec,
    JDXiSysExAddressOffset,
    JDXiSysExMessageLayout,
)


PARAMETER_SYSEX = bytes.fromhex(
    "F0 41 10 00 00 00 0E 12 19 01 00 00 10 7F 57 F7"
)
DIGITAL_COMMON_LONG_SYSEX = bytes.fromhex(
    "F0 41 10 00 00 00 0E 12 19 01 00 00 "
    "41 42 43 44 45 46 47 48 49 4A 4B 4C 64 "
    "03 F7"
)
DIGITAL2_MODIFY_SYSEX = bytes.fromhex(
    "F0 41 10 00 00 00 0E 12 19 21 50 00 00 55 00 00 F7"
)
IDENTITY_REQUEST = bytes([0xF0, 0x7E, 0x7F, 0x06, 0x01, 0xF7])
NON_JDXI_ROLAND_SYSEX = bytes.fromhex(
    "F0 41 10 00 00 00 0F 12 19 01 00 00 10 7F 56 F7"
)

EXPECTED_FIELD_NAMES = (
    "start",
    "roland_id",
    "device_id",
    "model_id",
    "command_id",
    "address",
    "tone_name",
    "value",
    "checksum",
    "end",
)


def test_field_specs_declare_stable_names():
    assert tuple(field.name for field in JDXiSysExMessageLayout.FIELDS) == (
        EXPECTED_FIELD_NAMES
    )


def test_field_spec_normalizes_offsets_inside_layout():
    data_len = len(PARAMETER_SYSEX)

    assert FieldSpec(1, 1, bytes).normalized_offset(data_len) == 1
    assert FieldSpec(-1, 1, bytes).normalized_offset(data_len) == data_len - 1
    assert FieldSpec(JDXiSysExAddressOffset, 4, bytes).normalized_offset(data_len) == 8
    assert FieldSpec(JDXiSysExAddressOffset.MSB, 1, bytes).normalized_offset(data_len) == 8


def test_field_spec_calculates_open_ended_ranges():
    field = FieldSpec(12, None, bytes)

    assert field.end_offset(len(PARAMETER_SYSEX)) == len(PARAMETER_SYSEX)


def test_field_validator_fails_clearly_in_strict_mode():
    field = FieldSpec(
        0,
        1,
        bytes,
        name="validated_start",
        validator=lambda raw: raw == b"\x00",
    )
    parser = JDXiSysExParser(PARAMETER_SYSEX, strict=True)

    try:
        parser._parse_field(field)
    except ValueError as ex:
        assert "Validation failed for field validated_start" in str(ex)
    else:
        raise AssertionError("strict field validation should raise")


def test_permissive_structured_fields_skip_unavailable_fields():
    parser = JDXiSysExParser(bytes([0xF0, 0xF7]))

    fields = parser.get_structured_fields()

    assert fields == {"start": bytes([0xF0]), "end": bytes([0xF7])}


def test_strict_structured_fields_raise_on_unavailable_fields():
    parser = JDXiSysExParser(bytes([0xF0, 0xF7]), strict=True)

    try:
        parser.get_structured_fields()
    except ValueError as ex:
        assert "roland_id" in str(ex)
    else:
        raise AssertionError("strict mode should raise on unavailable fields")


def test_parse_keeps_existing_dict_api(tmp_path):
    parser = JDXiSysExParser(PARAMETER_SYSEX)
    parser.log_folder = tmp_path

    parsed = parser.parse()

    assert isinstance(parsed, dict)
    assert parsed["ADDRESS"] == "12190100"
    assert parsed["TEMPORARY_AREA"] == "DIGITAL_SYNTH_1"
    assert parser.sysex_dict is parsed


def test_parse_accepts_universal_identity_request():
    parsed = JDXiSysExParser(IDENTITY_REQUEST).parse()

    assert parsed == {"type": "identity_request", "device_id": 0x7F}


def test_parse_rejects_non_jdxi_roland_parameter_message():
    parser = JDXiSysExParser(NON_JDXI_ROLAND_SYSEX)

    try:
        parser.parse()
    except ValueError as ex:
        assert "Not a JD-Xi SysEx message" in str(ex)
    else:
        raise AssertionError("non-JD-Xi Roland SysEx should be rejected")


def test_parse_does_not_write_json_log_by_default(tmp_path):
    parser = JDXiSysExParser(PARAMETER_SYSEX)
    parser.log_folder = tmp_path

    parser.parse()

    assert list(tmp_path.iterdir()) == []


def test_parse_invokes_optional_log_sink():
    captured = []
    parser = JDXiSysExParser(PARAMETER_SYSEX, log_sink=captured.append)

    parsed = parser.parse()

    assert captured == [parsed]


def test_json_sysex_log_sink_writes_when_opted_in(tmp_path):
    parser = JDXiSysExParser(
        PARAMETER_SYSEX,
        log_sink=JsonSysExLogSink(tmp_path),
    )

    parser.parse()

    log_file = tmp_path / "jdxi_tone_data_12190100.json"
    assert log_file.exists()
    assert '"TEMPORARY_AREA": "DIGITAL_SYNTH_1"' in log_file.read_text()


def test_parse_to_ir_returns_typed_parameter_message(tmp_path):
    parser = JDXiSysExParser(PARAMETER_SYSEX)
    parser.log_folder = tmp_path

    parsed = parser.parse_to_ir()

    assert isinstance(parsed, ParsedSysExMessage)
    assert parsed.raw == PARAMETER_SYSEX
    assert parsed.message_type == "parameter"
    assert parsed.roland_id == RolandID.ROLAND_ID
    assert parsed.device_id == RolandID.DEVICE_ID
    assert parsed.model_id == bytes([0x00, 0x00, 0x00, 0x0E])
    assert parsed.address == bytes([0x19, 0x01, 0x00, 0x00])
    assert parsed.data == bytes([0x10, 0x7F])
    assert parsed.checksum == 0x57
    assert parsed.valid_checksum is True


def test_message_factory_builds_parameter_domain_message():
    parsed = JDXiSysExParser(PARAMETER_SYSEX).parse_to_ir()

    message = JDXiMessageFactory.from_parsed(parsed)

    assert isinstance(message, JDXiSysExMessage)
    assert message.raw == PARAMETER_SYSEX
    assert message.message_type == "parameter"
    assert message.model_id == bytes([0x00, 0x00, 0x00, 0x0E])
    assert message.address == bytes([0x19, 0x01, 0x00, 0x00])
    assert message.payload == bytes([0x10, 0x7F])
    assert message.valid_checksum is True
    assert message.is_parameter is True
    assert message.is_identity is False
    assert message.identity_key == "0000000e:19010000"
    assert message.quality_score == (True, 2, len(PARAMETER_SYSEX))


def test_message_factory_builds_identity_domain_message():
    parsed = JDXiSysExParser(IDENTITY_REQUEST).parse_to_ir()

    message = JDXiMessageFactory.from_parsed(parsed)

    assert message.message_type == "identity_request"
    assert message.model_id is None
    assert message.address is None
    assert message.payload == bytes([0x7E, 0x7F, 0x06, 0x01])
    assert message.is_parameter is False
    assert message.is_identity is True
    assert message.identity_key == IDENTITY_REQUEST[:8].hex()


def test_message_deduplicator_keeps_latest_equal_quality_message():
    first = JDXiMessageFactory.from_parsed(JDXiSysExParser(PARAMETER_SYSEX).parse_to_ir())
    second = JDXiMessageFactory.from_parsed(
        JDXiSysExParser(PARAMETER_SYSEX).parse_to_ir()
    )

    deduplicated = JDXiMessageDeduplicator.deduplicate([first, second])

    assert deduplicated == [second]


def test_message_deduplicator_prefers_valid_checksum_over_latest_invalid():
    valid = JDXiMessageFactory.from_parsed(JDXiSysExParser(PARAMETER_SYSEX).parse_to_ir())
    corrupted = bytearray(PARAMETER_SYSEX)
    corrupted[-2] = 0x00
    invalid = JDXiMessageFactory.from_parsed(
        JDXiSysExParser(bytes(corrupted)).parse_to_ir()
    )

    deduplicated = JDXiMessageDeduplicator.deduplicate([valid, invalid])

    assert deduplicated == [valid]


def test_parse_to_result_returns_domain_message_on_success():
    result = JDXiSysExParser(PARAMETER_SYSEX).parse_to_result()

    assert isinstance(result, ParseResult)
    assert result.success is True
    assert result.errors == []
    assert result.raw == PARAMETER_SYSEX
    assert result.error_type is None
    assert result.message is not None
    assert result.message.identity_key == "0000000e:19010000"


def test_parse_to_result_returns_errors_without_raising():
    result = JDXiSysExParser(bytes([0x00, 0x01])).parse_to_result()

    assert result.success is False
    assert result.message is None
    assert result.errors == ["Invalid SysEx framing"]
    assert result.raw == bytes([0x00, 0x01])
    assert result.error_type == "ValueError"


def test_sysex_service_parses_domain_message():
    message = JDXiSysExService().parse(PARAMETER_SYSEX)

    assert isinstance(message, JDXiSysExMessage)
    assert message.identity_key == "0000000e:19010000"


def test_sysex_service_parse_result_keeps_errors():
    result = JDXiSysExService().parse_result(bytes([0x00, 0x01]))

    assert result.success is False
    assert result.errors == ["Invalid SysEx framing"]
    assert result.raw == bytes([0x00, 0x01])


def test_sysex_service_parse_stream_results_include_source_index():
    results = JDXiSysExService().parse_stream_results(
        [bytes([0x00, 0x01]), PARAMETER_SYSEX]
    )

    assert [result.source_index for result in results] == [0, 1]
    assert results[0].success is False
    assert results[1].success is True


def test_sysex_service_parse_stream_can_preserve_duplicates():
    messages = JDXiSysExService().parse_stream(
        [PARAMETER_SYSEX, PARAMETER_SYSEX],
        deduplicate=False,
    )

    assert len(messages) == 2
    assert messages[0].identity_key == messages[1].identity_key


def test_sysex_service_parse_stream_deduplicates_by_default():
    messages = JDXiSysExService().parse_stream([PARAMETER_SYSEX, PARAMETER_SYSEX])

    assert len(messages) == 1
    assert messages[0].identity_key == "0000000e:19010000"


def test_sysex_service_parse_stream_skips_invalid_messages():
    messages = JDXiSysExService().parse_stream([bytes([0x00, 0x01]), PARAMETER_SYSEX])

    assert len(messages) == 1
    assert messages[0].identity_key == "0000000e:19010000"


def test_message_json_adapter_serializes_domain_message():
    message = JDXiSysExService().parse(PARAMETER_SYSEX)

    serialized = JDXiMessageJsonAdapter.to_dict(message)

    assert serialized == {
        "message_type": "parameter",
        "identity_key": "0000000e:19010000",
        "model_id": "0000000e",
        "command_id": "DT1",
        "address": "19010000",
        "payload": "107f",
        "valid_checksum": True,
        "checksum": 0x57,
        "tone_name": None,
    }
    assert '"identity_key": "0000000e:19010000"' in JDXiMessageJsonAdapter.to_json(
        message
    )


def test_parameter_decoder_decodes_known_digital_common_block():
    message = JDXiMessageFactory.from_parsed(
        JDXiSysExParser(PARAMETER_SYSEX).parse_to_ir()
    )

    block = JDXiParameterDecoder.decode(message)

    assert isinstance(block, JDXiParameterBlock)
    assert block.address == bytes([0x19, 0x01, 0x00, 0x00])
    assert block.raw_data == bytes([0x10, 0x7F])
    assert block.block_name == "digital_synth_common"
    assert block.parameters == {
        "TONE_NAME_1": 0x10,
        "TONE_NAME_2": 0x7F,
    }


def test_generated_layout_decodes_existing_parameter_class_specs():
    message = JDXiMessageFactory.from_parsed(
        JDXiSysExParser(DIGITAL_COMMON_LONG_SYSEX).parse_to_ir()
    )

    block = JDXiParameterDecoder.decode(message)

    assert block.block_name == "digital_synth_common"
    assert block.parameters["TONE_NAME_1"] == 0x41
    assert block.parameters["TONE_NAME_12"] == 0x4C
    assert block.parameters["TONE_LEVEL"] == 0x64


def test_registry_decodes_digital2_modify_layout():
    message = JDXiMessageFactory.from_parsed(
        JDXiSysExParser(DIGITAL2_MODIFY_SYSEX).parse_to_ir()
    )

    block = JDXiParameterDecoder.decode(message)

    assert block.block_name == "digital_synth_modify"
    assert block.parameters["ATTACK_TIME_INTERVAL_SENS"] == 0x55
    assert block.address_info is not None
    assert block.address_info.display_name == "Temporary Tone / Digital Synth 2 / Modify"


def test_parameter_registry_exposes_semantic_address_info():
    info = JDXiParameterLayoutRegistry.get_address_info(bytes([0x19, 0x01, 0x00, 0x00]))

    assert info == ParameterAddressInfo(
        address=bytes([0x19, 0x01, 0x00, 0x00]),
        area="temporary_tone",
        part="digital_synth_1",
        block="common",
        display_name="Temporary Tone / Digital Synth 1 / Common",
        layout_name="digital_synth_common",
    )


def test_parameter_registry_lists_known_semantic_addresses():
    infos = JDXiParameterLayoutRegistry.list_address_info()

    assert [info.display_name for info in infos] == [
        "Temporary Tone / Digital Synth 1 / Common",
        "Temporary Tone / Digital Synth 1 / Modify",
        "Temporary Tone / Digital Synth 2 / Common",
        "Temporary Tone / Digital Synth 2 / Modify",
    ]


def test_parameter_registry_can_register_custom_address_info():
    class TestLayout:
        block_name = "custom"
        PARAMETERS = ()

    address = bytes([0x19, 0x7D, 0x00, 0x00])
    info = ParameterAddressInfo(
        address=address,
        area="temporary_tone",
        part="test",
        block="custom",
        display_name="Temporary Tone / Test / Custom",
        layout_name="custom",
    )

    JDXiParameterLayoutRegistry.register(address, TestLayout, address_info=info)

    assert JDXiParameterLayoutRegistry.get_layout(address) is TestLayout
    assert JDXiParameterLayoutRegistry.get_address_info(address) == info


def test_parameter_layout_builder_sorts_specs_by_address():
    class ExampleParams:
        SECOND = type("Spec", (), {"address": 2})()
        FIRST = type("Spec", (), {"address": 1})()

    layout = ParameterLayoutBuilder.from_parameter_class(ExampleParams, "example")

    assert [spec.name for spec in layout.PARAMETERS] == ["FIRST", "SECOND"]


def test_parameter_decoder_returns_unknown_block_for_unregistered_address():
    message = JDXiSysExMessage(
        raw=b"\xF0\xF7",
        message_type="parameter",
        model_id=bytes([0x00, 0x00, 0x00, 0x0E]),
        command_id=None,
        address=bytes([0x19, 0x7F, 0x00, 0x00]),
        payload=bytes([0x01, 0x02]),
        valid_checksum=True,
    )

    block = JDXiParameterDecoder.decode(message)

    assert block == JDXiParameterBlock(
        address=bytes([0x19, 0x7F, 0x00, 0x00]),
        raw_data=bytes([0x01, 0x02]),
        parameters={},
        block_name="unknown",
    )


def test_parameter_decoder_ignores_non_parameter_messages():
    identity = JDXiMessageFactory.from_parsed(
        JDXiSysExParser(IDENTITY_REQUEST).parse_to_ir()
    )

    assert JDXiParameterDecoder.decode(identity) is None


def test_parameter_encoder_updates_known_block_payload():
    block = JDXiParameterBlock(
        address=bytes([0x19, 0x01, 0x00, 0x00]),
        raw_data=bytes([0x10, 0x7F]),
        parameters={"TONE_NAME_2": 0x41},
        block_name="digital_synth_common",
    )

    encoded = JDXiParameterEncoder.encode(block)

    assert encoded == bytes([0x10, 0x41])


def test_parameter_encoder_returns_raw_data_for_unknown_layout():
    block = JDXiParameterBlock(
        address=bytes([0x19, 0x7F, 0x00, 0x00]),
        raw_data=bytes([0x01, 0x02]),
        parameters={"anything": 0x7F},
        block_name="unknown",
    )

    assert JDXiParameterEncoder.encode(block) == bytes([0x01, 0x02])


def test_parameter_encoder_updates_bitfield_values():
    class TestBitfieldLayout:
        block_name = "test_bitfield"
        PARAMETERS = (
            ParameterSpec("low_bits", 0, 1, bitmask=0b00000111),
            ParameterSpec("high_bits", 0, 1, bitmask=0b00111000, shift=3),
        )

    address = bytes([0x19, 0x7E, 0x00, 0x00])
    JDXiParameterLayoutRegistry.register(address, TestBitfieldLayout)
    block = JDXiParameterBlock(
        address=address,
        raw_data=bytes([0]),
        parameters={"low_bits": 0b101, "high_bits": 0b011},
        block_name="test_bitfield",
    )

    assert JDXiParameterEncoder.encode(block) == bytes([0b00011101])


def test_parse_to_ir_does_not_write_json_log(tmp_path):
    parser = JDXiSysExParser(PARAMETER_SYSEX)
    parser.log_folder = tmp_path

    parser.parse_to_ir()

    assert list(tmp_path.iterdir()) == []


def test_parse_to_ir_marks_invalid_checksum():
    corrupted = bytearray(PARAMETER_SYSEX)
    corrupted[-2] = 0x00

    parsed = JDXiSysExParser(bytes(corrupted)).parse_to_ir()

    assert parsed.message_type == "parameter"
    assert parsed.valid_checksum is False


def test_parse_to_ir_handles_universal_identity_request():
    parsed = JDXiSysExParser(IDENTITY_REQUEST).parse_to_ir()

    assert parsed.message_type == "identity_request"
    assert parsed.roland_id is None
    assert parsed.device_id == 0x7F
    assert parsed.valid_checksum is True


def test_parse_to_ir_rejects_non_jdxi_roland_parameter_message():
    parser = JDXiSysExParser(NON_JDXI_ROLAND_SYSEX)

    try:
        parser.parse_to_ir()
    except ValueError as ex:
        assert "Not a JD-Xi SysEx message" in str(ex)
    else:
        raise AssertionError("non-JD-Xi Roland SysEx should be rejected")


def test_midi_message_factory_handles_program_change():
    message = MidiMessageFactory.from_bytes([0xC2, 0x05])

    assert message.type == "program_change"
    assert message.channel == 2
    assert message.program == 5


def test_parser_convert_to_mido_message_delegates_to_factory():
    parser = JDXiSysExParser()

    message = parser.convert_to_mido_message([0xB1, 0x07, 0x40])

    assert message.type == "control_change"
    assert message.channel == 1
    assert message.control == 7
    assert message.value == 64
