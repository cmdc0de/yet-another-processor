"""CPU m1 tests. Run from repo root: python3 -m unittest compiler.tests.test_cpu_m1"""

import unittest

from compiler.yap_cpu import Cpu
from compiler.yap_isa import assemble, parse_reg


def _load(cpu: Cpu, words, at=0):
    blob = b"".join(int(w).to_bytes(4, "little") for w in words)
    cpu.mem_store(at, blob)


def _run(cpu: Cpu, max_cycles=10000) -> Cpu:
    cpu.run(max_cycles=max_cycles)
    return cpu


def _halt_at(cpu: Cpu, addr: int) -> None:
    _load(cpu, [assemble("halt")], at=addr)


class TestCpuM1(unittest.TestCase):
    def test_CPU_001(self):
        cpu = Cpu()
        _load(cpu, [assemble("add t0, one, one"), assemble("halt")])
        _run(cpu)
        self.assertTrue(cpu.halted)
        self.assertEqual(cpu.read(parse_reg("t0")), 2)
        self.assertEqual(cpu.pc, cpu.pc & 0xFFFFFFFF)
        self.assertEqual(cpu.read(parse_reg("t0")), cpu.read(parse_reg("t0")) & 0xFFFFFFFF)

    def test_CPU_002(self):
        cpu = Cpu()
        _load(cpu, [assemble("add t0, one, one"), assemble("halt")])
        _run(cpu)
        self.assertEqual(cpu.pc, 4)

    def test_CPU_003(self):
        cpu = Cpu()
        halt = assemble("halt")
        _load(cpu, [halt])
        _run(cpu)
        self.assertTrue(cpu.halted)
        self.assertEqual(cpu.ir, halt)

    def test_CPU_004(self):
        cpu = Cpu()
        _load(
            cpu,
            [
                assemble("add t0, one, one"),
                assemble("add s0, t0, one"),
                assemble("halt"),
            ],
        )
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t0")), 2)
        self.assertEqual(cpu.read(parse_reg("s0")), 3)

    def test_CPU_005(self):
        cpu = Cpu()
        _load(cpu, [assemble("add zero, one, one"), assemble("halt")])
        _run(cpu)
        self.assertEqual(cpu.read(0), 0)
        self.assertEqual(cpu.flags.z, 0)

    def test_CPU_006(self):
        cpu = Cpu()
        _load(cpu, [assemble("add t0, one, one"), assemble("halt")])
        _run(cpu)
        self.assertEqual(cpu.flags.as_tuple(), (0, 0, 0, 0))
        for i in range(32):
            self.assertIsInstance(cpu.read(i), int)

    def test_CPU_007(self):
        cpu = Cpu()
        _load(cpu, [assemble("add t0, one, one"), assemble("halt")])
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t0")), 2)
        cpu = Cpu()
        _load(cpu, [assemble("sub t0, one, one"), assemble("halt")])
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t0")), 0)
        self.assertEqual(cpu.flags.z, 1)

    def test_CPU_018(self):
        cpu = Cpu()
        _load(cpu, [assemble("halt")])
        _run(cpu)
        self.assertTrue(cpu.halted)
        self.assertGreater(cpu.cycles, 1)

    def test_CPU_019(self):
        cpu = Cpu()
        _load(cpu, [assemble("halt")])
        _run(cpu)
        self.assertTrue(cpu.halted)
        self.assertEqual(cpu.read(parse_reg("t0")), 0)
        cpu = Cpu()
        _load(cpu, [assemble("add t0, one, one"), assemble("halt")])
        _run(cpu)
        self.assertEqual(cpu.read(parse_reg("t0")), 2)

    def test_CPU_021(self):
        cpu = Cpu()
        _halt_at(cpu, 0x80)
        cpu.pc = 1
        _run(cpu)
        self.assertEqual(cpu.cause, 8)
        cpu = Cpu()
        _load(cpu, [assemble("halt")])
        _run(cpu)
        self.assertNotEqual(cpu.cause, 8)
        self.assertEqual(cpu.cause, 0)

    def test_CPU_022(self):
        cpu = Cpu()
        _load(cpu, [assemble("halt")])
        _run(cpu)
        pc = cpu.pc
        upc = cpu.upc
        cpu.step()
        self.assertTrue(cpu.halted)
        self.assertEqual(cpu.pc, pc)
        self.assertEqual(cpu.upc, upc)

    def test_CPU_023(self):
        cpu = Cpu()
        _halt_at(cpu, 0x80)
        cpu.pc = 1
        _run(cpu)
        self.assertTrue(cpu.halted)
        self.assertEqual(cpu.cause, 8)
        self.assertEqual(cpu.p, 1)
        self.assertEqual(cpu.ie, 0)
        self.assertEqual(cpu.epc, 1)
        self.assertEqual(cpu.pc, 0x80)


if __name__ == "__main__":
    unittest.main()
