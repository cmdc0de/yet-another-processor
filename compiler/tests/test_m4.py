"""ISA m4 acceptance tests. Run from repo root: python3 -m unittest compiler.tests.test_m4"""

import unittest

from compiler.yap_isa import FUNCT, OPCODE, Cpu, assemble, unpack_r


class TestM4(unittest.TestCase):
    def test_ISA_030(self):
        cpu = Cpu()
        cpu.step(assemble("cmp one, one"))
        word = assemble("beq 0x20", pc=cpu.pc)
        self.assertEqual(unpack_r(word)["opcode"], OPCODE["bcc"])
        cpu.step(word)
        self.assertEqual(cpu.pc, 0x20)

        cpu = Cpu()
        cpu.step(assemble("cmp one, zero"))
        cpu.step(assemble("beq 0x20", pc=cpu.pc))
        self.assertEqual(cpu.pc, 8)

        cpu = Cpu()
        cpu.step(assemble("test one, one"))
        cpu.step(assemble("bne 0x20", pc=cpu.pc))
        self.assertEqual(cpu.pc, 0x20)

        cpu = Cpu()
        cpu.step(assemble("cmp zero, one"))
        cpu.step(assemble("blo 0x20", pc=cpu.pc))
        self.assertEqual(cpu.pc, 0x20)

        cpu = Cpu()
        cpu.step(assemble("cmp zero, one"))
        cpu.step(assemble("bhs 0x20", pc=cpu.pc))
        self.assertEqual(cpu.pc, 8)

    def test_ISA_032(self):
        cpu = Cpu()
        before = cpu.gprs_snapshot()
        word = assemble("halt")
        self.assertEqual(unpack_r(word)["funct"], FUNCT["halt"])
        cpu.step(word)
        self.assertTrue(cpu.halted)
        self.assertEqual(cpu.gprs_snapshot(), before)
        pc = cpu.pc
        cpu.step(assemble("add t0, one, one"))
        self.assertEqual(cpu.pc, pc)
        self.assertEqual(cpu.gprs_snapshot(), before)


if __name__ == "__main__":
    unittest.main()
