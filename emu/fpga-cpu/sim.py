"""Run a YAP1 on the Icarus FPGA-CPU sim. python3 emu/fpga-cpu/sim.py image.yap"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from compiler.yap1 import Yap1Error, unpack
from compiler.yap_cpu.ucode import build_rom

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RTL = HERE / "rtl" / "cpu.v"
TB = HERE / "sim" / "tb.v"
MEM_WORDS = 16384
DEFAULT_MAX = 100000


def write_ucode_hex(path: Path) -> list:
    rom = build_rom()
    lines = [f"{word:016x}" for word in rom]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rom


def write_sram_hex(path: Path, payload: bytes, load: int) -> None:
    words = [0] * MEM_WORDS
    mem = bytearray(MEM_WORDS * 4)
    end = load + len(payload)
    if load < 0 or end > len(mem):
        raise ValueError("payload does not fit in 64KiB SRAM")
    mem[load:end] = payload
    for i in range(MEM_WORDS):
        words[i] = int.from_bytes(mem[i * 4 : i * 4 + 4], "little")
    path.write_text("".join(f"{w:08x}\n" for w in words), encoding="utf-8")


def run_sim(
    image_path: Path,
    max_cycles: int = DEFAULT_MAX,
    work: Path | None = None,
    *,
    entry: int | None = None,
    p: int = 1,
    ie: int = 0,
    ubase: int = 0,
    ulimit: int = 0x10000,
    irq: int = 0,
) -> subprocess.CompletedProcess:
    data = Path(image_path).read_bytes()
    image = unpack(data)
    tmp_ctx = tempfile.TemporaryDirectory(dir=str(work) if work else None)
    tmp = Path(tmp_ctx.name)
    try:
        ucode = tmp / "ucode.hex"
        sram = tmp / "sram.hex"
        simv = tmp / "simv"
        write_ucode_hex(ucode)
        write_sram_hex(sram, image.payload, image.load)
        compile_cmd = ["iverilog", "-o", str(simv), str(RTL), str(TB)]
        c = subprocess.run(compile_cmd, cwd=ROOT, capture_output=True, text=True)
        if c.returncode != 0:
            raise RuntimeError(c.stderr or c.stdout or "iverilog failed")
        pc = image.entry if entry is None else entry
        run_cmd = [
            "vvp",
            str(simv),
            f"+UCODE={ucode}",
            f"+SRAM={sram}",
            f"+MAXCYCLES={max_cycles}",
            f"+ENTRY={pc:x}",
            f"+P={int(p)}",
            f"+IE={int(ie)}",
            f"+UBASE={ubase:x}",
            f"+ULIMIT={ulimit:x}",
            f"+IRQ={int(irq)}",
        ]
        return subprocess.run(run_cmd, cwd=ROOT, capture_output=True, text=True)
    finally:
        tmp_ctx.cleanup()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Simulate a YAP1 on the FPGA CPU (Icarus)")
    parser.add_argument("image", help="YAP1 path")
    parser.add_argument("--max-cycles", type=int, default=DEFAULT_MAX)
    args = parser.parse_args(argv)
    try:
        r = run_sim(Path(args.image), max_cycles=args.max_cycles)
    except (OSError, Yap1Error, ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    sys.stdout.write(r.stdout)
    if r.stderr:
        sys.stderr.write(r.stderr)
    halted = "halted 1" in r.stdout
    return 0 if halted and r.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
