"""Physical CPU m7 tests. Run from repo root: python3 -m unittest compiler.tests.test_physical_cpu_m7

Needs `ngspice` on PATH (`ngspice -b`). Does not need KiCad.
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / "hw"
RF_DIR = HW / "rf-ic"
SCH = RF_DIR / "rf_ic.kicad_sch"
CIR = RF_DIR / "rf_ic_test.cir"
VOH = 3.0
VOL = 0.3
X_ICREG = re.compile(
    r"^Xr(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+ICREG\s*$",
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


class TestPhysicalCpuM7(unittest.TestCase):
    def test_PHYSICAL_CPU_012(self):
        sch = SCH.read_text(encoding="utf-8")
        for net in ("we16", "we31", "qa", "qb"):
            self.assertRegex(sch, rf'\(label "{re.escape(net)}"')
        self.assertIn("LAT=2", sch)
        self.assertNotIn("yap_cells:LATCH", sch)

        cir = CIR.read_text(encoding="utf-8")
        self.assertNotRegex(cir, r"\bLATCH\b")
        inst = list(X_ICREG.finditer(cir))
        self.assertEqual(len(inst), 16, "need 16 ICREG r16-r31")
        by_i = {int(m.group(1)): m for m in inst}
        self.assertEqual(set(by_i), set(range(16, 32)))
        for i in range(16, 32):
            m = by_i[i]
            d, en, q = m.group(2, 3, 4)
            self.assertEqual(d, "d")
            self.assertEqual(en, f"we{i}")
            self.assertEqual(q, f"q{i}")

        out = _ngspice(CIR)
        self.assertGreaterEqual(_meas(out, "qameas"), VOH, "qa from r16")
        self.assertLessEqual(_meas(out, "qbmeas"), VOL, "qb from r17")


if __name__ == "__main__":
    unittest.main()
