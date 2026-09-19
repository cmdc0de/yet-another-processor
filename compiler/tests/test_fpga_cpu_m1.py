"""FPGA-CPU m1 tests. Run from repo root: python3 -m unittest compiler.tests.test_fpga_cpu_m1"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

from compiler.yap1 import MAGIC, Yap1, pack
from compiler.yap_cpu.ucode import build_rom
from compiler.yap_isa import assemble

ROOT = Path(__file__).resolve().parents[2]
SIM_PY = ROOT / "emu" / "fpga-cpu" / "sim.py"
RTL = ROOT / "emu" / "fpga-cpu" / "rtl"


def _load_sim():
    spec = importlib.util.spec_from_file_location("fpga_cpu_sim", SIM_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["fpga_cpu_sim"] = mod
    spec.loader.exec_module(mod)
    return mod


def _yap(*insns: str) -> bytes:
    payload = b"".join(assemble(s).to_bytes(4, "little") for s in insns)
    return pack(Yap1(load=0, entry=0, payload=payload))


def _parse_dump(text: str) -> dict:
    out = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 2:
            out[parts[0]] = parts[1]
    return out


class TestFpgaCpuM1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sim = _load_sim()

    def test_FPGA_CPU_001(self):
        vers = list(RTL.glob("*.v"))
        self.assertTrue(vers, "emu/fpga-cpu/rtl/ should contain .v files")

    def test_FPGA_CPU_002(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "halt.yap"
            dest.write_bytes(_yap("halt"))
            header = dest.read_bytes()[:4]
            r = self.sim.run_sim(dest)
        dump = _parse_dump(r.stdout)
        self.assertEqual(dump.get("pc"), "00000000")
        self.assertEqual(int(dump.get("sram0", "0"), 16), assemble("halt"))
        self.assertNotEqual(header, assemble("halt").to_bytes(4, "little"))
        self.assertEqual(header, MAGIC)

    def test_FPGA_CPU_003(self):
        with tempfile.TemporaryDirectory() as tmp:
            halt = Path(tmp) / "halt.yap"
            nop = Path(tmp) / "nop.yap"
            halt.write_bytes(_yap("halt"))
            nop.write_bytes(_yap("nop"))
            h = self.sim.main([str(halt)])
            n = self.sim.main([str(nop), "--max-cycles", "8"])
        self.assertEqual(h, 0)
        self.assertNotEqual(n, 0)

    def test_FPGA_CPU_004(self):
        self.assertTrue(SIM_PY.is_file())

    def test_FPGA_CPU_005(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "halt.yap"
            dest.write_bytes(_yap("halt"))
            r = self.sim.run_sim(dest)
        dump = _parse_dump(r.stdout)
        self.assertGreater(int(dump.get("cycles", "0"), 16), 1)

    def test_FPGA_CPU_006(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "ucode.hex"
            rom = self.sim.write_ucode_hex(dest)
            lines = dest.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 256)
        self.assertTrue(all(len(x) == 16 for x in lines))
        self.assertEqual(lines[0], f"{build_rom()[0]:016x}")
        self.assertEqual(rom[0], build_rom()[0])

    def test_FPGA_CPU_012(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "halt.yap"
            dest.write_bytes(_yap("halt"))
            r = self.sim.run_sim(dest)
        dump = _parse_dump(r.stdout)
        self.assertEqual(dump.get("halted"), "1")
        self.assertEqual(dump.get("pc"), "00000000")
        self.assertEqual(int(dump.get("ir", "0"), 16), assemble("halt"))


if __name__ == "__main__":
    unittest.main()
