"""Check the specified fields and reject malformed assembly programs."""

import unittest

from assembler import parse_program
from instructions import ADD, LOAD, READ, STORE, Instruction, MachineError


class AssemblerTests(unittest.TestCase):
    """Validate every instruction form and the field boundaries."""

    def test_specification_fields(self):
        source = (
            "ACC = 188;\nACC = MEM[ACC];\n"
            "MEM[771] = ACC;\nACC = ACC + MEM[64];"
        )
        fields = [item.fields() for item in parse_program(source)]
        self.assertEqual(fields, [
            {"A": 7, "B": 188}, {"A": 26},
            {"A": 18, "B": 771}, {"A": 21, "B": 64},
        ])

    def test_whitespace_and_comments(self):
        source = "# comment\n ACC=0; # load\nACC= MEM [ ACC ];"
        self.assertEqual(
            parse_program(source), [Instruction(LOAD, 0), Instruction(READ)],
        )

    def test_maximum_fields(self):
        self.assertEqual(
            parse_program(
                "ACC = 8388607;\nMEM[1048575] = ACC;\n"
                "ACC = ACC + MEM[1048575];"
            ),
            [Instruction(LOAD, 8388607), Instruction(STORE, 1048575),
             Instruction(ADD, 1048575)],
        )

    def test_invalid_syntax_and_ranges(self):
        for source in [
            "", "# comment", "ACC = -1;", "ACC = 1.5;", "ACC = 1",
            "acc = 1;", "ACC = 8388608;", "MEM[1048576] = ACC;",
            "ACC = ACC + MEM[1048576];", "ACC = MEM[4];",
            "ACC = 1; ACC = 2;",
        ]:
            with self.subTest(source=source):
                with self.assertRaises(MachineError):
                    parse_program(source)

    def test_error_reports_line(self):
        with self.assertRaisesRegex(MachineError, "line 3"):
            parse_program("# header\nACC = 1;\nbroken")
