"""CPU m4 tests. Run from repo root: python3 -m unittest compiler.tests.test_cpu_m4"""

import unittest

from compiler.tests.test_cpu_m1 import _halt_at, _load, _run
from compiler.yap_cpu import Cpu
from compiler.yap_isa import assemble, parse_reg


class TestCpuM4(unittest.TestCase):
    def test_CPU_016(self):
        cpu = Cpu()
        _load(
            cpu,
            [
                assemble("addi t0, zero, 0x1000"),
                assemble("mtc0 t0, ubase"),
                assemble("mfc0 t1, ubase"),
                assemble("halt"),
            ],
        )
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t1")), 0x1000)

    def test_CPU_017(self):
        cpu = Cpu()
        _load(
            cpu,
            [
                assemble("lui t0, 0xA5A5"),
                assemble("ori t0, t0, 0xA5A5"),
                assemble("mtc1 t0, f0"),
                assemble("mfc1 t1, f0"),
                assemble("halt"),
            ],
        )
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t1")), 0xA5A5A5A5)

    def test_CPU_020(self):
        cpu = Cpu()
        _halt_at(cpu, 0x80)
        _load(cpu, [assemble("lw t0, 1(zero)")], at=0)
        _load(cpu, [assemble("mfc0 t1, cause"), assemble("halt")], at=0x80)
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t1")), 8)

    def test_CPU_024(self):
        cpu = Cpu()
        _halt_at(cpu, 0x80)
        _load(cpu, [assemble("sys 1")])
        _run(cpu)
        self.assertEqual(cpu.cause, 3)
        self.assertEqual(cpu.epc, 4)

    def test_CPU_025(self):
        cpu = Cpu()
        _halt_at(cpu, 0x80)
        _load(
            cpu,
            [
                assemble("addi t0, zero, 0x80"),
                assemble("mtc0 t0, epc"),
                assemble("addi t0, zero, 0x202"),
                assemble("mtc0 t0, status"),
                assemble("eret"),
            ],
        )
        _run(cpu)
        self.assertTrue(cpu.halted)
        self.assertEqual(cpu.pc, 0x80)
        self.assertEqual(cpu.p, 1)

    def test_CPU_028(self):
        cpu = Cpu()
        _halt_at(cpu, 0x80)
        _load(cpu, [assemble("eret")])
        cpu.p = 0
        _run(cpu)
        self.assertEqual(cpu.cause, 7)

    def test_CPU_029(self):
        cpu = Cpu()
        _halt_at(cpu, 0x80)
        _load(cpu, [assemble("addi t0, zero, 4"), assemble("mtc0 t0, status")])
        _run(cpu)
        self.assertEqual(cpu.cause, 7)
        self.assertEqual(cpu.te, 0)

    def test_CPU_030(self):
        cpu = Cpu()
        _load(cpu, [assemble("halt")])
        _halt_at(cpu, 0x80)
        cpu.ie = 1
        cpu.irq()
        _run(cpu)
        self.assertEqual(cpu.cause, 1)
        self.assertTrue(cpu.halted)
        self.assertEqual(cpu.pc, 0x80)

    def test_CPU_031(self):
        cpu = Cpu()
        _halt_at(cpu, 0x80)
        _load(cpu, [0x44100000])
        _run(cpu)
        self.assertEqual(cpu.cause, 6)


if __name__ == "__main__":
    unittest.main()
