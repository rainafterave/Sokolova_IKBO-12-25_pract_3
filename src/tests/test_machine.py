"""Verify basic execution and genuinely shared code and data memory."""

from pathlib import Path
import unittest

from assembler import parse_program
from codec import encode_program
from instructions import MachineError
from machine import VirtualMachine

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def execute(source):
    """Assemble source and execute the real fetch/decode cycle."""
    return VirtualMachine(encode_program(parse_program(source))).run()


class MemoryTests(unittest.TestCase):
    """Exercise immediate loads, indirect reads, stores and invalid access."""

    def test_load_store_and_indirect_read(self):
        machine = execute(
            "ACC = 188;\nMEM[256] = ACC;\nACC = 256;\nACC = MEM[ACC];"
        )
        self.assertEqual(machine.accumulator, 188)
        self.assertEqual(machine.dump(256, 257), {"256": 188, "257": 0})

    def test_copy_array(self):
        machine = execute((EXAMPLES / "copy.asm").read_text(encoding="utf-8"))
        self.assertEqual(
            machine.memory[256:264], machine.memory[272:280],
        )
        self.assertEqual(machine.memory[272:280], [3, 1, 4, 1, 5, 9, 2, 6])

    def test_code_can_be_read_as_data(self):
        machine = execute("ACC = 0;\nACC = MEM[ACC];")
        self.assertEqual(machine.accumulator, 7)

    def test_code_writes_affect_later_fetch(self):
        machine = execute("ACC = 39;\nMEM[8] = ACC;\nACC = 0;")
        self.assertEqual(machine.accumulator, 1)
        self.assertEqual(machine.memory[8], 39)

    def test_invalid_indirect_addresses(self):
        for address in [1048576, 8388607]:
            with self.subTest(address=address):
                with self.assertRaisesRegex(MachineError, "out of bounds"):
                    execute(f"ACC = {address};\nACC = MEM[ACC];")

    def test_corrupt_self_modified_code(self):
        for value in [0, 300]:
            with self.subTest(value=value):
                with self.assertRaises(MachineError):
                    execute(f"ACC = {value};\nMEM[8] = ACC;\nACC = 0;")

    def test_invalid_binary_and_memory_size(self):
        for code in [b"", b"\x07", b"\x00"]:
            with self.subTest(code=code):
                with self.assertRaises(MachineError):
                    VirtualMachine(code).run()
        with self.assertRaises(MachineError):
            VirtualMachine(b"\x1a", memory_size=0)
        with self.assertRaises(MachineError):
            VirtualMachine(b"\x07" * 4, memory_size=1)

    def test_invalid_dump_ranges(self):
        machine = execute("ACC = 1;")
        for start, end in [(-1, 1), (1, 0), (0, 1048576)]:
            with self.subTest(start=start, end=end):
                with self.assertRaises(MachineError):
                    machine.dump(start, end)
