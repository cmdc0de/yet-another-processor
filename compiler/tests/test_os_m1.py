"""OS m1 tests. Run from repo root: python3 -m unittest compiler.tests.test_os_m1"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from compiler.asm import main
from compiler.yap1 import unpack
from compiler.yap_isa import assemble as isa_assemble

ROOT = Path(__file__).resolve().parents[2]
KERNEL_S = ROOT / "os" / "kernel.s"


def _emu(image: Path) -> subprocess.CompletedProcess:
    bin_path = ROOT / "emu" / "rust" / "target" / "debug" / "yap-emu"
    if bin_path.is_file():
        return subprocess.run([str(bin_path), str(image)], cwd=ROOT, capture_output=True, text=True)
    return subprocess.run(
        ["cargo", "run", "--manifest-path", str(ROOT / "emu" / "rust" / "Cargo.toml"), "--quiet", "--", str(image)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


class TestOsM1(unittest.TestCase):
    def _assemble(self, dest: Path) -> int:
        return main([str(KERNEL_S), "-o", str(dest)])

    def test_OS_001(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "kernel.yap"
            self.assertEqual(self._assemble(dest), 0)
            image = unpack(dest.read_bytes())
            self.assertGreaterEqual(len(image.payload), 0x84)
            trap = image.payload[0x80:0x84]
            self.assertNotEqual(trap, b"\x00\x00\x00\x00")
            reset = image.payload[0:4]
            self.assertNotEqual(reset, trap)

    def test_OS_002(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "kernel.yap"
            self.assertEqual(self._assemble(dest), 0)
            r = _emu(dest)
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_OS_003(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "kernel.yap"
            self.assertEqual(self._assemble(dest), 0)
            r = _emu(dest)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertRegex(r.stdout, r"r4 00008000")

    def test_OS_018(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "k.yap"
            rc = subprocess.run(
                [sys.executable, "-m", "compiler.asm", str(KERNEL_S), "-o", str(dest)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(rc.returncode, 0, rc.stderr)
            self.assertTrue(dest.is_file())

    def test_OS_019(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "kernel.yap"
            self.assertEqual(self._assemble(dest), 0)
            r = _emu(dest)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(dest.is_file())


if __name__ == "__main__":
    unittest.main()
