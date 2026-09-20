"""Physical CPU m8 tests. Run from repo root: python3 -m unittest compiler.tests.test_physical_cpu_m8

Needs `ngspice` on PATH (`ngspice -b`). Does not need KiCad.
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / "hw"
UCODE_DIR = HW / "ucode"
SCH = UCODE_DIR / "ucode.kicad_sch"
CIR = UCODE_DIR / "ucode_test.cir"
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


class TestPhysicalCpuM8(unittest.TestCase):
    def test_PHYSICAL_CPU_013(self):
        sch = SCH.read_text(encoding="utf-8")
        for net in ("upc0", "upc7", "cw0", "cw63"):
            self.assertRegex(sch, rf'\(label "{re.escape(net)}"')
        self.assertTrue("256x64" in sch or "256×64" in sch)
        self.assertNotIn("yap_cells:LATCH", sch)

        cir = CIR.read_text(encoding="utf-8")
        self.assertNotRegex(cir, r"\bLATCH\b")

        out = _ngspice(CIR)
        for i in range(8):
            self.assertLessEqual(_meas(out, f"upc{i}r"), VOL, f"reset upc{i}")
        for b in range(3):
            self.assertLessEqual(_meas(out, f"cw{b}r"), VOL, f"reset NEXT cw{b}")

        self.assertGreaterEqual(_meas(out, "upc0c"), VOH, "after clk upc=1")
        for i in range(1, 8):
            self.assertLessEqual(_meas(out, f"upc{i}c"), VOL, f"after clk upc{i}")

        cw0c, cw1c, cw2c = (_meas(out, f"cw{b}c") for b in range(3))
        cw0r, cw1r, cw2r = (_meas(out, f"cw{b}r") for b in range(3))
        after = (cw0c > 1.65, cw1c > 1.65, cw2c > 1.65)
        reset = (cw0r > 1.65, cw1r > 1.65, cw2r > 1.65)
        self.assertNotEqual(after, reset, "ROM[1] seq differs from ROM[0]")
        for b, v in enumerate((cw0c, cw1c, cw2c)):
            if v > 1.65:
                self.assertGreaterEqual(v, VOH, f"ROM[1] cw{b}")
            else:
                self.assertLessEqual(v, VOL, f"ROM[1] cw{b}")


if __name__ == "__main__":
    unittest.main()
