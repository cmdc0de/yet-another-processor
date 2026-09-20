"""Physical CPU m1 tests. Run from repo root: python3 -m unittest compiler.tests.test_physical_cpu_m1

Needs `ngspice` on PATH (`ngspice -b`). Does not need KiCad.
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / "hw"
LATCH_DIR = HW / "latch"
CIR = LATCH_DIR / "latch_test.cir"
VOH = 3.0
VOL = 0.3


def _ngspice(cir: Path) -> str:
    exe = shutil.which("ngspice")
    if not exe:
        raise AssertionError(
            "ngspice not on PATH; install ngspice (ngspice -b). Missing binary is a failure."
        )
    r = subprocess.run(
        [exe, "-b", str(cir.name)],
        cwd=cir.parent,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr or r.stdout or "ngspice failed")
    return r.stdout + r.stderr


def _meas(text: str, name: str) -> float:
    pat = re.compile(rf"^{re.escape(name)}\s*=\s*([eE0-9.+-]+)", re.M | re.I)
    m = pat.search(text)
    if not m:
        raise AssertionError(f"no meas {name} in:\n{text}")
    return float(m.group(1))


class TestPhysicalCpuM1(unittest.TestCase):
    def test_PHYSICAL_CPU_001(self):
        schs = list(HW.glob("**/*.kicad_sch"))
        self.assertTrue(schs, "hw/ should contain a .kicad_sch")

    def test_PHYSICAL_CPU_002(self):
        sch = (LATCH_DIR / "latch.kicad_sch").read_text(encoding="utf-8")
        cir = CIR.read_text(encoding="utf-8")
        self.assertIn("LATCH", sch)
        self.assertIn("LATCH", cir)
        self.assertRegex(cir, r"\bLATCH\b")

    def test_PHYSICAL_CPU_003(self):
        sch = (LATCH_DIR / "latch.kicad_sch").read_text(encoding="utf-8")
        for net in ("D", "EN", "Q", "VDD", "VSS"):
            self.assertIn(net, sch, net)

    def test_PHYSICAL_CPU_004(self):
        out = _ngspice(CIR)
        self.assertLessEqual(_meas(out, "qfollow0"), VOL)
        self.assertGreaterEqual(_meas(out, "qfollow1"), VOH)
        self.assertGreaterEqual(_meas(out, "qhold1"), VOH)
        self.assertLessEqual(_meas(out, "qhold0"), VOL)


if __name__ == "__main__":
    unittest.main()
