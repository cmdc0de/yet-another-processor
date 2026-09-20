"""GPU m1 tests. Run from repo root: python3 -m unittest compiler.tests.test_gpu_m1

Needs Icarus Verilog (`iverilog`, `vvp` on PATH).
"""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GPU = ROOT / "gpu"
RTL = GPU / "rtl" / "gpu.v"
TB = GPU / "sim" / "tb.v"
W = 160
H = 120


def _require_icarus():
    iverilog = shutil.which("iverilog")
    vvp = shutil.which("vvp")
    if not iverilog or not vvp:
        raise AssertionError(
            "iverilog/vvp not on PATH; install Icarus Verilog. Missing binary is a failure."
        )
    return iverilog, vvp


def _run_sim(ppm: Path) -> None:
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
            [vvp, str(simv), f"+PPM={ppm}"],
            cwd=ROOT,
            capture_output=True,
        )
        if r.returncode != 0:
            err = (r.stderr or b"").decode("utf-8", errors="replace")
            out = (r.stdout or b"").decode("utf-8", errors="replace")
            raise RuntimeError(err or out or "vvp failed")


def _parse_ppm(path: Path) -> bytes:
    data = path.read_bytes()
    if not data.startswith(b"P6"):
        raise AssertionError(f"not P6: {data[:16]!r}")
    # P6\n160 120\n255\n<body>
    parts = data.split(b"\n", 3)
    if len(parts) < 4:
        raise AssertionError("short PPM header")
    wh = parts[1].split()
    return parts[3] if len(wh) == 2 else data


class TestGpuM1(unittest.TestCase):
    def test_GPU_001(self):
        vers = list(GPU.glob("**/*.v"))
        self.assertTrue(vers, "gpu/ should contain Verilog-2001 .v files")

    def test_GPU_003(self):
        self.assertTrue(shutil.which("iverilog"), "iverilog not on PATH")
        self.assertTrue(shutil.which("vvp"), "vvp not on PATH")

    def test_GPU_002(self):
        with tempfile.TemporaryDirectory() as tmp:
            ppm = Path(tmp) / "fb.ppm"
            _run_sim(ppm)
            self.assertTrue(ppm.is_file() and ppm.stat().st_size > 0)

    def test_GPU_004(self):
        rtl = RTL.read_text(encoding="utf-8")
        self.assertRegex(rtl, r"\bfb\s*\[")
        self.assertNotRegex(rtl, r"\byap_bus\b")

    def test_GPU_005(self):
        rtl = RTL.read_text(encoding="utf-8")
        self.assertIn("160", rtl)
        self.assertIn("120", rtl)
        self.assertIn("0x00RRGGBB", rtl)
        tb = TB.read_text(encoding="utf-8")
        self.assertIn("P6", tb)
        self.assertIn("160 120", tb)

    def test_GPU_006(self):
        with tempfile.TemporaryDirectory() as tmp:
            ppm = Path(tmp) / "fb.ppm"
            _run_sim(ppm)
            raw = ppm.read_bytes()
            self.assertTrue(raw.startswith(b"P6"), raw[:16])
            self.assertIn(b"160 120", raw)
            body = raw.split(b"\n", 3)[-1]
            self.assertEqual(len(body), W * H * 3, len(body))
            self.assertEqual(body, b"\x00" * (W * H * 3))


if __name__ == "__main__":
    unittest.main()
