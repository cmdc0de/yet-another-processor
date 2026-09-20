"""FPGA-CPU m3 tests. Run from repo root: python3 -m unittest compiler.tests.test_fpga_cpu_m3"""

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
    spec = importlib.util.spec_from_file_location("fpga_cpu_sim_m3", SIM_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["fpga_cpu_sim_m3"] = mod
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


def _yap_words(words: dict[int, int], entry: int = 0) -> bytes:
    return pack(Yap1(load=0, entry=entry, payload=_payload(words)))


def _golden(payload: bytes, entry: int = 0, p: int = 1, ie: int = 0, ubase: int = 0, ulimit: int = 65536, irq: bool = False):
    cpu = Cpu()
    cpu.mem_store(0, payload)
    cpu.pc = entry
    cpu.p = p
    cpu.ie = ie
    cpu.ubase = ubase
    cpu.ulimit = ulimit
    if irq:
        cpu.irq()
    cpu.run()
    return cpu


def _sim(sim, payload: bytes, entry: int = 0, p: int = 1, ie: int = 0, ubase: int = 0, ulimit: int = 0x10000, irq: int = 0):
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "img.yap"
        dest.write_bytes(pack(Yap1(load=0, entry=entry, payload=payload)))
        r = sim.run_sim(dest, entry=entry, p=p, ie=ie, ubase=ubase, ulimit=ulimit, irq=irq)
    return _parse_dump(r.stdout), r


def _word(cpu, addr: int) -> str:
    return f"{int.from_bytes(cpu.mem[addr : addr + 4], 'little'):08x}"


def _assert_state(test, dump, cpu, gprs=True, sram_addrs=()):
    test.assertEqual(dump.get("halted"), "1")
    test.assertEqual(dump.get("pc"), f"{cpu.pc:08x}", "pc")
    test.assertEqual(dump.get("flags"), f"{cpu.flags_word():08x}", "flags")
    test.assertEqual(dump.get("cause"), f"{cpu.cause:08x}", "cause")
    test.assertEqual(dump.get("epc"), f"{cpu.epc:08x}", "epc")
    test.assertEqual(dump.get("status"), f"{cpu.status_word():08x}", "status")
    test.assertEqual(dump.get("ubase"), f"{cpu.ubase:08x}", "ubase")
    test.assertEqual(dump.get("ulimit"), f"{cpu.ulimit:08x}", "ulimit")
    if gprs:
        for i in range(32):
            test.assertEqual(dump.get(f"r{i}"), f"{cpu.read(i):08x}", f"r{i}")
    for addr in sram_addrs:
        test.assertEqual(dump.get(f"sram{addr}"), _word(cpu, addr), f"sram{addr}")


class TestFpgaCpuM3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sim = _load_sim()

    def test_FPGA_CPU_010(self):
        first = _insns_at(
            0,
            [
                "lui t0, 0xA1B2",
                "ori t0, t0, 0xC3D4",
                "sw t0, 16(zero)",
                "lw t0, 16(zero)",
                "j 0x80",
            ],
        )
        first[0x80] = assemble("halt")
        cases = [
            first,
            _insns_at(
                0,
                [
                    "addi t1, zero, 0x5A",
                    "sb t1, 20(zero)",
                    "lbu t0, 20(zero)",
                    "halt",
                ],
            ),
            _insns_at(
                0,
                [
                    "addi t1, zero, 8",
                    "lui t0, 0x1111",
                    "ori t0, t0, 0x2222",
                    "sw t0, 4(t1)",
                    "halt",
                ],
            ),
            _insns_at(
                0,
                [
                    "lui t0, 0x1234",
                    "ori t0, t0, 0x5678",
                    "sw t0, 0(zero)",
                    "halt",
                ],
            ),
        ]
        sram_need = [(16,), (20,), (12,), (0,)]
        for words, addrs in zip(cases, sram_need):
            with self.subTest(words=words):
                payload = _payload(words)
                dump, r = _sim(self.sim, payload)
                cpu = _golden(payload)
                self.assertEqual(r.returncode, 0, r.stderr or r.stdout)
                _assert_state(self, dump, cpu, sram_addrs=addrs)

        prot = {0x1000: assemble("lw t0, 0(zero)"), 0x80: assemble("halt")}
        payload = _payload(prot)
        dump, r = _sim(self.sim, payload, entry=0x1000, p=0, ubase=0x1000, ulimit=0x8000)
        cpu = _golden(payload, entry=0x1000, p=0, ubase=0x1000, ulimit=0x8000)
        self.assertEqual(dump.get("cause"), f"{cpu.cause:08x}")
        self.assertEqual(dump.get("cause"), "00000002")
        self.assertEqual(dump.get("sram0"), "00000000")
        self.assertEqual(dump.get("pc"), f"{cpu.pc:08x}")

        lw_align = {0: assemble("lw t0, 1(zero)"), 0x80: assemble("halt")}
        payload = _payload(lw_align)
        dump, _ = _sim(self.sim, payload)
        cpu = _golden(payload)
        self.assertEqual(dump.get("cause"), f"{cpu.cause:08x}")
        self.assertEqual(dump.get("cause"), "00000008")

        sw_align = {0: assemble("sw ones, 1(zero)"), 0x80: assemble("halt")}
        payload = _payload(sw_align)
        dump, _ = _sim(self.sim, payload)
        cpu = _golden(payload)
        self.assertEqual(dump.get("cause"), "00000008")
        self.assertEqual(dump.get("sram0"), _word(cpu, 0))

    def test_FPGA_CPU_011(self):
        images = [
            ({0: assemble("j 0x20"), 0x20: assemble("halt")}, 0),
            ({0: assemble("jal 0x20"), 0x20: assemble("halt")}, 0),
            (
                {
                    0: assemble("addi t0, zero, 0x20"),
                    4: assemble("jr t0"),
                    0x20: assemble("halt"),
                },
                0,
            ),
            (
                {
                    0: assemble("addi t0, zero, 0x20"),
                    4: assemble("jalr t1, t0"),
                    0x20: assemble("halt"),
                },
                0,
            ),
            (
                {
                    0: assemble("cmp one, one"),
                    4: assemble("beq 0x20", pc=4),
                    0x20: assemble("halt"),
                },
                0,
            ),
            (
                {
                    0: assemble("cmp one, zero"),
                    4: assemble("beq 0x20", pc=4),
                    8: assemble("halt"),
                },
                0,
            ),
            (
                {
                    0: assemble("cmp zero, one"),
                    4: assemble("blo 0x20", pc=4),
                    0x20: assemble("halt"),
                },
                0,
            ),
            (
                {
                    0: assemble("cmp zero, one"),
                    4: assemble("bhs 0x20", pc=4),
                    8: assemble("halt"),
                },
                0,
            ),
        ]
        for words, entry in images:
            with self.subTest(words=words):
                payload = _payload(words)
                dump, r = _sim(self.sim, payload, entry=entry)
                cpu = _golden(payload, entry=entry)
                self.assertEqual(r.returncode, 0, r.stderr or r.stdout)
                self.assertEqual(dump.get("pc"), f"{cpu.pc:08x}")
                self.assertEqual(dump.get("r3"), f"{cpu.read(parse_reg('ra')):08x}")
                self.assertEqual(dump.get("r11"), f"{cpu.read(parse_reg('t1')):08x}")

    def test_FPGA_CPU_013(self):
        ubase = _insns_at(
            0,
            [
                "addi t0, zero, 0x1000",
                "mtc0 t0, ubase",
                "mfc0 t1, ubase",
                "halt",
            ],
        )
        payload = _payload(ubase)
        dump, r = _sim(self.sim, payload)
        cpu = _golden(payload)
        self.assertEqual(r.returncode, 0, r.stderr or r.stdout)
        _assert_state(self, dump, cpu)

        cause = {0: assemble("lw t0, 1(zero)"), 0x80: assemble("mfc0 t1, cause"), 0x84: assemble("halt")}
        payload = _payload(cause)
        dump, _ = _sim(self.sim, payload)
        cpu = _golden(payload)
        self.assertEqual(dump.get("r11"), f"{cpu.read(parse_reg('t1')):08x}")
        self.assertEqual(int(dump.get("r11"), 16), 8)

        sysw = {0: assemble("sys 1"), 0x80: assemble("halt")}
        payload = _payload(sysw)
        dump, _ = _sim(self.sim, payload)
        cpu = _golden(payload)
        self.assertEqual(dump.get("cause"), f"{cpu.cause:08x}")
        self.assertEqual(dump.get("epc"), f"{cpu.epc:08x}")
        self.assertEqual(dump.get("cause"), "00000003")
        self.assertEqual(dump.get("epc"), "00000004")

        eret = _insns_at(
            0,
            [
                "addi t0, zero, 0x80",
                "mtc0 t0, epc",
                "addi t0, zero, 0x202",
                "mtc0 t0, status",
                "eret",
            ],
        )
        eret[0x80] = assemble("halt")
        payload = _payload(eret)
        dump, _ = _sim(self.sim, payload)
        cpu = _golden(payload)
        self.assertEqual(dump.get("halted"), "1")
        self.assertEqual(dump.get("pc"), f"{cpu.pc:08x}")
        self.assertEqual(dump.get("pc"), "00000080")
        self.assertEqual(dump.get("status"), f"{cpu.status_word():08x}")

        ueret = {0: assemble("eret"), 0x80: assemble("halt")}
        payload = _payload(ueret)
        dump, _ = _sim(self.sim, payload, p=0)
        cpu = _golden(payload, p=0)
        self.assertEqual(dump.get("cause"), f"{cpu.cause:08x}")
        self.assertEqual(dump.get("cause"), "00000007")

        te = {0: assemble("addi t0, zero, 4"), 4: assemble("mtc0 t0, status"), 0x80: assemble("halt")}
        payload = _payload(te)
        dump, _ = _sim(self.sim, payload)
        cpu = _golden(payload)
        self.assertEqual(dump.get("cause"), "00000007")
        self.assertEqual(dump.get("status"), f"{cpu.status_word():08x}")
        self.assertEqual(int(dump.get("status"), 16) & 4, 0)

        irq = {0: assemble("halt"), 0x80: assemble("halt")}
        payload = _payload(irq)
        dump, _ = _sim(self.sim, payload, ie=1, irq=1)
        cpu = _golden(payload, ie=1, irq=True)
        self.assertEqual(dump.get("cause"), f"{cpu.cause:08x}")
        self.assertEqual(dump.get("cause"), "00000001")
        self.assertEqual(dump.get("pc"), f"{cpu.pc:08x}")
        self.assertEqual(dump.get("pc"), "00000080")


if __name__ == "__main__":
    unittest.main()
