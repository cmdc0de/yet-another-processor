"""OS m2 tests. Run from repo root: python3 -m unittest compiler.tests.test_os_m2"""

import tempfile
import unittest
from pathlib import Path

from compiler.asm import main
from compiler.tests.test_os_m1 import KERNEL_S, _emu
from compiler.yap1 import unpack
from compiler.yap_isa import Cpu, OPCODE, unpack_r


def _assemble(dest: Path) -> bytes:
    rc = main([str(KERNEL_S), "-o", str(dest)])
    if rc != 0:
        raise RuntimeError("assemble failed")
    return dest.read_bytes()


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


class TestOsM2(unittest.TestCase):
    def test_OS_004(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "kernel.yap"
            _assemble(dest)
            r = _emu(dest)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertRegex(r.stdout, r"ubase 00001000")
            self.assertRegex(r.stdout, r"ulimit 00008000")

    def test_OS_005(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "kernel.yap"
            data = _assemble(dest)
            image = unpack(data)
            word = int.from_bytes(image.payload[0x1000:0x1004], "little")
            fields = unpack_r(word)
            self.assertEqual(fields["opcode"], OPCODE["sys"])
            self.assertEqual(fields["imm16"], 1)

    def test_OS_007(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "kernel.yap"
            data = _assemble(dest)
            image = unpack(data)
            halt = (0x2C).to_bytes(4, "little")
            self.assertNotEqual(image.payload[0:4], halt)
            word = int.from_bytes(image.payload[0x1000:0x1004], "little")
            fields = unpack_r(word)
            self.assertEqual(fields["opcode"], OPCODE["sys"])
            self.assertEqual(fields["imm16"], 1)

    def test_OS_008(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "kernel.yap"
            _assemble(dest)
            r = _emu(dest)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertRegex(r.stdout, r"r4 00008000")

    def test_OS_009(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "kernel.yap"
            data = _assemble(dest)
            cpu = _run_python(data)
            self.assertTrue(cpu.halted)
            saved = int.from_bytes(cpu.mem[0xFFC:0x1000], "little")
            self.assertEqual(saved, 0x8000)

    def test_OS_010(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "kernel.yap"
            _assemble(dest)
            r = _emu(dest)
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_OS_013(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "kernel.yap"
            data = _assemble(dest)
            image = unpack(data)
            word = int.from_bytes(image.payload[0x1000:0x1004], "little")
            fields = unpack_r(word)
            self.assertEqual(fields["opcode"], OPCODE["sys"])
            self.assertEqual(fields["imm16"], 1)

    def test_OS_014(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "kernel.yap"
            _assemble(dest)
            r = _emu(dest)
            self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
