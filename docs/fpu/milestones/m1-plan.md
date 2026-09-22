# fpu m1

Features: FPU-001, FPU-002, FPU-003, FPU-004, FPU-005

## Intent

Verilog-2001 + Icarus in `fpu/`: module `yap_fpu` with 32 COP1 registers `f0`–`f31`, IEEE-754 binary32 words. After reset every register is `0`. Missing `iverilog`/`vvp` fails tests.

## Work

- `fpu/rtl/` module `yap_fpu`; `fpu/sim/` testbench dumps `f0`–`f31` after reset.
- unittest `compiler/tests/test_fpu_m1.py`.

## Done

- FPU-001: HDL under `fpu/`
- FPU-002: sim builds and runs on Linux
- FPU-003: missing Icarus fails (not skip)
- FPU-004: sources state IEEE-754 binary32
- FPU-005: 32 registers `f0`–`f31`; after reset each is `0`

## Out of scope

FPU-006–011 (add/sub/mul/div, assembler, OS save/restore). Later-generation 012–015. No `add.s`. No GPU FPGA.
