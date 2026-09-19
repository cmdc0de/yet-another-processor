# fpga-cpu m2

Features: FPGA-CPU-007, FPGA-CPU-008, FPGA-CPU-009

## Intent

Execute integer microcode on the Icarus CPU the same way `compiler.yap_cpu` does: two read ports, bank latencies, ALU/shifter/mul/div/I-type/ADR. After halt, dumped PC/FLAGS/GPRs match `yap_cpu` on the same YAP1. m1 tests still pass (`nop` without halt still hits the cycle cap).

## Work

- Verilog RF: wired `r0`–`r2`, MOSFET `r3`–`r15` (`LAT=1`), IC `r16`–`r31` (`LAT=2`); stall like `yap_cpu`.
- Combinational ALU for the `alu_op` / `flag_mode` map in `docs/cpu/design.md`. Sequencer already has NEXT/DISPATCH/HALT; DISPATCH must map SPECIAL integer ops and I-type `addi`/`andi`/`ori`/`xori`/`lui`/`adr` to the same `uPC` bases as `ucode.py`.
- Dump real GPRs/FLAGS from the HDL (not hardcoded zeros).
- Tests in `compiler/tests/test_fpga_cpu_m2.py`. Compare sim dump to a `yap_cpu` run.

## Done

- FPGA-CPU-007: `add t0, t0, one; halt` uses fewer cycles than `add s0, s0, one; halt`
- FPGA-CPU-008: `add t0, one, one; halt` — sim `pc`, FLAGS, `r10` match `yap_cpu`
- FPGA-CPU-009: `and`/`xor`, `sll`, `addi`/`andi`/`lui`, `mul`/`div` (÷0 → 0, Z=1), `adr t0, 4` → `t0==8`; flags as ISA

## Out of scope

FPGA-CPU-010–011, 013–016, later-generation 017–020.
