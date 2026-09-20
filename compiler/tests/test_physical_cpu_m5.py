"""Physical CPU m5 tests. Run from repo root: python3 -m unittest compiler.tests.test_physical_cpu_m5

Needs `ngspice` on PATH (`ngspice -b`). Does not need KiCad.
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / "hw"
WIRED_DIR = HW / "wired"
SCH = WIRED_DIR / "wired.kicad_sch"
CIR = WIRED_DIR / "wired_test.cir"
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


def _voltages(text: str, node: str) -> list[float]:
    pat = re.compile(rf"^v\({re.escape(node)}\)\s*=\s*([eE0-9.+-]+)", re.M | re.I)
    vals = [float(m.group(1)) for m in pat.finditer(text)]
    if not vals:
        raise AssertionError(f"no v({node}) prints in ngspice output:\n{text}")
    return vals


class TestPhysicalCpuM5(unittest.TestCase):
    def test_PHYSICAL_CPU_010(self):
        sch = SCH.read_text(encoding="utf-8")
        for net in ("r0_0", "r1_0", "r2_31"):
            self.assertRegex(sch, rf'\(label "{re.escape(net)}"')
        self.assertNotRegex(sch, r"\bLATCH\b")

        cir = CIR.read_text(encoding="utf-8")
        self.assertNotRegex(cir, r"\bLATCH\b")

        out = _ngspice(CIR)
        for b in range(32):
            v0 = _voltages(out, f"r0_{b}")[0]
            self.assertLessEqual(v0, VOL, f"r0_{b}")
            v2 = _voltages(out, f"r2_{b}")[0]
            self.assertGreaterEqual(v2, VOH, f"r2_{b}")
            v1 = _voltages(out, f"r1_{b}")[0]
            if b == 0:
                self.assertGreaterEqual(v1, VOH, "r1_0")
            else:
                self.assertLessEqual(v1, VOL, f"r1_{b}")


if __name__ == "__main__":
    unittest.main()
