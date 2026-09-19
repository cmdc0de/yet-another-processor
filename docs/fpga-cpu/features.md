# FPGA CPU emulator features

Prefix: `FPGA-CPU`

Guest is the YAP 32-bit LE machine. Image is YAP1. Implementation: `emu/fpga-cpu/`.

This sequence is HDL that implements `docs/cpu/design.md`, checked against the ISA tests and Rust. Not the Physical CPU. Not the SRAM bus protocol (Memory + bus). MOSFET cells stay parallel in `lt-spice/`.

v1 is **simulation** (a Verilog/SV testbench on Linux). Synthesis to a board is later-generation. Cycle contract is `yap_cpu` (one clock = one control word), not the behavioral `yap_isa.Cpu`.

HDL language and simulator (Icarus, Verilator, …) are `design.md` after this catalog.

## Harness and image

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| FPGA-CPU-001 | HDL sources under `emu/fpga-cpu/` | open | |
| FPGA-CPU-002 | Testbench loads one YAP1: payload at `load`, `PC=entry`; header not in SRAM | open | |
| FPGA-CPU-003 | Simulate until `halt` or a cycle cap; non-zero if it does not halt | open | |
| FPGA-CPU-004 | Simulation builds and runs on Linux (dev host) | open | |

## Cycle contract

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| FPGA-CPU-005 | One clock executes one 64-bit control word (`docs/cpu/design.md`) | open | |
| FPGA-CPU-006 | Microcode ROM: 256 × 64, same field layout as `compiler.yap_cpu` | open | |
| FPGA-CPU-007 | Split RF: wired `r0`–`r2`, MOSFET `r3`–`r15` (`LAT=1`), IC `r16`–`r31` (`LAT=2`) | open | |
| FPGA-CPU-008 | After halt (and after each retired insn in tests), architectural state matches `yap_cpu` | open | |

## Execute

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| FPGA-CPU-009 | Integer ALU, shifts, MUL/DIV, immediates, ADR | open | |
| FPGA-CPU-010 | Load/store word/half/byte, LE; window and align traps | open | |
| FPGA-CPU-011 | `j`/`jal`/`jr`/`jalr`/`bcc`; no delay slot | open | |
| FPGA-CPU-012 | `halt` stops the clocked machine | open | |
| FPGA-CPU-013 | CSRs, `sys`/`eret`, privilege, TE, IRQ | open | |
| FPGA-CPU-014 | COP1 `mfc1`/`mtc1`; other COP1 → CAUSE=6 | open | |

## Parity

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| FPGA-CPU-015 | Existing ISA assembler tests (`compiler.tests.test_m*`) pass on the sim | open | |
| FPGA-CPU-016 | `os/kernel.s` YAP1 reaches halt (exit 0) on the sim, as on `yap-emu` | open | |

## Later generation (do not pull into m1)

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| FPGA-CPU-017 | Synthesize to a named FPGA part | open | later-generation |
| FPGA-CPU-018 | Run the same YAP1 on FPGA board SRAM | open | later-generation |
| FPGA-CPU-019 | Caches / pipelined control | open | later-generation |
| FPGA-CPU-020 | Full VM / TLB | open | later-generation |
