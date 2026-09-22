"""FPU m1 tests. Run from repo root: python3 -m unittest compiler.tests.test_fpu_m1

Needs Icarus Verilog (`iverilog`, `vvp` on PATH).
"""

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FPU = ROOT / "fpu"
RTL = FPU / "rtl" / "fpu.v"
TB = FPU / "sim" / "tb.v"


def _require_icarus():
    iverilog = shutil.which("iverilog")
    vvp = shutil.which("vvp")
    if not iverilog or not vvp:
        raise AssertionError(
            "iverilog/vvp not on PATH; install Icarus Verilog. Missing binary is a failure."
        )
    return iverilog, vvp


def _run_sim() -> str:
    iverilog, vvp = _require_icarus()
    with tempfile.TemporaryDirectory() as tmp:
        simv = Path(tmp) / "simv"
        c = subprocess.run(
            [iverilog, "-o", str(simv), str(RTL), str(TB)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if c.returncode != 0:
            raise RuntimeError(c.stderr or c.stdout or "iverilog failed")
        r = subprocess.run(
            [vvp, str(simv)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            raise RuntimeError(r.stderr or r.stdout or "vvp failed")
        return (r.stdout or "") + (r.stderr or "")


class TestFpuM1(unittest.TestCase):
    def test_FPU_001(self):
        vers = list(FPU.glob("**/*.v"))
        self.assertTrue(vers, "fpu/ should contain Verilog-2001 .v files")

    def test_FPU_003(self):
        self.assertTrue(shutil.which("iverilog"), "iverilog not on PATH")
        self.assertTrue(shutil.which("vvp"), "vvp not on PATH")

    def test_FPU_002(self):
        _run_sim()

    def test_FPU_004(self):
        text = RTL.read_text(encoding="utf-8") + TB.read_text(encoding="utf-8")
        self.assertTrue(
            "binary32" in text or "IEEE-754" in text,
            "sources should name IEEE-754 binary32",
        )
        self.assertIn("binary32", text)

    def test_FPU_005(self):
        out = _run_sim()
        for i in range(32):
            m = re.search(rf"F{i}=([0-9a-fA-F]+)", out)
            self.assertTrue(m, f"missing F{i} in:\n{out}")
            self.assertEqual(int(m.group(1), 16), 0, f"F{i}")


if __name__ == "__main__":
    unittest.main()
