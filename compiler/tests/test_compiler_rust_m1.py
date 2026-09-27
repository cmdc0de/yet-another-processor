"""compiler-rust m1 tests. Run from repo root: python3 -m unittest compiler.tests.test_compiler_rust_m1

Needs `cargo`/`rustc` on PATH. Missing binary fails (COMPILER-RUST-003).
"""

import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

from compiler.tests.test_os_m1 import ROOT, _emu
from compiler.yap_isa import OPCODE, unpack_r

CRATE = ROOT / "compiler" / "rust"
MANIFEST = CRATE / "Cargo.toml"
EXAMPLE = CRATE / "examples" / "empty.ys"


def _require_cargo():
    cargo = shutil.which("cargo")
    rustc = shutil.which("rustc")
    if not cargo or not rustc:
        raise AssertionError(
            "cargo/rustc not on PATH; install Rust. Missing binary is a failure."
        )
    return cargo


def _compile(ys: Path, dest: Path) -> subprocess.CompletedProcess:
    cargo = _require_cargo()
    return subprocess.run(
        [
            cargo,
            "run",
            "--manifest-path",
            str(MANIFEST),
            "--quiet",
            "--",
            str(ys),
            "-o",
            str(dest),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


class TestCompilerRustM1(unittest.TestCase):
    def test_COMPILER_RUST_001(self):
        self.assertTrue((CRATE / "Cargo.toml").is_file())
        self.assertTrue((CRATE / "src" / "main.rs").is_file())

    def test_COMPILER_RUST_003(self):
        self.assertTrue(shutil.which("cargo"), "cargo not on PATH")
        self.assertTrue(shutil.which("rustc"), "rustc not on PATH")

    def test_COMPILER_RUST_002(self):
        cargo = _require_cargo()
        r = subprocess.run(
            [cargo, "build", "--manifest-path", str(MANIFEST), "--quiet"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_COMPILER_RUST_006(self):
        text = EXAMPLE.read_text(encoding="utf-8")
        self.assertTrue(EXAMPLE.name.endswith(".ys"))
        self.assertIn("fn main()", text)

    def test_COMPILER_RUST_004(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out.yap"
            r = _compile(EXAMPLE, dest)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(dest.is_file())

    def test_COMPILER_RUST_005(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out.yap"
            r = _compile(EXAMPLE, dest)
            self.assertEqual(r.returncode, 0, r.stderr)
            data = dest.read_bytes()
            self.assertGreaterEqual(len(data), 16)
            magic, load, size, entry = struct.unpack_from("<4sIII", data, 0)
            self.assertEqual(magic, b"YAP1")
            self.assertEqual(load, 0)
            self.assertEqual(entry, 0)
            self.assertEqual(size, len(data) - 16)

    def test_COMPILER_RUST_008(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out.yap"
            r = _compile(EXAMPLE, dest)
            self.assertEqual(r.returncode, 0, r.stderr)
            data = dest.read_bytes()
            word = int.from_bytes(data[16:20], "little")
            fields = unpack_r(word)
            self.assertEqual(fields["opcode"], OPCODE["j"])
            self.assertEqual(fields["opcode"], 0b000010)
            self.assertEqual((fields["target26"] << 2) & 0xFFFFFFFF, 0x84)

    def test_COMPILER_RUST_010(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out.yap"
            r = _compile(EXAMPLE, dest)
            self.assertEqual(r.returncode, 0, r.stderr)
            emu = _emu(dest)
            self.assertEqual(emu.returncode, 0, emu.stderr)


if __name__ == "__main__":
    unittest.main()
