"""MOSFET cells m3 tests. Run from repo root: python3 -m unittest compiler.tests.test_cells_m3

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

CELLS = (
    ("inverter_test.cir", "INVERTER"),
    ("nand_test.cir", "NAND"),
    ("nor_test.cir", "NOR"),
    ("and_test.cir", "AND"),
    ("or_test.cir", "OR"),
    ("xor_test.cir", "XOR"),
    ("tg_test.cir", "TG"),
    ("mux2_test.cir", "MUX2"),
    ("latch_test.cir", "LATCH"),
    ("adder_test.cir", "ADDER"),
)

ADDER_SUM = (0, 1, 1, 0, 1, 0, 0, 1)
ADDER_COUT = (0, 0, 0, 1, 0, 1, 1, 1)


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


def _meas(text: str, name: str) -> float:
    pat = re.compile(rf"^{re.escape(name)}\s*=\s*([eE0-9.+-]+)", re.M | re.I)
    m = pat.search(text)
    if not m:
        raise AssertionError(f"no meas {name} in:\n{text}")
    return float(m.group(1))


class TestCellsM3(unittest.TestCase):
    def test_CELL_012_adder_table(self):
        out = _ngspice(LT / "adder_test.cir")
        s = _voltages(out, "sum")
        c = _voltages(out, "cout")
        self.assertGreaterEqual(len(s), 8, out)
        self.assertGreaterEqual(len(c), 8, out)
        for i, (bit_s, bit_c) in enumerate(zip(ADDER_SUM, ADDER_COUT)):
            if bit_s:
                self.assertGreaterEqual(s[i], VOH, f"sum[{i}]")
            else:
                self.assertLessEqual(s[i], VOL, f"sum[{i}]")
            if bit_c:
                self.assertGreaterEqual(c[i], VOH, f"cout[{i}]")
            else:
                self.assertLessEqual(c[i], VOL, f"cout[{i}]")

    def test_CELL_013_latch_follow(self):
        out = _ngspice(LT / "latch_test.cir")
        self.assertLessEqual(_meas(out, "qfollow0"), VOL)
        self.assertGreaterEqual(_meas(out, "qfollow1"), VOH)

    def test_CELL_015_benches(self):
        for fname, subckt in CELLS:
            path = LT / fname
            self.assertTrue(path.is_file(), fname)
            text = path.read_text(encoding="utf-8")
            self.assertIn(".include yap_cells.lib", text)
            self.assertRegex(text, rf"\b{subckt}\b")

    def test_CELL_016_latch_hold(self):
        out = _ngspice(LT / "latch_test.cir")
        self.assertGreaterEqual(_meas(out, "qhold1"), VOH)
        self.assertLessEqual(_meas(out, "qhold0"), VOL)

    def test_CELL_017_adder_corners(self):
        out = _ngspice(LT / "adder_test.cir")
        s = _voltages(out, "sum")
        c = _voltages(out, "cout")
        self.assertLessEqual(s[0], VOL)
        self.assertLessEqual(c[0], VOL)
        self.assertGreaterEqual(s[7], VOH)
        self.assertGreaterEqual(c[7], VOH)


if __name__ == "__main__":
    unittest.main()
