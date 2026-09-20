"""Physical CPU m10 tests. Run from repo root: python3 -m unittest compiler.tests.test_physical_cpu_m10

Needs `ngspice` on PATH (`ngspice -b`). Does not need KiCad.
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / "hw"
ALU_DIR = HW / "alu"
SCH = ALU_DIR / "alu.kicad_sch"
CIR = ALU_DIR / "alu_test.cir"
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


def _voltages(text: str, node: str) -> list[float]:
    pat = re.compile(rf"^v\({re.escape(node)}\)\s*=\s*([eE0-9.+-]+)", re.M | re.I)
    vals = [float(m.group(1)) for m in pat.finditer(text)]
    if not vals:
        raise AssertionError(f"no v({node}) prints in ngspice output:\n{text}")
    return vals


class TestPhysicalCpuM10(unittest.TestCase):
    def test_PHYSICAL_CPU_015(self):
        sch = SCH.read_text(encoding="utf-8")
        for net in ("a", "b", "y", "op0"):
            self.assertRegex(sch, rf'\(label "{re.escape(net)}"')
        self.assertNotIn("yap_cells:LATCH", sch)

        cir = CIR.read_text(encoding="utf-8")
        self.assertRegex(cir, r"\bADDER\b")
        self.assertTrue(
            re.search(r"\bAND\b", cir)
            or re.search(r"\bOR\b", cir)
            or re.search(r"\bXOR\b", cir),
            "need AND/OR/XOR",
        )

        out = _ngspice(CIR)
        y = _voltages(out, "y")
        c = _voltages(out, "cout")
        self.assertGreaterEqual(len(y), 4, out)
        # ADD 1+0+0
        self.assertGreaterEqual(y[0], VOH, "ADD y")
        self.assertLessEqual(c[0], VOL, "ADD cout")
        # SUB 1-0
        self.assertGreaterEqual(y[1], VOH, "SUB y")
        # AND 1&1
        self.assertGreaterEqual(y[2], VOH, "AND y")
        # XOR 1^1
        self.assertLessEqual(y[3], VOL, "XOR y")


if __name__ == "__main__":
    unittest.main()
