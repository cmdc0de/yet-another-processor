# fpu m3

Features: FPU-010, FPU-011

## Intent

Assembler accepts `add.s` / `sub.s` / `mul.s` / `div.s` as in `docs/fpu/design.md` (`opcode=COP1`, `rs=16`). Kernel trap path saves `f0`–`f31` after the integer frame and restores them before `ERET`, so a returning syscall does not lose user FP state. m1–m2 FPU tests still pass. Existing OS m3 COP1-unimp panic fixture stays a non-arithmetic encoding.

## Work

- `compiler/`: encode `add.s` / `sub.s` / `mul.s` / `div.s`.
- `os/kernel.s`: on trap, `mfc1`/`mtc1` save/restore 32 FP words (`f0` at lowest address). Handler may use an FP reg as scratch so restore is observable.
- unittest `compiler/tests/test_fpu_m3.py`; FPU m1–m2 still green.

## Done

- FPU-010: `add.s f1, f2, f3` packs COP1, `rs=16`, `fd=1`, `fs=2`, `ft=3`, `funct=0` (and the other three mnemonics)
- FPU-011: user `mtc1` into `f0`, returning `SYS_WRITE`, `mfc1 f0`, `SYS_EXIT`. After halt, that GPR is `0xA5A5A5A5`. Kernel trap dirties `f0` before restore. `yap-emu` exits 0.

## Out of scope

Later-generation 012–015. No `yap_emu` / `yap_cpu` execute of `add.s` (encodings only). No GPU FPGA.
