"""ISA m3 acceptance tests. Run from repo root: python3 -m unittest compiler.tests.test_m3"""

import unittest

from compiler.yap_isa import FUNCT, OPCODE, Cpu, assemble, parse_reg, unpack_r
from compiler.yap_isa.cpu import CAUSE_ALIGN


class TestM3(unittest.TestCase):
    def test_ISA_017(self):
        cpu = Cpu()
        t0 = parse_reg("t0")
        word = assemble("div t0, ones, one")
        self.assertEqual(unpack_r(word)["funct"], FUNCT["div"])
        cpu.step(word)
        self.assertEqual(cpu.read(t0), 0xFFFFFFFF)
        cpu.step(assemble("div t0, ones, zero"))
        self.assertEqual(cpu.read(t0), 0)
        self.assertEqual(cpu.flags.z, 1)

    def test_ISA_018(self):
        cpu = Cpu()
        cpu.mem_store(0, bytes([0x78, 0x56, 0x34, 0x12]))
        word = assemble("lw t0, 0(zero)")
        self.assertEqual(unpack_r(word)["opcode"], OPCODE["lw"])
        cpu.step(word)
        self.assertEqual(cpu.read(parse_reg("t0")), 0x12345678)

    def test_ISA_019(self):
        cpu = Cpu()
        t0 = parse_reg("t0")
        cpu.step(assemble("lui t0, 0x1234"))
        cpu.step(assemble("ori t0, t0, 0x5678"))
        cpu.step(assemble("sw t0, 0(zero)"))
        self.assertEqual(list(cpu.mem_load(0, 4)), [0x78, 0x56, 0x34, 0x12])

    def test_ISA_020(self):
        cpu = Cpu()
        t0 = parse_reg("t0")
        cpu.mem_store(0, bytes([0xFF]))
        cpu.step(assemble("lb t0, 0(zero)"))
        self.assertEqual(cpu.read(t0), 0xFFFFFFFF)
        cpu.step(assemble("lbu t0, 0(zero)"))
        self.assertEqual(cpu.read(t0), 0xFF)

    def test_ISA_021(self):
        cpu = Cpu()
        cpu.mem_store(3, bytes([0xAA, 0xBB, 0xCC]))
        cpu.step(assemble("sb one, 4(zero)"))
        self.assertEqual(cpu.mem[4], 1)
        self.assertEqual(cpu.mem[3], 0xAA)
        self.assertEqual(cpu.mem[5], 0xCC)

    def test_ISA_022(self):
        cpu = Cpu()
        t0 = parse_reg("t0")
        cpu.mem_store(8, bytes([0xFF, 0x80]))
        cpu.step(assemble("lh t0, 8(zero)"))
        self.assertEqual(cpu.read(t0), 0xFFFF80FF)
        cpu.step(assemble("lhu t0, 8(zero)"))
        self.assertEqual(cpu.read(t0), 0x80FF)

    def test_ISA_023(self):
        cpu = Cpu()
        t0 = parse_reg("t0")
        cpu.write(t0, 0x80FF)
        cpu.step(assemble("sh t0, 8(zero)"))
        self.assertEqual(list(cpu.mem_load(8, 2)), [0xFF, 0x80])

    def test_ISA_024(self):
        cpu = Cpu()
        t0 = parse_reg("t0")
        cpu.step(assemble("lui t0, 0x1234"))
        cpu.step(assemble("ori t0, t0, 0x5678"))
        cpu.step(assemble("sw t0, 0(zero)"))
        self.assertEqual(cpu.mem[0], 0x78)
        cpu.step(assemble("lw t1, 0(zero)"))
        self.assertEqual(cpu.read(parse_reg("t1")), 0x12345678)
        cpu.cause = 0
        cpu.step(assemble("lw t0, 1(zero)"))
        self.assertEqual(cpu.cause, CAUSE_ALIGN)

    def test_ISA_027(self):
        cpu = Cpu()
        before = cpu.gprs_snapshot()
        word = assemble("j 0x20")
        self.assertEqual(unpack_r(word)["opcode"], OPCODE["j"])
        cpu.step(word)
        self.assertEqual(cpu.pc, 0x20)
        self.assertEqual(cpu.gprs_snapshot(), before)

    def test_ISA_028(self):
        cpu = Cpu()
        word = assemble("jal 0x20")
        self.assertEqual(unpack_r(word)["opcode"], OPCODE["jal"])
        cpu.step(word)
        self.assertEqual(cpu.read(parse_reg("ra")), 4)
        self.assertEqual(cpu.pc, 0x20)

    def test_ISA_029(self):
        cpu = Cpu()
        cpu.step(assemble("jal 0x20"))
        word = assemble("jr ra")
        self.assertEqual(unpack_r(word)["funct"], FUNCT["jr"])
        cpu.step(word)
        self.assertEqual(cpu.pc, 4)
        cpu.pc = 0
        t1 = parse_reg("t1")
        cpu.write(t1, 0x40)
        word = assemble("jalr t0, t1")
        self.assertEqual(unpack_r(word)["funct"], FUNCT["jalr"])
        cpu.step(word)
        self.assertEqual(cpu.read(parse_reg("t0")), 4)
        self.assertEqual(cpu.pc, 0x40)


if __name__ == "__main__":
    unittest.main()
