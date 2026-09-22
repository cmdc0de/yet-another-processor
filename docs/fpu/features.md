# FPU coprocessor features

Prefix: `FPU`

FP ops off the MOSFET datapath. ISA already has COP1 space, `mfc1`/`mtc1`, and trap-on-other (`ISA-043`–`045`). This sequence implements arithmetic the ISA can target. Not MOSFET FPU. Not GPU. Not VM.

Implementation: `fpu/`. Tests under `compiler/tests/`. v1 is **simulation** on Linux. Named FPGA/IC and IEEE extras are later-generation. Float format and COP1 encodings are `design.md` after this catalog.

## Tree and sim

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| FPU-001 | Sources under `fpu/` | open | |
| FPU-002 | Simulation builds and runs on Linux (dev host) | open | |
| FPU-003 | Tests fail if the chosen simulator is missing | open | |

## Format and file

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| FPU-004 | Documented float format (`design.md`) | open | |
| FPU-005 | Arithmetic uses the existing 32 COP1 registers `f0`–`f31` | open | |

## Arithmetic

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| FPU-006 | Add two floats, write `fd` | open | |
| FPU-007 | Subtract two floats, write `fd` | open | |
| FPU-008 | Multiply two floats, write `fd` | open | |
| FPU-009 | Divide two floats, write `fd` (div-by-zero defined in `design.md`) | open | |

## Software

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| FPU-010 | Assembler encodes the documented COP1 arithmetic ops | open | |
| FPU-011 | Kernel trap path saves and restores `f0`–`f31` | open | |

## Later generation (do not pull into m1)

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| FPU-012 | Named FPGA or IC on a board | open | later-generation |
| FPU-013 | Double-precision ops | open | later-generation |
| FPU-014 | IEEE round modes / exception flags | open | later-generation |
| FPU-015 | Compare-and-branch on FP condition | open | later-generation |
