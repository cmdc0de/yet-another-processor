"""Physical CPU m3 tests. Run from repo root: python3 -m unittest compiler.tests.test_physical_cpu_m3

Needs `ngspice` on PATH (`ngspice -b`). Does not need KiCad.
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / "hw"
ADDER32_DIR = HW / "adder32"
SCH = ADDER32_DIR / "adder32.kicad_sch"
CIR = ADDER32_DIR / "adder32_test.cir"
VOH = 3.0
VOL = 0.3
X_ADDER = re.compile(
    r"^X(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+ADDER\s*$",
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


def _voltages(text: str, node: str) -> list[float]:
    pat = re.compile(rf"^v\({re.escape(node)}\)\s*=\s*([eE0-9.+-]+)", re.M | re.I)
    vals = [float(m.group(1)) for m in pat.finditer(text)]
    if not vals:
        raise AssertionError(f"no v({node}) prints in ngspice output:\n{text}")
    return vals


class TestPhysicalCpuM3(unittest.TestCase):
    def test_PHYSICAL_CPU_008(self):
        sch = SCH.read_text(encoding="utf-8")
        for net in ("a0", "a31", "sum0", "sum31"):
            self.assertRegex(sch, rf'\(label "{re.escape(net)}"')

        cir = CIR.read_text(encoding="utf-8")
        inst = list(X_ADDER.finditer(cir))
        self.assertEqual(len(inst), 32, "need 32 ADDER instances")
        by_i = {int(m.group(1)): m for m in inst}
        self.assertEqual(set(by_i), set(range(32)))
        for i in range(32):
            m = by_i[i]
            a, b, cin, s, cout = m.group(2, 3, 4, 5, 6)
            self.assertEqual(a, f"a{i}")
            self.assertEqual(b, f"b{i}")
            self.assertEqual(s, f"sum{i}")
            if i == 0:
                self.assertEqual(cin, "cin")
            else:
                self.assertEqual(cin, f"c{i-1}", f"bit {i} cin")
            if i == 31:
                self.assertEqual(cout, "cout")
            else:
                self.assertEqual(cout, f"c{i}", f"bit {i} cout")

        out = _ngspice(CIR)
        for i in range(32):
            sums = _voltages(out, f"sum{i}")
            self.assertGreaterEqual(len(sums), 2, f"sum{i}")
            self.assertLessEqual(sums[0], VOL, f"zero sum{i}")
            self.assertLessEqual(sums[1], VOL, f"ones+1 sum{i}")
        couts = _voltages(out, "cout")
        self.assertGreaterEqual(len(couts), 2, out)
        self.assertLessEqual(couts[0], VOL, "zero cout")
        self.assertGreaterEqual(couts[1], VOH, "ones+1 cout")


if __name__ == "__main__":
    unittest.main()
