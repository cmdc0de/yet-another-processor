"""CPU m2 tests. Run from repo root: python3 -m unittest compiler.tests.test_cpu_m2"""

import unittest

from compiler.tests.test_cpu_m1 import _load, _run
from compiler.yap_cpu import Cpu
from compiler.yap_isa import assemble, parse_reg


class TestCpuM2(unittest.TestCase):
    def test_CPU_008(self):
        cpu = Cpu()
        _load(cpu, [assemble("and t0, ones, one"), assemble("halt")])
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t0")), 1)
        self.assertEqual(cpu.flags.z, 0)
        self.assertEqual(cpu.flags.c, 0)
        self.assertEqual(cpu.flags.v, 0)
        cpu = Cpu()
        _load(cpu, [assemble("xor t0, one, one"), assemble("halt")])
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t0")), 0)
        self.assertEqual(cpu.flags.z, 1)
        self.assertEqual(cpu.flags.c, 0)
        self.assertEqual(cpu.flags.v, 0)

    def test_CPU_009(self):
        cpu = Cpu()
        _load(cpu, [assemble("sll t0, one, 1"), assemble("halt")])
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t0")), 2)
        self.assertEqual(cpu.flags.c, 0)
        self.assertEqual(cpu.flags.v, 0)
        cpu = Cpu()
        _load(cpu, [assemble("sra t0, ones, 1"), assemble("halt")])
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t0")) >> 31, 1)

    def test_CPU_010(self):
        cpu = Cpu()
        _load(cpu, [assemble("cmp one, one"), assemble("halt")])
        _run(cpu)
        self.assertEqual(cpu.flags.z, 1)
        self.assertEqual(cpu.read(parse_reg("t0")), 0)
        cpu = Cpu()
        _load(cpu, [assemble("test one, zero"), assemble("halt")])
        _run(cpu)
        self.assertEqual(cpu.flags.z, 1)

    def test_CPU_011(self):
        cpu = Cpu()
        _load(cpu, [assemble("mul t0, one, one"), assemble("halt")])
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t0")), 1)
        cpu = Cpu()
        _load(cpu, [assemble("div t0, one, zero"), assemble("halt")])
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t0")), 0)
        self.assertEqual(cpu.flags.z, 1)

    def test_CPU_012(self):
        cpu = Cpu()
        _load(cpu, [assemble("addi t0, one, -1"), assemble("halt")])
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t0")), 0)
        self.assertEqual(cpu.flags.z, 1)
        cpu = Cpu()
        _load(cpu, [assemble("andi t0, ones, 0xFF"), assemble("halt")])
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t0")), 0xFF)
        cpu = Cpu()
        _load(cpu, [assemble("lui t0, 1"), assemble("halt")])
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t0")), 0x10000)

    def test_CPU_013(self):
        cpu = Cpu()
        _load(cpu, [assemble("adr t0, 4"), assemble("halt")])
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t0")), 8)

    def test_CPU_032(self):
        mos = Cpu()
        _load(mos, [assemble("add t0, t0, one"), assemble("halt")])
        _run(mos)
        ic = Cpu()
        _load(ic, [assemble("add s0, s0, one"), assemble("halt")])
        _run(ic)
        self.assertGreater(ic.cycles, mos.cycles)


if __name__ == "__main__":
    unittest.main()
