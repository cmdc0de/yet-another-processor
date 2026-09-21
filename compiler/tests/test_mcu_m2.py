"""MCU m2 tests. Run from repo root: python3 -m unittest compiler.tests.test_mcu_m2

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
TB = MCU / "sim" / "tb_m2.v"


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


def _hex_field(out: str, name: str) -> int:
    m = re.search(rf"{name}=([0-9a-fA-F]+)", out)
    if not m:
        raise AssertionError(f"missing {name} in:\n{out}")
    return int(m.group(1), 16)


class TestMcuM2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = _run_sim()

    def test_MCU_007(self):
        self.assertEqual(_hex_field(self.out, "KEY_STATUS"), 0x1)
        self.assertEqual(_hex_field(self.out, "KEY_DATA"), 0x41)
        self.assertEqual(_hex_field(self.out, "KEY_STATUS2"), 0)

    def test_MCU_008(self):
        m = re.search(r"SER_TX=([0-9a-fA-F]+)\s+STB=([01])", self.out)
        self.assertTrue(m, self.out)
        self.assertEqual(int(m.group(1), 16), 0x42)
        self.assertEqual(m.group(2), "1")

    def test_MCU_009(self):
        self.assertEqual(_hex_field(self.out, "SER_STATUS"), 0x2)
        self.assertEqual(_hex_field(self.out, "SER_DATA"), 0x43)
        self.assertEqual(_hex_field(self.out, "SER_STATUS2"), 0)

    def test_MCU_010(self):
        self.assertEqual(_hex_field(self.out, "STOR_W0"), 0xA5A5A5A5)
        self.assertEqual(_hex_field(self.out, "STOR_W1"), 0x12345678)


if __name__ == "__main__":
    unittest.main()
