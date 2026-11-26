"""Match every supplied byte sequence and exercise binary boundaries."""

import unittest

from codec import decode_at, encode, encode_program
from instructions import ADD, LOAD, READ, STORE, Instruction, MachineError

SPECIFICATION = (
    (Instruction(LOAD, 188), bytes.fromhex("87 17 00 00")),
    (Instruction(READ), bytes.fromhex("1A")),
    (Instruction(STORE, 771), bytes.fromhex("72 60 00 00")),
    (Instruction(ADD, 64), bytes.fromhex("15 08 00 00")),
)


class CodecTests(unittest.TestCase):
    """Check exact byte order, lengths, limits and malformed binaries."""

    def test_specification_bytes_and_decoding(self):
        for instruction, expected in SPECIFICATION:
            with self.subTest(instruction=instruction):
                self.assertEqual(encode(instruction), expected)
                self.assertEqual(
                    decode_at(expected), (instruction, len(expected)),
                )

    def test_variable_length_program(self):
        instructions = [instruction for instruction, _ in SPECIFICATION]
        code = encode_program(instructions)
        self.assertEqual(len(code), 13)
        offset = 0
        for expected in instructions:
            decoded, size = decode_at(code, offset)
            self.assertEqual(decoded, expected)
            offset += size
        self.assertEqual(offset, len(code))

    def test_round_trip_limits(self):
        for instruction in [
            Instruction(LOAD, 0), Instruction(LOAD, 8388607),
            Instruction(STORE, 1048575), Instruction(ADD, 1048575),
        ]:
            with self.subTest(instruction=instruction):
                self.assertEqual(decode_at(encode(instruction))[0], instruction)

    def test_reject_unknown_truncated_and_reserved(self):
        for code in [
            b"", b"\x00", b"\x07", b"\x1a\x07",
            bytes.fromhex("07 00 00 10"), bytes.fromhex("12 00 00 02"),
            b"\x3a",
        ]:
            with self.subTest(code=code):
                offset = 1 if code == b"\x1a\x07" else 0
                with self.assertRaises(MachineError):
                    decode_at(code, offset)

    def test_reject_invalid_intermediate_fields(self):
        for instruction in [
            Instruction(0), Instruction(READ, 1), Instruction(LOAD),
            Instruction(LOAD, -1), Instruction(STORE, 1048576),
            Instruction(ADD, True),
        ]:
            with self.subTest(instruction=instruction):
                with self.assertRaises(MachineError):
                    encode(instruction)
