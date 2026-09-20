"""Memory-bus m2 tests. Run from repo root: python3 -m unittest compiler.tests.test_memory_bus_m2

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
TB = BUS / "sim" / "tb_m2.v"


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
        )
        text = (r.stdout or b"").decode("utf-8", errors="replace")
        err = (r.stderr or b"").decode("utf-8", errors="replace")
        if r.returncode != 0:
            raise RuntimeError(err or text or "vvp failed")
        return text + err


def _field(out: str, prefix: str, name: str) -> str:
    m = re.search(rf"^{re.escape(prefix)} .*\b{name}=(\S+)", out, re.M)
    if not m:
        raise AssertionError(f"no {prefix} {name} in:\n{out}")
    return m.group(1)


class TestMemoryBusM2(unittest.TestCase):
    def test_MEMORY_BUS_003(self):
        out = _run_sim()
        self.assertEqual(_field(out, "IDLE", "dq_z"), "1", out)
        self.assertEqual(_field(out, "STORE_CMD", "dq_z"), "0", out)
        self.assertEqual(_field(out, "LOAD_DATA", "dq_z"), "0", out)
        self.assertEqual(int(_field(out, "LOAD_DATA", "dq"), 16), 0xA5A5A5A5)

    def test_MEMORY_BUS_004(self):
        out = _run_sim()
        word = int(re.search(r"AFTER_WORD mem0=([0-9a-fA-F]+)", out).group(1), 16)
        self.assertEqual(word, 0xA5A5A5A5, out)
        byt = int(re.search(r"AFTER_BYTE mem0=([0-9a-fA-F]+)", out).group(1), 16)
        self.assertEqual(byt & 0xFFFFFF00, 0xA5A5A500, hex(byt))
        self.assertEqual(byt & 0xFF, 0x5A, hex(byt))
        half = int(re.search(r"AFTER_HALF mem0=([0-9a-fA-F]+)", out).group(1), 16)
        self.assertEqual(half & 0xFFFF, byt & 0xFFFF, hex(half))

    def test_MEMORY_BUS_005(self):
        out = _run_sim()
        self.assertEqual(_field(out, "STORE_CMD", "ce_n"), "0")
        self.assertEqual(_field(out, "STORE_CMD", "we_n"), "0")
        self.assertEqual(_field(out, "STORE_CMD", "oe_n"), "1")
        self.assertEqual(_field(out, "LOAD_CMD", "ce_n"), "0")
        self.assertEqual(_field(out, "LOAD_CMD", "oe_n"), "0")
        self.assertEqual(_field(out, "LOAD_CMD", "we_n"), "1")
        self.assertEqual(_field(out, "IDLE", "ce_n"), "1")
        self.assertEqual(_field(out, "IDLE", "oe_n"), "1")
        self.assertEqual(_field(out, "IDLE", "we_n"), "1")


if __name__ == "__main__":
    unittest.main()
