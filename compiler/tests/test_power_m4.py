"""Power m4 tests. Run from repo root: python3 -m unittest compiler.tests.test_power_m4

Needs `ngspice` on PATH (`ngspice -b`).
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PWR = ROOT / "hw" / "power"
SUB = PWR / "lvlsh.subckt"
CIR = PWR / "lvlsh_test.cir"
LV_MIN = 3.20
LV_MAX = 3.40
HV_MIN = 4.75
HV_MAX = 5.25


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
    return (r.stdout or "") + (r.stderr or "")


def _voltages(text: str, node: str) -> list[float]:
    pat = re.compile(rf"^v\({re.escape(node)}\)\s*=\s*([eE0-9.+-]+)", re.M | re.I)
    vals = [float(m.group(1)) for m in pat.finditer(text)]
    if not vals:
        raise AssertionError(f"no v({node}) prints in ngspice output:\n{text}")
    return vals


class TestPowerM4(unittest.TestCase):
    def test_POWER_009(self):
        blob = SUB.read_text(encoding="utf-8") + CIR.read_text(encoding="utf-8")
        self.assertIn("IO5", blob)
        self.assertIn("IO33", blob)
        self.assertRegex(blob, r"\.subckt\s+LVLSH\s+HV\s+LV\s+VSS")
        self.assertRegex(CIR.read_text(encoding="utf-8"), r"\bLVLSH\b")
        out = _ngspice(CIR)
        lv = _voltages(out, "io33")
        hv = _voltages(out, "io5_up")
        self.assertGreaterEqual(lv[-1], LV_MIN, out)
        self.assertLessEqual(lv[-1], LV_MAX, out)
        self.assertGreaterEqual(hv[-1], HV_MIN, out)
        self.assertLessEqual(hv[-1], HV_MAX, out)


if __name__ == "__main__":
    unittest.main()
