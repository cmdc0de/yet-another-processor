"""compiler-rust m2 tests. Run from repo root: python3 -m unittest compiler.tests.test_compiler_rust_m2"""

import struct
import tempfile
import unittest
from pathlib import Path

from compiler.tests.test_compiler_rust_m1 import CRATE, _compile
from compiler.tests.test_os_m1 import _emu
from compiler.yap_isa import OPCODE, OPCODE_SPECIAL, unpack_r
from compiler.yap_isa.encode import FUNCT

ADD_YS = CRATE / "examples" / "add.ys"
FUNCT_JR = FUNCT["jr"]
FUNCT_ADD = FUNCT["add"]
FUNCT_SUB = FUNCT["sub"]


def _payload(data: bytes) -> bytes:
    magic, load, size, entry = struct.unpack_from("<4sIII", data, 0)
    assert magic == b"YAP1"
    assert load == 0 and entry == 0
    assert size == len(data) - 16
    return data[16:]


def _words(payload: bytes) -> list[int]:
    return [int.from_bytes(payload[i : i + 4], "little") for i in range(0, len(payload), 4)]


class TestCompilerRustM2(unittest.TestCase):
    def test_COMPILER_RUST_007(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "add.yap"
            r = _compile(ADD_YS, dest)
            self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
            words = _words(_payload(dest.read_bytes()))
            functs = [
                unpack_r(w)["funct"]
                for w in words
                if unpack_r(w)["opcode"] == OPCODE_SPECIAL
            ]
            self.assertIn(FUNCT_ADD, functs)
            self.assertIn(FUNCT_SUB, functs)
            src = ADD_YS.read_text(encoding="utf-8")
            self.assertIn("+", src)
            self.assertIn("-", src)

    def test_COMPILER_RUST_009(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "add.yap"
            r = _compile(ADD_YS, dest)
            self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
            payload = _payload(dest.read_bytes())
            words = _words(payload)
            start_jal = unpack_r(words[0x8C // 4])
            self.assertEqual(start_jal["opcode"], OPCODE["jal"])
            main_addr = (start_jal["target26"] << 2) & 0xFFFFFFFF
            self.assertNotEqual(main_addr, 0x84)
            add_addr = None
            for w in words:
                u = unpack_r(w)
                if u["opcode"] != OPCODE["jal"]:
                    continue
                t = (u["target26"] << 2) & 0xFFFFFFFF
                if t != main_addr and t != 0x84:
                    add_addr = t
                    break
            self.assertIsNotNone(add_addr)
            self.assertLess(add_addr, main_addr)
            last = unpack_r(words[main_addr // 4 - 1])
            self.assertEqual(last["opcode"], OPCODE_SPECIAL)
            self.assertEqual(last["funct"], FUNCT_JR)
            self.assertEqual(last["rs"], 3)
            emu = _emu(dest)
            self.assertEqual(emu.returncode, 0, emu.stderr)


if __name__ == "__main__":
    unittest.main()
