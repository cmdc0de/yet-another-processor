"""CPU m3 tests. Run from repo root: python3 -m unittest compiler.tests.test_cpu_m3"""

import unittest

from compiler.tests.test_cpu_m1 import _halt_at, _load, _run
from compiler.yap_cpu import Cpu
from compiler.yap_isa import assemble, parse_reg


class TestCpuM3(unittest.TestCase):
    def test_CPU_014(self):
        cpu = Cpu()
        _load(
            cpu,
            [
                assemble("lui t0, 0xA1B2"),
                assemble("ori t0, t0, 0xC3D4"),
                assemble("sw t0, 16(zero)"),
                assemble("lw t0, 16(zero)"),
                assemble("halt"),
            ],
        )
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t0")), 0xA1B2C3D4)
        cpu = Cpu()
        _load(
            cpu,
            [
                assemble("addi t1, zero, 0x5A"),
                assemble("sb t1, 20(zero)"),
                assemble("lbu t0, 20(zero)"),
                assemble("halt"),
            ],
        )
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t0")), 0x5A)
        cpu = Cpu()
        _load(
            cpu,
            [
                assemble("addi t1, zero, 8"),
                assemble("lui t0, 0x1111"),
                assemble("ori t0, t0, 0x2222"),
                assemble("sw t0, 4(t1)"),
                assemble("halt"),
            ],
        )
        _run(cpu)
        self.assertEqual(bytes(cpu.mem[12:16]), (0x11112222).to_bytes(4, "little"))

    def test_CPU_015(self):
        cpu = Cpu()
        _load(
            cpu,
            [
                assemble("lui t0, 0x1234"),
                assemble("ori t0, t0, 0x5678"),
                assemble("sw t0, 0(zero)"),
                assemble("halt"),
            ],
        )
        _run(cpu)
        self.assertEqual(bytes(cpu.mem[0:4]), bytes([0x78, 0x56, 0x34, 0x12]))

    def test_CPU_026(self):
        cpu = Cpu()
        _load(cpu, [assemble("lw t0, 0(zero)")], at=0x1000)
        _halt_at(cpu, 0x80)
        cpu.pc = 0x1000
        cpu.p = 0
        cpu.ubase = 0x1000
        cpu.ulimit = 0x8000
        _run(cpu)
        self.assertEqual(cpu.cause, 2)
        self.assertEqual(int.from_bytes(cpu.mem[0:4], "little"), 0)
        self.assertTrue(cpu.halted)
        self.assertEqual(cpu.pc, 0x80)

    def test_CPU_027(self):
        cpu = Cpu()
        _halt_at(cpu, 0x80)
        _load(cpu, [assemble("lw t0, 1(zero)")])
        _run(cpu)
        self.assertEqual(cpu.cause, 8)
        cpu = Cpu()
        _halt_at(cpu, 0x80)
        cpu.write(parse_reg("t0"), 0xFFFFFFFF)
        _load(cpu, [assemble("sw t0, 1(zero)")])
        before = bytes(cpu.mem[0:4])
        _run(cpu)
        self.assertEqual(cpu.cause, 8)
        self.assertEqual(bytes(cpu.mem[0:4]), before)


if __name__ == "__main__":
    unittest.main()
