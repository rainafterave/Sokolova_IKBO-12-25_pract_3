"""Exercise real CLI processes, output files and failure handling."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_vectors import DATA

PROJECT = Path(__file__).resolve().parents[2]
ENTRY = PROJECT / "src/main.py"
EXAMPLES = PROJECT / "src/examples"


def command(*arguments):
    """Run the application outside the repository working directory."""
    return subprocess.run(
        [sys.executable, str(ENTRY), *map(str, arguments)],
        capture_output=True, cwd=PROJECT.parent,
    )


class CommandTests(unittest.TestCase):
    """Test every public mode and protect outputs when an operation fails."""

    def test_specification_cli_and_test_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "sub/program.bin"
            result = command(
                "assemble", EXAMPLES / "specification.asm",
                "-o", binary, "--test",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(binary.read_bytes(), bytes.fromhex(
                "87 17 00 00 1A 72 60 00 00 15 08 00 00",
            ))
            self.assertIn(b"Assembled instructions: 4", result.stdout)
            self.assertIn(b"0x87, 0x17, 0x00, 0x00", result.stdout)

    def test_three_vectors_export_exact_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, (left, right) in DATA.items():
                with self.subTest(name=name):
                    binary, dump = root / "program.bin", root / "dump.json"
                    assembled = command(
                        "assemble", EXAMPLES / "vectors" / f"{name}.asm",
                        "-o", binary,
                    )
                    self.assertEqual(assembled.returncode, 0, assembled.stderr)
                    result = command(
                        "run", binary, "-o", dump, "--start", 288, "--end", 295,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    values = json.loads(dump.read_text(encoding="utf-8"))
                    self.assertEqual(list(values.values()), [
                        a + b for a, b in zip(left, right)
                    ])

    def test_bad_source_preserves_existing_binary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, binary = root / "bad.asm", root / "old.bin"
            source.write_text("ACC = -1;", encoding="utf-8")
            binary.write_bytes(b"original")
            result = command("assemble", source, "-o", binary)
            self.assertEqual(result.returncode, 1)
            self.assertIn(b"line 1", result.stderr)
            self.assertEqual(binary.read_bytes(), b"original")

    def test_runtime_errors_preserve_previous_dump(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary, dump = root / "bad.bin", root / "old.json"
            binary.write_bytes(b"\x07")
            dump.write_bytes(b"original")
            result = command(
                "run", binary, "-o", dump, "--start", 0, "--end", 10,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn(b"truncated", result.stderr)
            self.assertEqual(dump.read_bytes(), b"original")

    def test_dump_range_arguments_are_validated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary, dump = root / "code.bin", root / "result.json"
            binary.write_bytes(bytes.fromhex("07 00 00 00"))
            for start, end in [(-1, 1), (5, 2), (0, 1048576)]:
                with self.subTest(start=start, end=end):
                    result = command(
                        "run", binary, "-o", dump,
                        "--start", start, "--end", end,
                    )
                    self.assertEqual(result.returncode, 1)
                    self.assertFalse(dump.exists())

    def test_missing_file_and_required_arguments(self):
        self.assertEqual(command().returncode, 2)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = command(
                "assemble", root / "missing.asm", "-o", root / "out.bin",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn(b"Error:", result.stderr)

    def test_output_path_is_a_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            result = command(
                "assemble", EXAMPLES / "specification.asm", "-o", directory,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(list(Path(directory).iterdir()), [])
