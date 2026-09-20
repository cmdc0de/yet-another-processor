# fpga-cpu m3

Features: FPGA-CPU-010, FPGA-CPU-011, FPGA-CPU-013

## Intent

Finish the Icarus CPU’s integer execute path against `compiler.yap_cpu`: load/store (LE, window/align), `j`/`jal`/`jr`/`jalr`/`bcc` with no delay slot, and the CSR/privilege/trap/IRQ contract. After halt, dumped PC/GPRs/FLAGS/CSRs (and SRAM where a store is in the image) match `yap_cpu` on the same YAP1. m1–m2 tests still pass.

## Work

- Memory: `mem_we`, size 1/2/4, byte/half extract and `load_sext` on the CPU. Testbench SRAM honors `we`/`size`. DISPATCH maps `lw`/`lh`/`lb`/`lbu`/`lhu`/`sw`/`sh`/`sb` to the same `uPC` bases as `ucode.py`.
- Before `re`/`we`: misaligned → TRAP 8; user and not in `[UBASE, ULIMIT)` → TRAP 2; no SRAM write. Fetch window when `P=0`.
- Sequencer: `SEQ_ERET`, `SEQ_SKIP_IF` (bcc). DISPATCH maps `j`/`jal`/`jr`/`jalr`/`bcc`, `sys`, `mfc0`/`mtc0`, `eret`. `a_sel` J-target and `b_sel` branch offset.
- CSR file: STATUS, FLAGS, EPC, CAUSE, UBASE, ULIMIT. `sys` → CAUSE=3, `EPC=PC+4`. Other traps `EPC=PC`. User CSR write / supervisor-only / user `eret` → CAUSE=7. TE=1 → CAUSE=7, TE stays 0. `irq` pin while `IE=1` on fetch → CAUSE=1.
- Window and user-`eret` images may set initial `P`/`UBASE`/`ULIMIT`/`entry` (plusargs), as cpu m3/m4 poked `cpu.p`. IRQ tests raise the sim `irq` input (plusarg or API), as `cpu.irq()`.
- Tests in `compiler/tests/test_fpga_cpu_m3.py`. Compare sim dump to a `yap_cpu` run.

## Done

- FPGA-CPU-010: same images as cpu m3 CPU-014, 015, 026, 027 (`sw`/`lw`, `sb`/`lbu`, offset `4(t1)`; SRAM `78 56 34 12` after `sw` of `0x12345678` at 0; user `lw` at 0 with window `[0x1000,0x8000)` → CAUSE=2; `lw`/`sw` at 1 → CAUSE=8)
- FPGA-CPU-011: same images as cpu m5 CPU-039–043 (`j`/`jal`/`jr`/`jalr` to `0x20`; `beq` taken and not taken; `blo` taken, `bhs` not taken)
- FPGA-CPU-013: same images as cpu m4 CPU-016, 020, 024, 025, 028, 029, 030 (`mfc0`/`mtc0` UBASE; `mfc0` CAUSE after align trap; `sys` EPC=`PC+4`; supervisor `eret` to halt at `0x80`; user `eret` → CAUSE=7; TE=1 → CAUSE=7; `IE=1` + irq → CAUSE=1)

## Out of scope

FPGA-CPU-014–016 (COP1, ISA-test parity, `os/kernel.s`), later-generation 017–020.
