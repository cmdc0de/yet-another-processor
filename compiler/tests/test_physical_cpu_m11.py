"""Physical CPU m11 tests. Run from repo root: python3 -m unittest compiler.tests.test_physical_cpu_m11

Parses KiCad 6 .kicad_pcb as text. Does not need kicad-cli or a GUI.
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LATCH_DIR = ROOT / "hw" / "latch"


class TestPhysicalCpuM11(unittest.TestCase):
    def test_PHYSICAL_CPU_016(self):
        pcbs = list(LATCH_DIR.glob("*.kicad_pcb"))
        self.assertTrue(pcbs, "hw/latch/ should contain a .kicad_pcb")
        blob = pcbs[0].read_text(encoding="utf-8")
        for token in (
            "IRLML6246",
            "IRLML6401",
            "MICRO3_SOT23_INF",
            "D",
            "EN",
            "Q",
            "VDD",
            "VSS",
        ):
            self.assertIn(token, blob, token)


if __name__ == "__main__":
    unittest.main()
