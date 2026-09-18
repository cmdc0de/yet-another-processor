# emu-rust m6

Features: EMU-RUST-033, EMU-RUST-034

## Intent

32 FPU registers with `mfc1`/`mtc1`, matching `docs/isa/design.md` and `yap_isa.Cpu`. Any other COP1 encoding traps CAUSE=6 and vectors through the m5 trap path. Software float can run; real FP ops wait on the FPU sequence. m1–m5 tests still pass.

## Work

- `f0`–`f31` (32-bit each). `mtc1 rt, fs` copies GPR → FPR; `mfc1 rd, fs` copies FPR → GPR. FPRs are not GPRs.
- COP1 opcode `010001`. `rs` = MFC1 (0) or MTC1 (4) for moves; any other COP1 `rs`/funct → CAUSE=6, PC=0x80.
- m1–m5 tests still pass.

## Done

- EMU-RUST-033: `mtc1 t0, f0` then `mfc1 t1, f0` copies the value; `f0` is not a GPR
- EMU-RUST-034: a COP1 word that is not a move traps CAUSE=6, PC=0x80

## Out of scope

Other hosts (007–010), FP arithmetic, later-generation rows.
