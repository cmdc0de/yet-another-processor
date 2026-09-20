"""Physical CPU m2 tests. Run from repo root: python3 -m unittest compiler.tests.test_physical_cpu_m2

Needs `ngspice` on PATH (`ngspice -b`). Does not need KiCad.
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / "hw"
FLAGS_DIR = HW / "flags"
ADDER_DIR = HW / "adder"
FLAGS_CIR = FLAGS_DIR / "flags_test.cir"
ADDER_CIR = ADDER_DIR / "adder_test.cir"
VOH = 3.0
VOL = 0.3

# CELL-012 table: a,b,cin = 000 .. 111
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
        cwd=cir.parent,
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


class TestPhysicalCpuM2(unittest.TestCase):
    def test_PHYSICAL_CPU_005(self):
        sch = (FLAGS_DIR / "flags.kicad_sch").read_text(encoding="utf-8")
        cir = FLAGS_CIR.read_text(encoding="utf-8")
        for net in ("D", "Q", "VDD", "VSS"):
            self.assertIn(net, sch, net)
        self.assertTrue(
            '(label "WE"' in sch or '(label "EN"' in sch,
            "flags schematic needs WE or EN",
        )
        self.assertRegex(cir, r"\bLATCH\b")
        self.assertIn("WE", cir)
        self.assertRegex(cir, r"\bWE\b.*\bLATCH\b")

    def test_PHYSICAL_CPU_006(self):
        sch = (ADDER_DIR / "adder.kicad_sch").read_text(encoding="utf-8")
        for net in ("a", "b", "cin", "sum", "cout"):
            self.assertRegex(sch, rf'\(label "{re.escape(net)}"')

    def test_PHYSICAL_CPU_007(self):
        cir = ADDER_CIR.read_text(encoding="utf-8")
        self.assertRegex(cir, r"\bADDER\b")
        out = _ngspice(ADDER_CIR)
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


if __name__ == "__main__":
    unittest.main()
