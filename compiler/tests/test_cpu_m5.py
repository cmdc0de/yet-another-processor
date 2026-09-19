"""CPU m5 tests. Run from repo root: python3 -m unittest compiler.tests.test_cpu_m5"""

import unittest

from compiler.tests.test_cpu_m1 import _halt_at, _load, _run
from compiler.yap_cpu import Cpu
from compiler.yap_isa import assemble, parse_reg


class TestCpuM5(unittest.TestCase):
    def test_CPU_039(self):
        cpu = Cpu()
        _load(cpu, [assemble("j 0x20")])
        _halt_at(cpu, 0x20)
        _run(cpu)
        self.assertTrue(cpu.halted)
        self.assertEqual(cpu.pc, 0x20)

    def test_CPU_040(self):
        cpu = Cpu()
        _load(cpu, [assemble("jal 0x20")])
        _halt_at(cpu, 0x20)
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("ra")), 4)
        self.assertEqual(cpu.pc, 0x20)

    def test_CPU_041(self):
        cpu = Cpu()
        _load(cpu, [assemble("addi t0, zero, 0x20"), assemble("jr t0")])
        _halt_at(cpu, 0x20)
        _run(cpu)
        self.assertEqual(cpu.pc, 0x20)

    def test_CPU_042(self):
        cpu = Cpu()
        _load(cpu, [assemble("addi t0, zero, 0x20"), assemble("jalr t1, t0")])
        _halt_at(cpu, 0x20)
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t1")), 8)
        self.assertEqual(cpu.pc, 0x20)

    def test_CPU_043(self):
        cpu = Cpu()
        _load(cpu, [assemble("cmp one, one"), assemble("beq 0x20", pc=4)])
        _halt_at(cpu, 0x20)
        _run(cpu)
        self.assertEqual(cpu.pc, 0x20)
        cpu = Cpu()
        _load(
            cpu,
            [
                assemble("cmp one, zero"),
                assemble("beq 0x20", pc=4),
                assemble("halt"),
            ],
        )
        _run(cpu)
        self.assertEqual(cpu.pc, 8)
        cpu = Cpu()
        _load(cpu, [assemble("cmp zero, one"), assemble("blo 0x20", pc=4)])
        _halt_at(cpu, 0x20)
        _run(cpu)
        self.assertEqual(cpu.pc, 0x20)
        cpu = Cpu()
        _load(
            cpu,
            [
                assemble("cmp zero, one"),
                assemble("bhs 0x20", pc=4),
                assemble("halt"),
            ],
        )
        _run(cpu)
        self.assertEqual(cpu.pc, 8)


if __name__ == "__main__":
    unittest.main()
