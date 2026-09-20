"""Physical CPU m6 tests. Run from repo root: python3 -m unittest compiler.tests.test_physical_cpu_m6

Needs `ngspice` on PATH (`ngspice -b`). Does not need KiCad.
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / "hw"
RF_DIR = HW / "rf-mosfet"
SCH = RF_DIR / "rf_mosfet.kicad_sch"
CIR = RF_DIR / "rf_mosfet_test.cir"
VOH = 3.0
VOL = 0.3
X_LATCH = re.compile(
    r"^Xr(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+LATCH\s*$",
    re.M,
)


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


class TestPhysicalCpuM6(unittest.TestCase):
    def test_PHYSICAL_CPU_011(self):
        sch = SCH.read_text(encoding="utf-8")
        for net in ("we3", "we15", "qa", "qb"):
            self.assertRegex(sch, rf'\(label "{re.escape(net)}"')
        self.assertIn("LAT=1", sch)

        cir = CIR.read_text(encoding="utf-8")
        self.assertTrue(
            re.search(r"\bMUX2\b", cir) or re.search(r"\bTG\b", cir),
            "read mux MUX2 or TG",
        )
        inst = list(X_LATCH.finditer(cir))
        self.assertEqual(len(inst), 13, "need 13 LATCH r3-r15")
        by_i = {int(m.group(1)): m for m in inst}
        self.assertEqual(set(by_i), set(range(3, 16)))
        for i in range(3, 16):
            m = by_i[i]
            d, en, q = m.group(2, 3, 4)
            self.assertEqual(d, "d")
            self.assertEqual(en, f"we{i}")
            self.assertEqual(q, f"q{i}")

        out = _ngspice(CIR)
        self.assertGreaterEqual(_meas(out, "qameas"), VOH, "qa from r3")
        self.assertLessEqual(_meas(out, "qbmeas"), VOL, "qb from r4")


if __name__ == "__main__":
    unittest.main()
