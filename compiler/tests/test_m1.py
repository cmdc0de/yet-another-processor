"""ISA m1 acceptance tests. Run from repo root: python3 -m unittest compiler.tests.test_m1"""

import unittest

from compiler.yap_isa import (
    FUNCT,
    GPR_COUNT,
    MASK,
    NAME_TO_NUM,
    OPCODE_SPECIAL,
    WORD_BYTES,
    Cpu,
    assemble,
    nop_word,
    parse_reg,
    unpack_r,
)


class TestM1(unittest.TestCase):
    def test_ISA_001(self):
        word = assemble("add t0, one, one")
        raw = word.to_bytes(4, "little")
        self.assertEqual(len(raw), WORD_BYTES)
        self.assertEqual(len(raw), 4)
        cpu = Cpu()
        cpu.pc = 0xFFFFFFFC
        cpu.step(word)
        self.assertEqual(cpu.pc, 0)

    def test_ISA_002(self):
        cpu = Cpu()
        for i in range(GPR_COUNT):
            cpu.read(i)
        with self.assertRaises(ValueError):
            parse_reg("r32")
        with self.assertRaises(ValueError):
            cpu.read(32)

    def test_ISA_003(self):
        cpu = Cpu()
        pc0 = cpu.pc
        cpu.step(assemble("add t0, one, one"))
        self.assertEqual(cpu.pc, (pc0 + 4) & MASK)

    def test_ISA_004(self):
        cpu = Cpu()
        # ones+ones → 0xFFFFFFFE, N=1 Z=0 (design.md wrap)
        cpu.step(assemble("add t0, ones, ones"))
        self.assertEqual(cpu.flags.n, 1)
        self.assertEqual(cpu.flags.z, 0)
        cpu.step(assemble("add zero, zero, zero"))
        self.assertEqual(cpu.flags.z, 1)
        self.assertEqual(cpu.flags.n, 0)
        # overflowing signed ADD: 0x7FFFFFFF + 1
        cpu.write(parse_reg("t0"), 0x7FFFFFFF)
        cpu.step(assemble("add t0, t0, one"))
        self.assertEqual(cpu.read(parse_reg("t0")), 0x80000000)
        self.assertEqual(cpu.flags.v, 1)
        self.assertEqual(cpu.flags.n, 1)
        self.assertEqual(cpu.flags.c, 0)
        # borrowing SUB: 0 - 1
        cpu.step(assemble("sub t1, zero, one"))
        self.assertEqual(cpu.flags.c, 1)
        self.assertEqual(cpu.read(parse_reg("t1")), MASK)

    def test_ISA_005(self):
        cpu = Cpu()
        word = assemble("add t0, one, one")
        fields = unpack_r(word)
        self.assertEqual(fields["opcode"], OPCODE_SPECIAL)
        self.assertEqual(fields["funct"], FUNCT["add"])
        cpu.step(word)
        self.assertEqual(cpu.read(parse_reg("t0")), 2)

    def test_ISA_006(self):
        cpu = Cpu()
        cpu.step(assemble("sub t0, one, one"))
        self.assertEqual(cpu.read(parse_reg("t0")), 0)
        self.assertEqual(cpu.flags.z, 1)

    def test_ISA_007(self):
        cpu = Cpu()
        cpu.step(assemble("and t0, ones, one"))
        self.assertEqual(cpu.read(parse_reg("t0")), 1)

    def test_ISA_008(self):
        cpu = Cpu()
        cpu.step(assemble("or t0, zero, one"))
        self.assertEqual(cpu.read(parse_reg("t0")), 1)

    def test_ISA_009(self):
        cpu = Cpu()
        cpu.step(assemble("xor t0, ones, ones"))
        self.assertEqual(cpu.read(parse_reg("t0")), 0)

    def test_ISA_010(self):
        cpu = Cpu()
        cpu.step(assemble("not t0, zero"))
        self.assertEqual(cpu.read(parse_reg("t0")), MASK)

    def test_ISA_011(self):
        cpu = Cpu()
        cpu.step(assemble("sll t0, one, 3"))
        self.assertEqual(cpu.read(parse_reg("t0")), 8)

    def test_ISA_014(self):
        cpu = Cpu()
        cpu.step(assemble("add t0, one, one"))
        t0 = parse_reg("t0")
        cpu.step(assemble("cmp t0, one"))
        self.assertEqual(cpu.read(t0), 2)
        self.assertEqual(cpu.flags.z, 0)
        self.assertEqual(cpu.flags.c, 0)
        self.assertEqual(cpu.flags.n, 0)
        word = assemble("cmp one, t0")
        self.assertEqual(unpack_r(word)["funct"], FUNCT["cmp"])
        cpu.step(word)
        self.assertEqual(cpu.read(t0), 2)
        self.assertEqual(cpu.flags.c, 1)

    def test_ISA_031(self):
        self.assertEqual(assemble("nop"), assemble("sll zero, zero, 0"))
        self.assertEqual(assemble("nop"), nop_word())
        cpu = Cpu()
        before = cpu.gprs_snapshot()
        cpu.step(assemble("nop"))
        self.assertEqual(cpu.gprs_snapshot(), before)

    def test_ISA_050(self):
        self.assertEqual(NAME_TO_NUM["zero"], 0)
        self.assertEqual(NAME_TO_NUM["one"], 1)
        self.assertEqual(NAME_TO_NUM["ones"], 2)
        self.assertEqual(NAME_TO_NUM["ra"], 3)
        self.assertEqual(NAME_TO_NUM["sp"], 4)
        self.assertEqual(NAME_TO_NUM["a0"], 5)
        self.assertEqual(NAME_TO_NUM["fp"], 30)
        self.assertEqual(NAME_TO_NUM["k0"], 31)
        self.assertEqual(parse_reg("zero"), 0)
        self.assertEqual(parse_reg("k0"), 31)

    def test_ISA_052(self):
        cpu = Cpu()
        t0 = parse_reg("t0")
        cpu.step(assemble("add t0, one, one"))
        word = assemble("test t0, one")
        self.assertEqual(unpack_r(word)["funct"], FUNCT["test"])
        cpu.step(word)
        self.assertEqual(cpu.read(t0), 2)
        # 2 & 1 == 0 → even, Z=1 (design.md AND flags)
        self.assertEqual(cpu.flags.z, 1)
        self.assertEqual(cpu.flags.n, 0)
        self.assertEqual(cpu.flags.c, 0)
        self.assertEqual(cpu.flags.v, 0)
        cpu.step(assemble("test t0, zero"))
        self.assertEqual(cpu.flags.z, 1)
        # odd: 1 & 1 != 0 → Z=0
        cpu.step(assemble("test one, one"))
        self.assertEqual(cpu.flags.z, 0)

    def test_ISA_053(self):
        cpu = Cpu()
        t0 = parse_reg("t0")
        cpu.step(assemble("add t0, one, one"))
        word = assemble("teq t0, t0")
        self.assertEqual(unpack_r(word)["funct"], FUNCT["teq"])
        cpu.step(word)
        self.assertEqual(cpu.read(t0), 2)
        self.assertEqual(cpu.flags.z, 1)
        self.assertEqual(cpu.flags.n, 0)
        self.assertEqual(cpu.flags.c, 0)
        self.assertEqual(cpu.flags.v, 0)
        cpu.step(assemble("teq t0, one"))
        self.assertEqual(cpu.read(t0), 2)
        self.assertEqual(cpu.flags.z, 0)

    def test_ISA_054(self):
        cpu = Cpu()
        cpu.step(assemble("add zero, one, one"))
        self.assertEqual(cpu.read(0), 0)
        self.assertEqual(cpu.flags.z, 0)
        self.assertEqual(cpu.flags.n, 0)

    def test_ISA_055(self):
        cpu = Cpu()
        cpu.step(assemble("add one, zero, ones"))
        self.assertEqual(cpu.read(1), 1)

    def test_ISA_056(self):
        cpu = Cpu()
        cpu.step(assemble("add ones, zero, zero"))
        self.assertEqual(cpu.read(2), MASK)


if __name__ == "__main__":
    unittest.main()
