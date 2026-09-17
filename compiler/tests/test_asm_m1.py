"""Assembler m1 tests. Run from repo root: python3 -m unittest compiler.tests.test_asm_m1"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from compiler.asm import AsmError, assemble_source, main
from compiler.yap1 import MAGIC, unpack
from compiler.yap_isa import OPCODE, assemble as isa_assemble, unpack_r
from compiler.yap_isa.regs import NAME_TO_NUM

ROOT = Path(__file__).resolve().parents[2]


class TestAsmM1(unittest.TestCase):
    def test_COMPILER_001(self):
        data = assemble_source("nop\nhalt\n")
        self.assertGreater(len(data), 16)
        image = unpack(data)
        nop = isa_assemble("nop").to_bytes(4, "little")
        halt = isa_assemble("halt").to_bytes(4, "little")
        self.assertEqual(image.payload, nop + halt)

    def test_COMPILER_002(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "a.s"
            src.write_text("nop\n", encoding="utf-8")
            missing = subprocess.run(
                [sys.executable, "-m", "compiler.asm", str(src)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(missing.returncode, 0)
            out = Path(tmp) / "out.yap"
            rc = main([str(src), "-o", str(out)])
            self.assertEqual(rc, 0)
            self.assertTrue(out.is_file())

    def test_COMPILER_003(self):
        data = assemble_source("nop\nnop\nnop\n")
        image = unpack(data)
        self.assertEqual(image.size, 12)
        nop = isa_assemble("nop").to_bytes(4, "little")
        self.assertEqual(image.payload, nop * 3)

    def test_COMPILER_023(self):
        data = assemble_source("nop\n")
        self.assertEqual(data[:4], MAGIC)
        image = unpack(data)
        self.assertEqual(image.load, 0)
        self.assertEqual(image.entry, 0)
        self.assertEqual(image.size, len(data) - 16)
        bad = bytearray(data)
        bad[8:12] = (99).to_bytes(4, "little")
        with self.assertRaises(Exception):
            unpack(bytes(bad))

    def test_COMPILER_004(self):
        plain = unpack(assemble_source("nop\n")).payload
        self.assertEqual(unpack(assemble_source("nop ; hi\n")).payload, plain)
        self.assertEqual(unpack(assemble_source("nop # hi\n")).payload, plain)

    def test_COMPILER_005(self):
        a = unpack(assemble_source("ADD t0, one, one\n")).payload
        b = unpack(assemble_source("add t0, one, one\n")).payload
        self.assertEqual(a, b)

    def test_COMPILER_006(self):
        image = unpack(assemble_source("add sp, zero, one\n"))
        word = int.from_bytes(image.payload, "little")
        self.assertEqual(unpack_r(word)["rd"], NAME_TO_NUM["sp"])
        self.assertEqual(unpack_r(word)["rd"], 4)

    def test_COMPILER_007(self):
        image = unpack(assemble_source("lw t0, 4(sp)\n"))
        fields = unpack_r(int.from_bytes(image.payload, "little"))
        self.assertEqual(fields["opcode"], OPCODE["lw"])
        self.assertEqual(fields["rs"], NAME_TO_NUM["sp"])
        self.assertEqual(fields["imm16"], 4)

    def test_COMPILER_018(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "bad.s"
            src.write_text("nop\nnop\nblorp t0, t0\n", encoding="utf-8")
            dest = Path(tmp) / "out.yap"
            with self.assertRaises(AsmError) as ctx:
                from compiler.asm import assemble_file

                assemble_file(src)
            self.assertEqual(ctx.exception.line_no, 3)
            self.assertIn(":3:", str(ctx.exception))
            from io import StringIO
            from unittest import mock

            with mock.patch("sys.stderr", StringIO()):
                rc = main([str(src), "-o", str(dest)])
            self.assertNotEqual(rc, 0)
            self.assertFalse(dest.exists())

    def test_COMPILER_019(self):
        with self.assertRaises(AsmError):
            assemble_source("blorp t0, t0\n")


if __name__ == "__main__":
    unittest.main()
