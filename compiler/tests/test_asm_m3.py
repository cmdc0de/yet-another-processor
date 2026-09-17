"""Assembler m3 tests. Run from repo root: python3 -m unittest compiler.tests.test_asm_m3"""

import unittest

from compiler.asm import AsmError, assemble_source
from compiler.yap1 import unpack
from compiler.yap_isa import unpack_r


class TestAsmM3(unittest.TestCase):
    def test_COMPILER_012(self):
        image = unpack(assemble_source(".word 0x12345678\n"))
        self.assertEqual(list(image.payload), [0x78, 0x56, 0x34, 0x12])
        image = unpack(assemble_source(".byte 1 2\n"))
        self.assertEqual(list(image.payload), [1, 2])
        image = unpack(assemble_source(".byte 1,2\n"))
        self.assertEqual(list(image.payload), [1, 2])
        image = unpack(assemble_source(".half 0x80FF\n"))
        self.assertEqual(list(image.payload), [0xFF, 0x80])
        with self.assertRaises(AsmError):
            assemble_source(".half 1\n.word 0\n")

    def test_COMPILER_013(self):
        image = unpack(assemble_source(".byte 1\n.align 2\n.word 0\n"))
        self.assertEqual(image.payload[0], 1)
        self.assertEqual(image.payload[1:4], b"\x00\x00\x00")
        self.assertEqual(image.payload[4:8], b"\x00\x00\x00\x00")
        self.assertEqual(len(image.payload), 8)

    def test_COMPILER_014(self):
        image = unpack(assemble_source(".equ N, 4\nlw t0, N(sp)\n"))
        fields = unpack_r(int.from_bytes(image.payload, "little"))
        self.assertEqual(fields["imm16"], 4)
        with self.assertRaises(AsmError):
            assemble_source(".equ N, 1\n.equ N, 1\n")


if __name__ == "__main__":
    unittest.main()
