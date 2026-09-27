"""FPU m3 tests. Run from repo root: python3 -m unittest compiler.tests.test_fpu_m3"""

import tempfile
import unittest
from pathlib import Path

from compiler.asm import assemble_source, main
from compiler.tests.test_os_m1 import KERNEL_S, ROOT, _emu
from compiler.yap1 import unpack
from compiler.yap_isa import Cpu, OPCODE, assemble, parse_reg, unpack_r
from compiler.yap_isa.csrs import COP1_FMT_S

OS_DIR = ROOT / "os"
USER_MARK = ".org 0x1000"


def _kernel_prefix() -> str:
    text = KERNEL_S.read_text(encoding="utf-8")
    i = text.find(USER_MARK)
    if i < 0:
        raise RuntimeError("kernel.s missing user .org 0x1000")
    return text[:i]


def _run_python(data: bytes) -> Cpu:
    image = unpack(data)
    cpu = Cpu(mem_size=max(65536, image.load + image.size))
    cpu.mem_store(image.load, image.payload)
    cpu.pc = image.entry
    for _ in range(100000):
        if cpu.halted:
            break
        word = int.from_bytes(cpu.mem_load(cpu.pc, 4), "little")
        cpu.step(word)
    return cpu


class TestFpuM3(unittest.TestCase):
    def test_FPU_010(self):
        add = unpack_r(assemble("add.s f1, f2, f3"))
        self.assertEqual(add["opcode"], OPCODE["cop1"])
        self.assertEqual(add["rs"], COP1_FMT_S)
        self.assertEqual(add["rd"], 1)
        self.assertEqual(add["rt"], 2)
        self.assertEqual(add["shamt"], 3)
        self.assertEqual(add["funct"], 0)
        self.assertEqual(unpack_r(assemble("sub.s f1, f2, f3"))["funct"], 1)
        self.assertEqual(unpack_r(assemble("mul.s f1, f2, f3"))["funct"], 2)
        self.assertEqual(unpack_r(assemble("div.s f1, f2, f3"))["funct"], 3)

    def test_FPU_011(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "fpu_save.yap"
            data = assemble_source(
                _kernel_prefix() + (OS_DIR / "user_fpu_save.s").read_text(encoding="utf-8"),
                path=str(OS_DIR / "user_fpu_save.s"),
            )
            dest.write_bytes(data)
            r = _emu(dest)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertRegex(r.stdout, r"r11 a5a5a5a5")
            cpu = _run_python(data)
            self.assertTrue(cpu.halted)
            self.assertEqual(cpu.read(parse_reg("t1")), 0xA5A5A5A5)
            kernel = KERNEL_S.read_text(encoding="utf-8")
            self.assertIn("mtc1 zero, f0", kernel)


if __name__ == "__main__":
    unittest.main()
