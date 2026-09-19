# fpga-cpu m1

Features: FPGA-CPU-001, FPGA-CPU-002, FPGA-CPU-003, FPGA-CPU-004, FPGA-CPU-005, FPGA-CPU-006, FPGA-CPU-012

## Intent

Stand up `emu/fpga-cpu/`: Verilog-2001 + Icarus. Python writes `ucode.hex` from `yap_cpu`, loads one YAP1 into simulated SRAM (no header), runs until `halt` or a cycle cap. A `halt` image exits 0. A never-halt image with a small cap exits non-zero. One clock = one control word for fetch + halt.

## Work

- `emu/fpga-cpu/rtl/` CPU stub: PC, IR, `uPC`, 256×64 ROM (`$readmemh` `ucode.hex`), mem port, sequencer ops NEXT/DISPATCH/HALT/TRAP enough to fetch and halt.
- `emu/fpga-cpu/sim/` testbench + `sim.py` per `docs/fpga-cpu/design.md`.
- Generate `ucode.hex` from `compiler.yap_cpu.ucode.build_rom()` in the sim setup path.
- Tests in `compiler/tests/test_fpga_cpu_m1.py` (or under `emu/fpga-cpu/`). Need `iverilog`/`vvp` on `PATH`.
- Halt fixture: assemble `halt`. Non-halt: `nop` loop or `add` without halt, `--max-cycles` small.

## Done

- FPGA-CPU-001: `.v` files exist under `emu/fpga-cpu/`
- FPGA-CPU-002: YAP1 payload at `load`; dump/`$display` shows insn at `entry`, not the `YAP1` magic bytes
- FPGA-CPU-003: `halt` image → `sim.py` exit 0; never-halt + small cap → exit ≠ 0
- FPGA-CPU-004: `python3 -m unittest …` on this Linux host with Icarus
- FPGA-CPU-005: `halt` at 0 takes more than one clock (fetch + halt)
- FPGA-CPU-006: `ucode.hex` has 256 lines of 16 hex digits; first word is the fetch control word from `yap_cpu`
- FPGA-CPU-012: after halt, further clocks leave `PC` unchanged and stay halted

## Out of scope

FPGA-CPU-007–011, 013–016, later-generation 017–020.
