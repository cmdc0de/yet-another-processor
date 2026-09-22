"""Power m1 tests. Run from repo root: python3 -m unittest compiler.tests.test_power_m1

Needs `ngspice` on PATH (`ngspice -b`). Missing binary fails (POWER-003).
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PWR = ROOT / "hw" / "power"
SUB = PWR / "reg33.subckt"
CIR = PWR / "rails_test.cir"
VDD_MIN = 3.20
VDD_MAX = 3.40


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


class TestPowerM1(unittest.TestCase):
    def test_POWER_001(self):
        srcs = list(PWR.glob("**/*.cir")) + list(PWR.glob("**/*.subckt"))
        self.assertTrue(srcs, "hw/power/ should contain SPICE .cir / .subckt sources")

    def test_POWER_003(self):
        self.assertTrue(shutil.which("ngspice"), "ngspice not on PATH")

    def test_POWER_002(self):
        _ngspice(CIR)

    def test_POWER_004(self):
        text = SUB.read_text(encoding="utf-8") + CIR.read_text(encoding="utf-8")
        self.assertIn("VIN", text)
        self.assertIn("VSS", text)
        self.assertRegex(CIR.read_text(encoding="utf-8"), r"DC\s+5\.0")
        self.assertRegex(CIR.read_text(encoding="utf-8"), r"\s0\s")

    def test_POWER_005(self):
        sub = SUB.read_text(encoding="utf-8")
        cir = CIR.read_text(encoding="utf-8")
        self.assertRegex(sub, r"\.subckt\s+REG33\s+VIN\s+VDD\s+VSS")
        self.assertRegex(cir, r"\bREG33\b")

    def test_POWER_006(self):
        out = _ngspice(CIR)
        vs = _voltages(out, "vdd")
        self.assertGreaterEqual(vs[-1], VDD_MIN, out)
        self.assertLessEqual(vs[-1], VDD_MAX, out)

    def test_POWER_007(self):
        text = SUB.read_text(encoding="utf-8") + CIR.read_text(encoding="utf-8")
        self.assertIn("CPU core, SRAM/bus, and MCU I/O use VDD (not VIN)", text)


if __name__ == "__main__":
    unittest.main()
