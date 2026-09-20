"""MOSFET cells m2 tests. Run from repo root: python3 -m unittest compiler.tests.test_cells_m2

Needs `ngspice` on PATH (`ngspice -b`).
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LT = ROOT / "lt-spice"
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
        cwd=LT,
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


class TestCellsM2(unittest.TestCase):
    def test_CELL_006_nor(self):
        vs = _voltages(_ngspice(LT / "nor_test.cir"), "y")
        self.assertGreaterEqual(len(vs), 4, vs)
        self.assertGreaterEqual(vs[0], VOH)
        self.assertLessEqual(vs[1], VOL)
        self.assertLessEqual(vs[2], VOL)
        self.assertLessEqual(vs[3], VOL)

    def test_CELL_007_and(self):
        vs = _voltages(_ngspice(LT / "and_test.cir"), "y")
        self.assertGreaterEqual(len(vs), 4, vs)
        self.assertLessEqual(vs[0], VOL)
        self.assertLessEqual(vs[1], VOL)
        self.assertLessEqual(vs[2], VOL)
        self.assertGreaterEqual(vs[3], VOH)

    def test_CELL_008_or(self):
        vs = _voltages(_ngspice(LT / "or_test.cir"), "y")
        self.assertGreaterEqual(len(vs), 4, vs)
        self.assertLessEqual(vs[0], VOL)
        self.assertGreaterEqual(vs[1], VOH)
        self.assertGreaterEqual(vs[2], VOH)
        self.assertGreaterEqual(vs[3], VOH)

    def test_CELL_009_xor(self):
        vs = _voltages(_ngspice(LT / "xor_test.cir"), "y")
        self.assertGreaterEqual(len(vs), 4, vs)
        self.assertLessEqual(vs[0], VOL)
        self.assertGreaterEqual(vs[1], VOH)
        self.assertGreaterEqual(vs[2], VOH)
        self.assertLessEqual(vs[3], VOL)

    def test_CELL_010_tg(self):
        vs = _voltages(_ngspice(LT / "tg_test.cir"), "out")
        self.assertGreaterEqual(len(vs), 4, vs)
        self.assertLessEqual(vs[0], VOL)
        self.assertGreaterEqual(vs[1], VOH)
        self.assertLess(vs[2], VOH)
        self.assertGreater(vs[2], VOL)
        self.assertLess(vs[3], VOH)
        self.assertGreater(vs[3], VOL)

    def test_CELL_011_mux2(self):
        vs = _voltages(_ngspice(LT / "mux2_test.cir"), "y")
        self.assertGreaterEqual(len(vs), 8, vs)
        expect_high = [False, False, True, True, False, True, False, True]
        for i, high in enumerate(expect_high):
            if high:
                self.assertGreaterEqual(vs[i], VOH, f"idx {i}")
            else:
                self.assertLessEqual(vs[i], VOL, f"idx {i}")


if __name__ == "__main__":
    unittest.main()
