"""Verify all eight result cells for three different vector data sets."""

import unittest

from test_machine import EXAMPLES, execute

DATA = {
    "ascending": (
        [1, 2, 3, 4, 5, 6, 7, 8], [8, 7, 6, 5, 4, 3, 2, 1],
    ),
    "sparse": (
        [0, 0, 5, 0, 0, 10, 0, 1], [3, 0, 0, 7, 0, 0, 2, 0],
    ),
    "large": (
        [8388607, 1000000, 2000000, 3000000, 0, 1, 42, 5000000],
        [1, 2000000, 3000000, 4000000, 8388607, 0, 58, 5000000],
    ),
}


class VectorTests(unittest.TestCase):
    """Test the complete assemble/decode/execute path for each vector."""

    def test_three_vector_programs(self):
        for name, (left, right) in DATA.items():
            with self.subTest(program=name):
                path = EXAMPLES / "vectors" / f"{name}.asm"
                machine = execute(path.read_text(encoding="utf-8"))
                expected = [a + b for a, b in zip(left, right)]
                self.assertEqual(machine.memory[256:264], left)
                self.assertEqual(machine.memory[272:280], right)
                self.assertEqual(machine.memory[288:296], expected)
                self.assertEqual(
                    machine.dump(288, 295),
                    {str(288 + i): value
                     for i, value in enumerate(expected)},
                )
