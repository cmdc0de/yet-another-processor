"""FPGA-CPU m4 tests. Run from repo root: python3 -m unittest compiler.tests.test_fpga_cpu_m4"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

from compiler.asm import main as asm_main
from compiler.yap1 import Yap1, pack
from compiler.yap_cpu import Cpu
from compiler.yap_isa import assemble, parse_reg
from compiler.yap_isa.encode import OPCODE, pack_r

ROOT = Path(__file__).resolve().parents[2]
SIM_PY = ROOT / "emu" / "fpga-cpu" / "sim.py"
KERNEL_S = ROOT / "os" / "kernel.s"


def _load_sim():
    spec = importlib.util.spec_from_file_location("fpga_cpu_sim_m4", SIM_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["fpga_cpu_sim_m4"] = mod
    spec.loader.exec_module(mod)
    return mod


def _parse_dump(text: str) -> dict:
    out = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 2:
            out[parts[0]] = parts[1]
    return out


def _payload(words: dict[int, int]) -> bytes:
    end = max(a + 4 for a in words)
    blob = bytearray(end)
    for addr, word in words.items():
        blob[addr : addr + 4] = int(word).to_bytes(4, "little")
    return bytes(blob)


def _insns_at(addr, texts):
    out = {}
    pc = addr
    for text in texts:
        out[pc] = assemble(text, pc=pc)
        pc += 4
    return out


def _golden(payload: bytes, entry: int = 0):
    cpu = Cpu()
    cpu.mem_store(0, payload)
    cpu.pc = entry
    cpu.run()
    return cpu


def _sim(sim, payload: bytes, entry: int = 0):
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "img.yap"
        dest.write_bytes(pack(Yap1(load=0, entry=entry, payload=payload)))
        r = sim.run_sim(dest, entry=entry)
    return _parse_dump(r.stdout), r


class TestFpgaCpuM4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sim = _load_sim()

    def test_FPGA_CPU_014(self):
        words = _insns_at(
            0,
            [
                "lui t0, 0xA5A5",
                "ori t0, t0, 0xA5A5",
                "mtc1 t0, f0",
                "mfc1 t1, f0",
                "halt",
            ],
        )
        payload = _payload(words)
        dump, r = _sim(self.sim, payload)
        cpu = _golden(payload)
        self.assertEqual(r.returncode, 0, r.stderr or r.stdout)
        self.assertEqual(dump.get("halted"), "1")
        self.assertEqual(dump.get("r11"), f"{cpu.read(parse_reg('t1')):08x}")
        self.assertEqual(int(dump.get("r11"), 16), 0xA5A5A5A5)

        bad = {0: pack_r(0, 1, 0, 0, 0, opcode=OPCODE["cop1"]), 0x80: assemble("halt")}
        payload = _payload(bad)
        dump, _ = _sim(self.sim, payload)
        cpu = _golden(payload)
        self.assertEqual(dump.get("cause"), f"{cpu.cause:08x}")
        self.assertEqual(dump.get("cause"), "00000006")
        self.assertEqual(dump.get("pc"), f"{cpu.pc:08x}")

    def test_FPGA_CPU_015(self):
        images = [
            _insns_at(0, ["add t0, one, one", "halt"]),
            _insns_at(0, ["sll t0, one, 3", "halt"]),
            _insns_at(0, ["div t0, ones, one", "halt"]),
            {0: assemble("cmp one, one"), 4: assemble("beq 0x20", pc=4), 0x20: assemble("halt")},
            {0: assemble("sys 1"), 0x80: assemble("halt")},
            _insns_at(
                0,
                [
                    "lui t0, 0xA5A5",
                    "ori t0, t0, 0xA5A5",
                    "mtc1 t0, f0",
                    "mfc1 t1, f0",
                    "halt",
                ],
            ),
        ]
        for words in images:
            with self.subTest(words=words):
                payload = _payload(words)
                dump, r = _sim(self.sim, payload)
                cpu = _golden(payload)
                self.assertEqual(r.returncode, 0, r.stderr or r.stdout)
                self.assertEqual(dump.get("halted"), "1")
                self.assertEqual(dump.get("flags"), f"{cpu.flags_word():08x}")
                self.assertEqual(dump.get("cause"), f"{cpu.cause:08x}")
                for i in range(32):
                    self.assertEqual(dump.get(f"r{i}"), f"{cpu.read(i):08x}", f"r{i}")

    def test_FPGA_CPU_016(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "kernel.yap"
            self.assertEqual(asm_main([str(KERNEL_S), "-o", str(dest)]), 0)
            rc = self.sim.main([str(dest)])
            r = self.sim.run_sim(dest)
        dump = _parse_dump(r.stdout)
        self.assertEqual(rc, 0, r.stderr or r.stdout)
        self.assertEqual(dump.get("halted"), "1")


if __name__ == "__main__":
    unittest.main()
