"""ISA m6 acceptance tests. Run from repo root: python3 -m unittest compiler.tests.test_m6"""

import unittest

from compiler.yap_isa import OPCODE, OPCODE_SPECIAL, Cpu, assemble, parse_reg, unpack_r
from compiler.yap_isa.abi import ABI_MAP, SP, STACK_ALIGN, USER_C_REGS, push_word
from compiler.yap_isa.csrs import CAUSE_COP, TRAP_VECTOR
from compiler.yap_isa.encode import pack_r
from compiler.yap_isa.regs import NAME_TO_NUM


class TestM6(unittest.TestCase):
    def test_ISA_043(self):
        word = assemble("mfc1 t0, f0")
        op = unpack_r(word)["opcode"]
        self.assertEqual(op, OPCODE["cop1"])
        self.assertEqual(op, 0b010001)
        self.assertNotEqual(op, OPCODE_SPECIAL)
        self.assertNotEqual(op, OPCODE["cop0"])

    def test_ISA_044(self):
        cpu = Cpu()
        t0, t1 = parse_reg("t0"), parse_reg("t1")
        cpu.write(t0, 0xA5A5A5A5)
        cpu.step(assemble("mtc1 t0, f0"))
        self.assertEqual(cpu.read_f(0), 0xA5A5A5A5)
        cpu.write(t1, 0)
        cpu.step(assemble("mfc1 t1, f0"))
        self.assertEqual(cpu.read(t1), 0xA5A5A5A5)
        with self.assertRaises(ValueError):
            parse_reg("f0")

    def test_ISA_045(self):
        cpu = Cpu()
        bad = pack_r(0, 1, 0, 0, 0, opcode=OPCODE["cop1"])
        cpu.step(bad)
        self.assertEqual(cpu.cause, CAUSE_COP)
        self.assertEqual(cpu.pc, TRAP_VECTOR)

    def test_ISA_046(self):
        self.assertEqual(parse_reg("sp"), 4)
        self.assertEqual(parse_reg("sp"), SP)
        cpu = Cpu()
        cpu.write(SP, 0x200)
        self.assertEqual(cpu.read(SP), 0x200)
        cpu.write(0, 99)
        cpu.write(1, 99)
        cpu.write(2, 99)
        self.assertEqual(cpu.read(0), 0)
        self.assertEqual(cpu.read(1), 1)
        self.assertEqual(cpu.read(2), 0xFFFFFFFF)

    def test_ISA_047(self):
        cpu = Cpu()
        cpu.write(SP, 0x200)
        a = push_word(cpu, 0x11111111)
        b = push_word(cpu, 0x22222222)
        self.assertEqual(cpu.read(SP), 0x1F8)
        self.assertEqual(cpu.read(SP) % STACK_ALIGN, 0)
        self.assertLess(b, a)
        self.assertLess(a, 0x200)
        self.assertEqual(int.from_bytes(cpu.mem_load(a, 4), "little"), 0x11111111)
        self.assertEqual(int.from_bytes(cpu.mem_load(b, 4), "little"), 0x22222222)

    def test_ISA_048(self):
        self.assertEqual(NAME_TO_NUM["ra"], 3)
        self.assertEqual(NAME_TO_NUM["a0"], 5)
        self.assertEqual(NAME_TO_NUM["a3"], 8)
        self.assertEqual(NAME_TO_NUM["s0"], 16)
        self.assertEqual(NAME_TO_NUM["s11"], 27)
        self.assertEqual(NAME_TO_NUM["fp"], 30)
        self.assertEqual(NAME_TO_NUM["k0"], 31)
        self.assertEqual(ABI_MAP["ra"], 3)
        self.assertNotIn("k0", USER_C_REGS)
        self.assertIn("sp", USER_C_REGS)
        self.assertIn("a0", USER_C_REGS)


if __name__ == "__main__":
    unittest.main()
