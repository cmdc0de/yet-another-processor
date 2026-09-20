# fpga-cpu m3 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and Icarus Verilog (`iverilog`, `vvp` on `PATH`).

```bash
python3 -m unittest compiler.tests.test_fpga_cpu_m3 compiler.tests.test_fpga_cpu_m2 compiler.tests.test_fpga_cpu_m1 -v
```

Expected: `Ran 13 tests ... OK`. m1–m2 still pass; a `nop`-only image with `--max-cycles 8` still exits non-zero.

## FPGA-CPU-010 — load/store, window, align

```bash
python3 -m unittest compiler.tests.test_fpga_cpu_m3.TestFpgaCpuM3.test_FPGA_CPU_010
```

Same images as cpu m3 CPU-014, 015, 026, 027. Sim GPRs/FLAGS/CAUSE (and SRAM at 0 for the LE store) match `yap_cpu`. User `lw` at 0 with window `[0x1000,0x8000)` → CAUSE=2. `lw`/`sw` at 1 → CAUSE=8.

## FPGA-CPU-011 — jumps and bcc

```bash
python3 -m unittest compiler.tests.test_fpga_cpu_m3.TestFpgaCpuM3.test_FPGA_CPU_011
```

Same images as cpu m5 CPU-039–043. Sim `pc` / link GPR match `yap_cpu` after halt (`j`/`jal`/`jr`/`jalr` to `0x20`; `beq` taken and not taken; `blo` taken, `bhs` not taken).

## FPGA-CPU-013 — CSRs, sys, eret, TE, IRQ

```bash
python3 -m unittest compiler.tests.test_fpga_cpu_m3.TestFpgaCpuM3.test_FPGA_CPU_013
```

Same images as cpu m4 CPU-016, 020, 024, 025, 028, 029, 030 (not COP1). Sim CSRs/GPRs/`pc` match `yap_cpu`.
