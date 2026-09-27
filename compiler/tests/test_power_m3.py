"""Power m3 tests. Run from repo root: python3 -m unittest compiler.tests.test_power_m3

Needs `ngspice` on PATH (`ngspice -b`).
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PWR = ROOT / "hw" / "power"
SCH = PWR / "ldo.kicad_sch"
SUB = PWR / "reg33.subckt"
CIR = PWR / "en_test.cir"
VDD_MIN = 3.20
VDD_MAX = 3.40
VDD_OFF = 0.3


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


class TestPowerM3(unittest.TestCase):
    def test_POWER_010(self):
        blob = (
            SCH.read_text(encoding="utf-8")
            + SUB.read_text(encoding="utf-8")
            + CIR.read_text(encoding="utf-8")
        )
        self.assertIn("EN", blob)
        self.assertRegex(CIR.read_text(encoding="utf-8"), r"\bEN\b|\ben\b")
        out = _ngspice(CIR)
        vs = _voltages(out, "vdd")
        self.assertGreaterEqual(len(vs), 2, out)
        self.assertGreaterEqual(vs[0], VDD_MIN, out)
        self.assertLessEqual(vs[0], VDD_MAX, out)
        self.assertLessEqual(vs[1], VDD_OFF, out)


if __name__ == "__main__":
    unittest.main()
