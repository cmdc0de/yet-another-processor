"""OS m3 tests. Run from repo root: python3 -m unittest compiler.tests.test_os_m3"""

import tempfile
import unittest
from pathlib import Path

from compiler.asm import assemble_source, main
from compiler.tests.test_os_m1 import KERNEL_S, ROOT, _emu
from compiler.yap1 import unpack
from compiler.yap_isa import Cpu, OPCODE, unpack_r

OS_DIR = ROOT / "os"
USER_MARK = ".org 0x1000"
MSG = b"yap"
YLOG = b"YLOG"
KPAN = b"KPAN"


def _kernel_prefix() -> str:
    text = KERNEL_S.read_text(encoding="utf-8")
    i = text.find(USER_MARK)
    if i < 0:
        raise RuntimeError("kernel.s missing user .org 0x1000")
    return text[:i]


def _assemble_kernel(dest: Path) -> bytes:
    rc = main([str(KERNEL_S), "-o", str(dest)])
    if rc != 0:
        raise RuntimeError("assemble kernel failed")
    return dest.read_bytes()


def _assemble_user(name: str, dest: Path) -> bytes:
    user_path = OS_DIR / name
    data = assemble_source(_kernel_prefix() + user_path.read_text(encoding="utf-8"), path=str(user_path))
    dest.write_bytes(data)
    return data


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


class TestOsM3(unittest.TestCase):
    def test_OS_015(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "kernel.yap"
            data = _assemble_kernel(dest)
            r = _emu(dest)
            self.assertEqual(r.returncode, 0, r.stderr)
            cpu = _run_python(data)
            self.assertTrue(cpu.halted)
            self.assertEqual(bytes(cpu.mem[0x800:0x804]), YLOG)
            length = int.from_bytes(cpu.mem[0x804:0x808], "little")
            self.assertEqual(length, len(MSG))
            self.assertEqual(bytes(cpu.mem[0x808 : 0x808 + length]), MSG)

    def test_OS_016(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "bad_sys.yap"
            data = _assemble_user("user_bad_sys.s", dest)
            r = _emu(dest)
            self.assertEqual(r.returncode, 0, r.stderr)
            cpu = _run_python(data)
            self.assertTrue(cpu.halted)
            stored = int.from_bytes(cpu.mem[0x1100:0x1104], "little")
            self.assertNotEqual(stored, 0)

    def test_OS_017(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "bad_write.yap"
            data = _assemble_user("user_bad_write.s", dest)
            r = _emu(dest)
            self.assertEqual(r.returncode, 0, r.stderr)
            cpu = _run_python(data)
            self.assertTrue(cpu.halted)
            self.assertEqual(bytes(cpu.mem[0x800:0x804]), YLOG)
            length = int.from_bytes(cpu.mem[0x804:0x808], "little")
            self.assertEqual(length, 0)

    def test_OS_006(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "prot.yap"
            data = _assemble_user("user_prot.s", dest)
            r = _emu(dest)
            self.assertEqual(r.returncode, 0, r.stderr)
            cpu = _run_python(data)
            self.assertTrue(cpu.halted)
            self.assertEqual(cpu.cause, 2)

    def test_OS_011(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "align.yap"
            data = _assemble_user("user_align.s", dest)
            r = _emu(dest)
            self.assertEqual(r.returncode, 0, r.stderr)
            cpu = _run_python(data)
            self.assertTrue(cpu.halted)
            self.assertEqual(cpu.cause, 8)

    def test_OS_012(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "cop1.yap"
            data = _assemble_user("user_cop1.s", dest)
            r = _emu(dest)
            self.assertEqual(r.returncode, 0, r.stderr)
            cpu = _run_python(data)
            self.assertTrue(cpu.halted)
            self.assertEqual(bytes(cpu.mem[0x800:0x804]), KPAN)


if __name__ == "__main__":
    unittest.main()
