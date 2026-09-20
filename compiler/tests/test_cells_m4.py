"""MOSFET cells m4 tests. Run from repo root: python3 -m unittest compiler.tests.test_cells_m4"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LT = ROOT / "lt-spice"
CELLS = (
    "INVERTER",
    "NAND",
    "NOR",
    "AND",
    "OR",
    "XOR",
    "TG",
    "MUX2",
    "LATCH",
    "ADDER",
)


def _parse_asy(path: Path) -> dict:
    out = {"prefix": "", "value": "", "spicemodel": "", "modelfile": ""}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("SYMATTR Prefix "):
            out["prefix"] = line.split(" ", 2)[2].strip()
        elif line.startswith("SYMATTR Value "):
            out["value"] = line.split(" ", 2)[2].strip()
        elif line.startswith("SYMATTR SpiceModel "):
            out["spicemodel"] = line.split(" ", 2)[2].strip()
        elif line.startswith("SYMATTR ModelFile "):
            out["modelfile"] = line.split(" ", 2)[2].strip()
    return out


class TestCellsM4(unittest.TestCase):
    def test_CELL_003_symbols(self):
        asys = list(LT.glob("*.asy"))
        self.assertTrue(asys, "lt-spice/ should contain .asy files")
        parsed = [(p, _parse_asy(p)) for p in asys]
        for name in CELLS:
            hits = [
                (p, a)
                for p, a in parsed
                if a["prefix"] == "X"
                and "yap_cells.lib" in a["modelfile"]
                and (a["value"] == name or a["spicemodel"] == name)
            ]
            self.assertTrue(hits, f"no Prefix X symbol for {name} using yap_cells.lib")


if __name__ == "__main__":
    unittest.main()
