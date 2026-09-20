"""Physical CPU m9 tests. Run from repo root: python3 -m unittest compiler.tests.test_physical_cpu_m9

Needs `ngspice` on PATH (`ngspice -b`). Does not need KiCad.
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / "hw"
PORT_DIR = HW / "memport"
SCH = PORT_DIR / "memport.kicad_sch"
CIR = PORT_DIR / "memport_test.cir"
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


class TestPhysicalCpuM9(unittest.TestCase):
    def test_PHYSICAL_CPU_014(self):
        sch = SCH.read_text(encoding="utf-8")
        for net in ("addr0", "addr31", "wdata0", "rdata0", "sz0", "re", "we"):
            self.assertRegex(sch, rf'\(label "{re.escape(net)}"')
        self.assertIn("LAT_MEM=1", sch)

        out = _ngspice(CIR)
        self.assertGreaterEqual(_meas(out, "r0"), VOH, "rdata0 after we+clk+re")
        self.assertLessEqual(_meas(out, "r1"), VOL, "rdata1 after we+clk+re")


if __name__ == "__main__":
    unittest.main()
