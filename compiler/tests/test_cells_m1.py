"""MOSFET cells m1 tests. Run from repo root: python3 -m unittest compiler.tests.test_cells_m1

Needs `ngspice` on PATH (`ngspice -b`). Missing binary fails (CELL-018).
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LT = ROOT / "lt-spice"
LIB = LT / "yap_cells.lib"
INV_CIR = LT / "inverter_test.cir"
NAND_CIR = LT / "nand_test.cir"
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


class TestCellsM1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ngspice = shutil.which("ngspice")

    def test_CELL_018_ngspice_batch(self):
        self.assertIsNotNone(
            self.ngspice,
            "ngspice not on PATH; install ngspice (ngspice -b). Missing binary is a failure.",
        )
        out = subprocess.run(
            [self.ngspice, "-b", INV_CIR.name],
            cwd=LT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(out.returncode, 0, out.stderr or out.stdout)
        self.assertNotIn("ltspice", (out.stdout + out.stderr).lower())

    def test_CELL_001_rails(self):
        for path in (INV_CIR, NAND_CIR):
            text = path.read_text(encoding="utf-8")
            self.assertRegex(text, r"\b3\.3\b")
            self.assertRegex(text, r"VDD\s+\w+\s+0\s+DC\s+3\.3")
            self.assertRegex(text, r"\s0\s")

    def test_CELL_002_models(self):
        lib = LIB.read_text(encoding="utf-8")
        self.assertRegex(lib, r"\.model\s+IRLML6246\b")
        self.assertRegex(lib, r"\.model\s+IRLML6401\b")
        self.assertNotIn("AO3400", lib)
        self.assertNotIn("AO3401A", lib)
        inv = _ngspice(INV_CIR)
        nand = _ngspice(NAND_CIR)
        blob = lib + inv + nand
        self.assertIn("IRLML6246", blob)
        self.assertIn("IRLML6401", blob)

    def test_CELL_004_inverter(self):
        out = _ngspice(INV_CIR)
        vs = _voltages(out, "out")
        self.assertGreaterEqual(len(vs), 2, out)
        self.assertGreaterEqual(vs[0], VOH)
        self.assertLessEqual(vs[1], VOL)

    def test_CELL_005_nand(self):
        out = _ngspice(NAND_CIR)
        vs = _voltages(out, "y")
        self.assertGreaterEqual(len(vs), 4, out)
        self.assertGreaterEqual(vs[0], VOH)
        self.assertGreaterEqual(vs[1], VOH)
        self.assertGreaterEqual(vs[2], VOH)
        self.assertLessEqual(vs[3], VOL)

    def test_CELL_014_levels(self):
        inv = _voltages(_ngspice(INV_CIR), "out")
        nand = _voltages(_ngspice(NAND_CIR), "y")
        highs = [inv[0], nand[0], nand[1], nand[2]]
        lows = [inv[1], nand[3]]
        for v in highs:
            self.assertGreaterEqual(v, VOH)
        for v in lows:
            self.assertLessEqual(v, VOL)


if __name__ == "__main__":
    unittest.main()
