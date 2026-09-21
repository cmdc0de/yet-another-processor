"""MCU m1 tests. Run from repo root: python3 -m unittest compiler.tests.test_mcu_m1

Needs Icarus Verilog (`iverilog`, `vvp` on PATH).
"""

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MCU = ROOT / "hw" / "mcu"
RTL = MCU / "rtl" / "mcu.v"
TB = MCU / "sim" / "tb.v"

OFFSETS = (
    ("STATUS", "0x00"),
    ("KEY_DATA", "0x04"),
    ("SER_DATA", "0x08"),
    ("STOR_LBA", "0x0C"),
    ("STOR_IDX", "0x10"),
    ("STOR_DATA", "0x14"),
    ("STOR_CMD", "0x18"),
)


def _require_icarus():
    iverilog = shutil.which("iverilog")
    vvp = shutil.which("vvp")
    if not iverilog or not vvp:
        raise AssertionError(
            "iverilog/vvp not on PATH; install Icarus Verilog. Missing binary is a failure."
        )
    return iverilog, vvp


def _run_sim() -> str:
    iverilog, vvp = _require_icarus()
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
        return (r.stdout or "") + (r.stderr or "")


class TestMcuM1(unittest.TestCase):
    def test_MCU_001(self):
        vers = list(MCU.glob("**/*.v"))
        self.assertTrue(vers, "hw/mcu/ should contain Verilog-2001 .v files")

    def test_MCU_003(self):
        self.assertTrue(shutil.which("iverilog"), "iverilog not on PATH")
        self.assertTrue(shutil.which("vvp"), "vvp not on PATH")

    def test_MCU_002(self):
        _run_sim()

    def test_MCU_004(self):
        rtl = RTL.read_text(encoding="utf-8")
        tb = TB.read_text(encoding="utf-8")
        for name in ("clk", "rst", "we", "re", "addr", "wdata", "rdata"):
            self.assertRegex(rtl, rf"\b{name}\b")
            self.assertRegex(tb, rf"\b{name}\b")
        self.assertRegex(rtl, r"\[7:0\]\s+addr")
        self.assertRegex(rtl, r"\[31:0\]\s+wdata")
        self.assertRegex(rtl, r"\[31:0\]\s+rdata")

    def test_MCU_005(self):
        text = RTL.read_text(encoding="utf-8") + TB.read_text(encoding="utf-8")
        for name, off in OFFSETS:
            self.assertIn(name, text)
            self.assertIn(off, text)

    def test_MCU_006(self):
        out = _run_sim()
        m = re.search(r"STATUS=([0-9a-fA-F]+)", out)
        self.assertTrue(m, out)
        self.assertEqual(int(m.group(1), 16), 0)

    def test_MCU_011(self):
        rtl = RTL.read_text(encoding="utf-8")
        self.assertIn("3.3", rtl)
        self.assertNotIn("5 V MCU", rtl)
        self.assertNotIn("5V MCU", rtl)


if __name__ == "__main__":
    unittest.main()
