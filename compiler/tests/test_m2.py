"""ISA m2 acceptance tests. Run from repo root: python3 -m unittest compiler.tests.test_m2"""

import unittest

from compiler.yap_isa import (
    FUNCT,
    OPCODE,
    Cpu,
    assemble,
    parse_reg,
    unpack_r,
)


class TestM2(unittest.TestCase):
    def test_ISA_012(self):
        cpu = Cpu()
        t0 = parse_reg("t0")
        cpu.step(assemble("sll t0, one, 3"))
        word = assemble("srl t0, t0, 2")
        self.assertEqual(unpack_r(word)["funct"], FUNCT["srl"])
        cpu.step(word)
        self.assertEqual(cpu.read(t0), 2)
        word = assemble("srlv t0, t0, one")
        self.assertEqual(unpack_r(word)["funct"], FUNCT["srlv"])
        cpu.step(word)
        self.assertEqual(cpu.read(t0), 1)

    def test_ISA_013(self):
        cpu = Cpu()
        t0 = parse_reg("t0")
        word = assemble("lui t0, 0x8000")
        cpu.step(word)
        self.assertEqual(cpu.read(t0), 0x80000000)
        word = assemble("sra t0, t0, 1")
        self.assertEqual(unpack_r(word)["funct"], FUNCT["sra"])
        cpu.step(word)
        self.assertEqual(cpu.read(t0), 0xC0000000)
        self.assertEqual(cpu.flags.n, 1)
        word = assemble("srav t0, t0, one")
        self.assertEqual(unpack_r(word)["funct"], FUNCT["srav"])
        cpu.step(word)
        self.assertEqual(cpu.read(t0), 0xE0000000)

    def test_ISA_015(self):
        cpu = Cpu()
        t0 = parse_reg("t0")
        cpu.step(assemble("addi t0, one, -1"))
        self.assertEqual(cpu.read(t0), 0)
        self.assertEqual(cpu.flags.z, 1)
        cpu.step(assemble("andi t0, ones, 0x00FF"))
        self.assertEqual(cpu.read(t0), 0xFF)
        cpu.step(assemble("ori t0, zero, 1"))
        self.assertEqual(cpu.read(t0), 1)
        cpu.step(assemble("xori t0, ones, 0"))
        self.assertEqual(cpu.read(t0), 0xFFFFFFFF)

    def test_ISA_016(self):
        cpu = Cpu()
        t0 = parse_reg("t0")
        word = assemble("mul t0, one, ones")
        self.assertEqual(unpack_r(word)["funct"], FUNCT["mul"])
        cpu.step(word)
        self.assertEqual(cpu.read(t0), 0xFFFFFFFF)
        cpu.step(assemble("mul t0, ones, ones"))
        self.assertEqual(cpu.read(t0), 1)
        cpu.step(assemble("mul t0, zero, ones"))
        self.assertEqual(cpu.read(t0), 0)
        self.assertEqual(cpu.flags.z, 1)
        self.assertEqual(cpu.flags.c, 0)
        self.assertEqual(cpu.flags.v, 0)

    def test_ISA_025(self):
        cpu = Cpu()
        t0 = parse_reg("t0")
        word = assemble("lui t0, 0x1234")
        self.assertEqual(unpack_r(word)["opcode"], OPCODE["lui"])
        flags_before = cpu.flags.as_tuple()
        cpu.step(word)
        self.assertEqual(cpu.read(t0), 0x12340000)
        self.assertEqual(cpu.flags.as_tuple(), flags_before)
        cpu.step(assemble("ori t0, t0, 0x5678"))
        self.assertEqual(cpu.read(t0), 0x12345678)

    def test_ISA_026(self):
        cpu = Cpu()
        t0 = parse_reg("t0")
        self.assertEqual(cpu.pc, 0)
        word = assemble("adr t0, 16")
        self.assertEqual(unpack_r(word)["opcode"], OPCODE["adr"])
        flags_before = cpu.flags.as_tuple()
        cpu.step(word)
        self.assertEqual(cpu.read(t0), 20)
        self.assertEqual(cpu.flags.as_tuple(), flags_before)

    def test_sllv(self):
        cpu = Cpu()
        t0 = parse_reg("t0")
        t1 = parse_reg("t1")
        cpu.write(t1, 3)
        word = assemble("sllv t0, one, t1")
        self.assertEqual(unpack_r(word)["funct"], FUNCT["sllv"])
        cpu.step(word)
        self.assertEqual(cpu.read(t0), 8)


if __name__ == "__main__":
    unittest.main()
