"""FPU m2 tests. Run from repo root: python3 -m unittest compiler.tests.test_fpu_m2

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
TB = FPU / "sim" / "tb_m2.v"


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


def _hex_field(out: str, name: str) -> int:
    m = re.search(rf"{name}=([0-9a-fA-F]+)", out)
    if not m:
        raise AssertionError(f"missing {name} in:\n{out}")
    return int(m.group(1), 16)


class TestFpuM2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = _run_sim()

    def test_FPU_006(self):
        self.assertEqual(_hex_field(self.out, "ADD"), 0x40400000)

    def test_FPU_007(self):
        self.assertEqual(_hex_field(self.out, "SUB"), 0x3F000000)

    def test_FPU_008(self):
        self.assertEqual(_hex_field(self.out, "MUL"), 0x40C00000)

    def test_FPU_009(self):
        self.assertEqual(_hex_field(self.out, "DIV"), 0x3F000000)
        self.assertEqual(_hex_field(self.out, "DIV0"), 0x7F800000)
        self.assertEqual(_hex_field(self.out, "DIV00"), 0x7FC00000)


if __name__ == "__main__":
    unittest.main()
