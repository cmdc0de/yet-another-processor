"""Assembler m2 tests. Run from repo root: python3 -m unittest compiler.tests.test_asm_m2"""

import unittest

from compiler.asm import AsmError, assemble_ex, assemble_source
from compiler.yap1 import unpack
from compiler.yap_isa import Cpu, assemble as isa_assemble, unpack_r


class TestAsmM2(unittest.TestCase):
    def test_COMPILER_008(self):
        data, symbols = assemble_ex("loop: nop\nj loop\n")
        self.assertEqual(symbols["loop"], 0)
        image = unpack(data)
        nop = isa_assemble("nop").to_bytes(4, "little")
        self.assertEqual(image.payload[:4], nop)

    def test_COMPILER_009(self):
        data, _ = assemble_ex("nop\nloop: nop\nj loop\n")
        image = unpack(data)
        jword = int.from_bytes(image.payload[8:12], "little")
        self.assertEqual(unpack_r(jword)["opcode"], 0b000010)
        self.assertEqual(unpack_r(jword)["target26"], 4 >> 2)
        data, _ = assemble_ex("cmp one, one\nbeq loop\nloop: nop\n")
        image = unpack(data)
        cpu = Cpu()
        cpu.mem_store(0, image.payload)
        cpu.step(int.from_bytes(image.payload[0:4], "little"))
        cpu.step(int.from_bytes(image.payload[4:8], "little"))
        self.assertEqual(cpu.pc, 8)

    def test_COMPILER_010(self):
        data, symbols = assemble_ex("j loop\nloop: halt\n")
        self.assertEqual(symbols["loop"], 4)
        image = unpack(data)
        jword = int.from_bytes(image.payload[0:4], "little")
        self.assertEqual(unpack_r(jword)["target26"], 4 >> 2)
        halt = isa_assemble("halt").to_bytes(4, "little")
        self.assertEqual(image.payload[4:8], halt)

    def test_COMPILER_011(self):
        data = assemble_source(".org 0x80\nhalt\n")
        image = unpack(data)
        self.assertGreaterEqual(image.size, 0x84)
        halt = isa_assemble("halt").to_bytes(4, "little")
        self.assertEqual(image.payload[0x80:0x84], halt)
        self.assertEqual(image.payload[:0x80], b"\x00" * 0x80)
        with self.assertRaises(AsmError):
            assemble_source("nop\nnop\n.org 4\n")


if __name__ == "__main__":
    unittest.main()
