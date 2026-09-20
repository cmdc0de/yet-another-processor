"""GPU m2 tests. Run from repo root: python3 -m unittest compiler.tests.test_gpu_m2

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
TB = GPU / "sim" / "tb_m2.v"
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


def _ppm_body(path: Path) -> bytes:
    raw = path.read_bytes()
    if not raw.startswith(b"P6"):
        raise AssertionError(f"not P6: {raw[:16]!r}")
    body = raw.split(b"\n", 3)[-1]
    if len(body) != W * H * 3:
        raise AssertionError(f"body {len(body)}")
    return body


def _pix(body: bytes, x: int, y: int) -> bytes:
    i = (y * W + x) * 3
    return body[i : i + 3]


class TestGpuM2(unittest.TestCase):
    def test_GPU_007(self):
        rtl = RTL.read_text(encoding="utf-8")
        for off in ("8'h00", "8'h04", "8'h08", "8'h0c", "8'h10", "8'h14"):
            self.assertIn(off, rtl, off)
        self.assertIn("we", rtl)
        self.assertIn("wdata", rtl)

    def test_GPU_008(self):
        with tempfile.TemporaryDirectory() as tmp:
            ppm = Path(tmp) / "fb.ppm"
            _run_sim(ppm)
            body = _ppm_body(ppm)
        red = b"\xff\x00\x00"
        black = b"\x00\x00\x00"
        self.assertEqual(_pix(body, 0, 0), red)
        self.assertEqual(_pix(body, 7, 7), red)
        self.assertEqual(_pix(body, 8, 0), black)
        self.assertEqual(_pix(body, 0, 8), black)


if __name__ == "__main__":
    unittest.main()
