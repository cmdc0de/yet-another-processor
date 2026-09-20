"""Physical CPU m4 tests. Run from repo root: python3 -m unittest compiler.tests.test_physical_cpu_m4

Needs `ngspice` on PATH (`ngspice -b`). Does not need KiCad.
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / "hw"
REG32_DIR = HW / "reg32"
SCH = REG32_DIR / "reg32.kicad_sch"
CIR = REG32_DIR / "reg32_test.cir"
VOH = 3.0
VOL = 0.3
X_LATCH = re.compile(
    r"^X(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+LATCH\s*$",
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


class TestPhysicalCpuM4(unittest.TestCase):
    def test_PHYSICAL_CPU_009(self):
        sch = SCH.read_text(encoding="utf-8")
        for net in ("d0", "d31", "q0", "q31", "WE"):
            self.assertRegex(sch, rf'\(label "{re.escape(net)}"')

        cir = CIR.read_text(encoding="utf-8")
        inst = list(X_LATCH.finditer(cir))
        self.assertEqual(len(inst), 32, "need 32 LATCH instances")
        by_i = {int(m.group(1)): m for m in inst}
        self.assertEqual(set(by_i), set(range(32)))
        for i in range(32):
            m = by_i[i]
            d, en, q = m.group(2, 3, 4)
            self.assertEqual(d, f"d{i}")
            self.assertEqual(en, "WE", f"bit {i} EN should be WE")
            self.assertEqual(q, f"q{i}")

        out = _ngspice(CIR)
        for i in range(32):
            self.assertLessEqual(_meas(out, f"q{i}follow0"), VOL, f"q{i} follow 0")
            self.assertGreaterEqual(_meas(out, f"q{i}follow1"), VOH, f"q{i} follow 1")
            self.assertGreaterEqual(_meas(out, f"q{i}hold1"), VOH, f"q{i} hold 1")


if __name__ == "__main__":
    unittest.main()
