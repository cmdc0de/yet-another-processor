"""Memory-bus m1 tests. Run from repo root: python3 -m unittest compiler.tests.test_memory_bus_m1

Needs Icarus Verilog (`iverilog`, `vvp` on PATH).
"""

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUS = ROOT / "hw" / "bus"
RTL = BUS / "rtl" / "bus.v"
TB = BUS / "sim" / "tb.v"


def _run_sim() -> str:
    iverilog = shutil.which("iverilog")
    vvp = shutil.which("vvp")
    if not iverilog or not vvp:
        raise AssertionError(
            "iverilog/vvp not on PATH; install Icarus Verilog. Missing binary is a failure."
        )
    with tempfile.TemporaryDirectory() as tmp:
        simv = Path(tmp) / "simv"
        c = subprocess.run(
            [iverilog, "-o", str(simv), str(RTL), str(TB)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if c.returncode != 0:
            raise RuntimeError(c.stderr or c.stdout or "iverilog failed")
        r = subprocess.run(
            [vvp, str(simv)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            raise RuntimeError(r.stderr or r.stdout or "vvp failed")
        return r.stdout + r.stderr


class TestMemoryBusM1(unittest.TestCase):
    def test_MEMORY_BUS_006(self):
        vers = list(BUS.glob("**/*.v"))
        self.assertTrue(vers, "hw/bus/ should contain Verilog-2001 .v files")

    def test_MEMORY_BUS_008(self):
        self.assertTrue(shutil.which("iverilog"), "iverilog not on PATH")
        self.assertTrue(shutil.which("vvp"), "vvp not on PATH")

    def test_MEMORY_BUS_002(self):
        rtl = RTL.read_text(encoding="utf-8")
        tb = TB.read_text(encoding="utf-8")
        for name in ("addr", "size", "re", "we"):
            self.assertRegex(rtl, rf"\b{name}\b")
            self.assertRegex(tb, rf"\b{name}\b")
        self.assertRegex(rtl, r"\[31:0\]\s+addr")
        self.assertRegex(rtl, r"\[2:0\]\s+size")

    def test_MEMORY_BUS_009(self):
        rtl = RTL.read_text(encoding="utf-8")
        self.assertIn("3.3", rtl)
        self.assertNotIn("5 V SRAM", rtl)
        self.assertNotIn("5V SRAM", rtl)

    def test_MEMORY_BUS_001(self):
        out = _run_sim()
        we = re.search(r"AFTER_WE mem0=([0-9a-fA-F]+)", out)
        commit = re.search(r"AFTER_COMMIT mem0=([0-9a-fA-F]+) rdata=([0-9a-fA-F]+)", out)
        self.assertTrue(we, out)
        self.assertTrue(commit, out)
        self.assertEqual(int(we.group(1), 16), 0, "write must not commit combinationally on clock 0")
        self.assertEqual(int(commit.group(1), 16), 0xA5A5A5A5)
        self.assertEqual(int(commit.group(2), 16), 0, "rdata not valid on the command cycle")

    def test_MEMORY_BUS_007(self):
        out = _run_sim()
        done = re.search(r"AFTER_RE rdata=([0-9a-fA-F]+)", out)
        self.assertTrue(done, out)
        self.assertEqual(int(done.group(1), 16), 0xA5A5A5A5)


if __name__ == "__main__":
    unittest.main()
