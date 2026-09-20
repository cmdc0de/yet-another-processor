"""FPGA-CPU m2 tests. Run from repo root: python3 -m unittest compiler.tests.test_fpga_cpu_m2"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

from compiler.yap1 import Yap1, pack
from compiler.yap_cpu import Cpu
from compiler.yap_isa import assemble, parse_reg

ROOT = Path(__file__).resolve().parents[2]
SIM_PY = ROOT / "emu" / "fpga-cpu" / "sim.py"


def _load_sim():
    spec = importlib.util.spec_from_file_location("fpga_cpu_sim_m2", SIM_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["fpga_cpu_sim_m2"] = mod
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


def _golden(insns):
    cpu = Cpu()
    blob = b"".join(assemble(s).to_bytes(4, "little") for s in insns)
    cpu.mem_store(0, blob)
    cpu.run()
    return cpu


def _sim_dump(sim, insns):
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "img.yap"
        dest.write_bytes(_yap(*insns))
        r = sim.run_sim(dest)
    return _parse_dump(r.stdout), r


def _assert_gprs_flags(test, dump, cpu):
    test.assertEqual(dump.get("halted"), "1")
    test.assertEqual(dump.get("flags"), f"{cpu.flags_word():08x}")
    for i in range(32):
        test.assertEqual(dump.get(f"r{i}"), f"{cpu.read(i):08x}", f"r{i}")


class TestFpgaCpuM2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sim = _load_sim()

    def test_FPGA_CPU_007(self):
        mos, _ = _sim_dump(self.sim, ["add t0, t0, one", "halt"])
        ic, _ = _sim_dump(self.sim, ["add s0, s0, one", "halt"])
        self.assertEqual(mos.get("halted"), "1")
        self.assertEqual(ic.get("halted"), "1")
        self.assertGreater(int(ic["cycles"], 16), int(mos["cycles"], 16))

    def test_FPGA_CPU_008(self):
        insns = ["add t0, one, one", "halt"]
        dump, _ = _sim_dump(self.sim, insns)
        cpu = _golden(insns)
        self.assertEqual(dump.get("halted"), "1")
        self.assertEqual(dump.get("pc"), f"{cpu.pc:08x}")
        self.assertEqual(dump.get("flags"), f"{cpu.flags_word():08x}")
        self.assertEqual(dump.get("r10"), f"{cpu.read(parse_reg('t0')):08x}")

    def test_FPGA_CPU_009(self):
        images = [
            ["and t0, ones, one", "halt"],
            ["xor t0, one, one", "halt"],
            ["sll t0, one, 1", "halt"],
            ["sra t0, ones, 1", "halt"],
            ["mul t0, one, one", "halt"],
            ["div t0, one, zero", "halt"],
            ["addi t0, one, -1", "halt"],
            ["andi t0, ones, 0xFF", "halt"],
            ["lui t0, 1", "halt"],
            ["adr t0, 4", "halt"],
        ]
        for insns in images:
            with self.subTest(insns=insns):
                dump, r = _sim_dump(self.sim, insns)
                cpu = _golden(insns)
                self.assertEqual(r.returncode, 0, r.stderr or r.stdout)
                _assert_gprs_flags(self, dump, cpu)


if __name__ == "__main__":
    unittest.main()
