"""ISA m5 acceptance tests. Run from repo root: python3 -m unittest compiler.tests.test_m5"""

import unittest

from compiler.yap_isa import OPCODE, Cpu, assemble, parse_reg, unpack_r
from compiler.yap_isa.csrs import (
    CAUSE_IRQ,
    CAUSE_PAGE_FAULT,
    CAUSE_PRIV,
    CAUSE_PROT,
    CAUSE_SYS,
    CAUSE_TLB_MISS,
    TRAP_VECTOR,
)


class TestM5(unittest.TestCase):
    def test_ISA_033(self):
        cpu = Cpu()
        self.assertEqual(cpu.p, 1)
        self.assertEqual(cpu.ie, 0)
        self.assertEqual(cpu.pc, 0)
        cpu.step(assemble("mtc0 zero, status"))
        self.assertEqual(cpu.p, 0)

    def test_ISA_034(self):
        cpu = Cpu()
        cpu.step(assemble("mtc0 zero, status"))
        cpu.step(assemble("mtc0 t0, ubase"))
        self.assertEqual(cpu.cause, CAUSE_PRIV)
        self.assertEqual(cpu.pc, TRAP_VECTOR)
        self.assertEqual(cpu.p, 1)
        cpu = Cpu()
        cpu.step(assemble("addi t0, zero, 0x100"))
        cpu.step(assemble("mtc0 t0, ubase"))
        self.assertEqual(cpu.ubase, 0x100)
        self.assertEqual(cpu.p, 1)
        cpu = Cpu()
        cpu.step(assemble("mtc0 zero, status"))
        cpu.step(assemble("eret"))
        self.assertEqual(cpu.cause, CAUSE_PRIV)

    def test_ISA_035(self):
        cpu = Cpu()
        cpu.step(assemble("sys 1"))
        self.assertEqual(cpu.cause, CAUSE_SYS)
        self.assertEqual(cpu.epc, 4)
        self.assertEqual(cpu.p, 1)
        self.assertEqual(cpu.ie, 0)
        self.assertEqual(cpu.pc, TRAP_VECTOR)
        self.assertEqual(cpu.pp, 1)
        self.assertEqual(cpu.pie, 0)

    def test_ISA_036(self):
        cpu = Cpu()
        cpu.step(assemble("sys 1"))
        cpu.step(assemble("eret"))
        self.assertEqual(cpu.pc, 4)
        self.assertEqual(cpu.p, 1)

    def test_ISA_037(self):
        cpu = Cpu()
        cpu.step(assemble("lw t0, 0(zero)"))
        cpu.step(assemble("addi t0, zero, 0x100"))
        cpu.step(assemble("mtc0 t0, ubase"))
        cpu.step(assemble("addi t0, zero, 0x200"))
        cpu.step(assemble("mtc0 t0, ulimit"))
        cpu.step(assemble("lw t0, 0(zero)"))
        self.assertEqual(cpu.p, 1)
        cpu.step(assemble("mtc0 zero, status"))
        cpu.pc = 0x100
        cpu.step(assemble("lw t0, 0(zero)"))
        self.assertEqual(cpu.cause, CAUSE_PROT)

    def test_ISA_038(self):
        cpu = Cpu()
        cpu.step(assemble("addi t0, zero, 0x100"))
        cpu.step(assemble("mtc0 t0, ubase"))
        cpu.step(assemble("addi t0, zero, 0x200"))
        cpu.step(assemble("mtc0 t0, ulimit"))
        cpu.step(assemble("mtc0 zero, status"))
        cpu.pc = 0x100
        cpu.step(assemble("lw t0, 0(zero)"))
        self.assertEqual(cpu.cause, CAUSE_PROT)
        self.assertEqual(cpu.pc, TRAP_VECTOR)

    def test_ISA_039(self):
        cpu = Cpu()
        cpu.irq()
        self.assertEqual(cpu.pc, 0)
        cpu.ie = 1
        cpu.irq()
        self.assertEqual(cpu.pc, TRAP_VECTOR)

    def test_ISA_040(self):
        cpu = Cpu()
        cpu.ie = 1
        cpu.irq()
        self.assertEqual(cpu.cause, CAUSE_IRQ)

    def test_ISA_041(self):
        self.assertEqual(CAUSE_TLB_MISS, 4)
        self.assertEqual(CAUSE_PAGE_FAULT, 5)
        self.assertNotEqual(CAUSE_TLB_MISS, CAUSE_PROT)
        self.assertNotEqual(CAUSE_PAGE_FAULT, CAUSE_SYS)

    def test_ISA_042(self):
        cpu = Cpu()
        cpu.step(assemble("addi t0, zero, 4"))
        cpu.step(assemble("mtc0 t0, status"))
        self.assertEqual(cpu.cause, CAUSE_PRIV)
        self.assertEqual(cpu.te, 0)
        self.assertEqual(cpu.pc, TRAP_VECTOR)

    def test_ISA_049(self):
        cpu = Cpu()
        a0 = parse_reg("a0")
        cpu.write(a0, 99)
        word = assemble("sys 0x12")
        fields = unpack_r(word)
        self.assertEqual(fields["opcode"], OPCODE["sys"])
        self.assertEqual(fields["imm16"], 0x12)
        cpu.step(word)
        self.assertEqual(cpu.cause, CAUSE_SYS)
        self.assertEqual(cpu.read(a0), 99)
        self.assertEqual(cpu.read(parse_reg("a1")), 0)
        self.assertEqual(cpu.read(parse_reg("a2")), 0)
        self.assertEqual(cpu.read(parse_reg("a3")), 0)


if __name__ == "__main__":
    unittest.main()
