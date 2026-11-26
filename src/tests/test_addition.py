"""Verify accumulator addition and saving arithmetic results to memory."""

import unittest

from machine import VirtualMachine
from assembler import parse_program
from codec import encode_program
from instructions import MachineError
from test_machine import EXAMPLES, execute


class AdditionTests(unittest.TestCase):
    """Cover normal arithmetic, zero, large values and invalid addresses."""

    def test_addition_program_saves_result(self):
        source = (EXAMPLES / "addition.asm").read_text(encoding="utf-8")
        machine = execute(source)
        self.assertEqual(
            machine.dump(256, 258), {"256": 12, "257": 30, "258": 42},
        )
        self.assertEqual(machine.accumulator, 42)

    def test_addition_to_zero_initialized_memory(self):
        machine = execute("ACC = 17;\nACC = ACC + MEM[256];")
        self.assertEqual(machine.accumulator, 17)

    def test_no_implicit_arithmetic_truncation(self):
        machine = execute(
            "ACC = 8388607;\nMEM[256] = ACC;\nACC = ACC + MEM[256];"
        )
        self.assertEqual(machine.accumulator, 16777214)

    def test_addition_address_is_checked(self):
        code = encode_program(parse_program("ACC = ACC + MEM[256];"))
        machine = VirtualMachine(code, memory_size=64)
        with self.assertRaisesRegex(MachineError, "out of bounds"):
            machine.run()
