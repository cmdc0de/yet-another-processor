"""Assembler m4 tests. Run from repo root: python3 -m unittest compiler.tests.test_asm_m4"""

import tempfile
import unittest
from pathlib import Path

from compiler.asm import assemble_source, main
from compiler.yap1 import unpack
from compiler.yap_isa import OPCODE, Cpu, assemble as isa_assemble, unpack_r
from compiler.yap_isa.regs import NAME_TO_NUM


class TestAsmM4(unittest.TestCase):
    def test_COMPILER_015(self):
        image = unpack(assemble_source("li t0, 1\n"))
        self.assertEqual(len(image.payload), 4)
        self.assertEqual(image.payload, isa_assemble("addi t0, zero, 1").to_bytes(4, "little"))
        fields = unpack_r(int.from_bytes(image.payload, "little"))
        self.assertEqual(fields["opcode"], OPCODE["addi"])

        image = unpack(assemble_source("li t0, 0x12345678\n"))
        self.assertEqual(len(image.payload), 8)
        lui = int.from_bytes(image.payload[0:4], "little")
        ori = int.from_bytes(image.payload[4:8], "little")
        self.assertEqual(unpack_r(lui)["opcode"], OPCODE["lui"])
        self.assertEqual(unpack_r(ori)["opcode"], OPCODE["ori"])
        cpu = Cpu()
        t0 = NAME_TO_NUM["t0"]
        cpu.step(lui)
        cpu.step(ori)
        self.assertEqual(cpu.read(t0), 0x12345678)

    def test_COMPILER_016(self):
        moved = unpack(assemble_source("move t0, sp\n")).payload
        add = unpack(assemble_source("add t0, sp, zero\n")).payload
        self.assertEqual(moved, add)

    def test_COMPILER_017(self):
        image = unpack(assemble_source("lab: nop\nla t0, lab\n"))
        self.assertEqual(len(image.payload), 8)
        la_word = int.from_bytes(image.payload[4:8], "little")
        self.assertEqual(unpack_r(la_word)["opcode"], OPCODE["adr"])

        image = unpack(assemble_source("la t0, far\n.org 0x20000\nfar: nop\n"))
        self.assertEqual(len(image.payload[:8]), 8)
        lui = int.from_bytes(image.payload[0:4], "little")
        ori = int.from_bytes(image.payload[4:8], "little")
        self.assertEqual(unpack_r(lui)["opcode"], OPCODE["lui"])
        self.assertEqual(unpack_r(ori)["opcode"], OPCODE["ori"])
        cpu = Cpu()
        t0 = NAME_TO_NUM["t0"]
        cpu.step(lui)
        cpu.step(ori)
        self.assertEqual(cpu.read(t0), 0x20000)

    def test_COMPILER_020(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "halt.s"
            src.write_text("nop\nhalt\n", encoding="utf-8")
            out = Path(tmp) / "h.yap"
            rc = main([str(src), "-o", str(out), "--run"])
            self.assertEqual(rc, 0)
            self.assertTrue(out.is_file())

            loop = Path(tmp) / "loop.s"
            loop.write_text("j loop\nloop: j loop\n", encoding="utf-8")
            lout = Path(tmp) / "loop.yap"
            rc = main([str(loop), "-o", str(lout), "--run", "--max-steps", "1000"])
            self.assertNotEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
