# fpu m2

Features: FPU-006, FPU-007, FPU-008, FPU-009

## Intent

COP1 arithmetic as in `docs/fpu/design.md`: `add.s` / `sub.s` / `mul.s` / `div.s` (`rs=16`) write IEEE-754 binary32 into `fd`. Div-by-zero is signed inf; 0/0 is qNaN `0x7FC00000`. Testbench pokes `f[]` and an execute port, dumps `fd`. m1 reset-zero tests still pass. Verilog-2001 + Icarus.

## Work

- `fpu/rtl/`: execute port (`fd`, `fs`, `ft`, `funct` or equivalent) writing `f[fd]`.
- `fpu/sim/tb_m2.v`: load known words, issue the four ops, `$display` results.
- unittest `compiler/tests/test_fpu_m2.py`; m1 still green.

## Done

- FPU-006: `1.0 + 2.0` writes `3.0` to `fd`
- FPU-007: `1.0 − 0.5` writes `0.5` to `fd`
- FPU-008: `2.0 × 3.0` writes `6.0` to `fd`
- FPU-009: `1.0 ÷ 2.0` writes `0.5`; `1.0 ÷ 0.0` writes `+inf`; `0.0 ÷ 0.0` writes qNaN `0x7FC00000`

## Out of scope

FPU-010–011 (assembler, OS save/restore). Later-generation 012–015. No `yap_cpu` microcode hook. No GPU FPGA.
