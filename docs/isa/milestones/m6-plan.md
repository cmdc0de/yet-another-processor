# ISA m6

Features: ISA-043, ISA-044, ISA-045, ISA-046, ISA-047, ISA-048

## Intent

Finish the v1 ISA contract: COP1 opcode space with `mfc1`/`mtc1` and trap on other COP1 ops (CAUSE=6), plus ABI checks for `sp`, stack growth/alignment, and the caller/callee register map from `design.md`. No FP arithmetic.

## Work

- COP1 opcode `010001`. `mfc1 rd, fs` / `mtc1 rt, fs` move 32-bit values to/from a coprocessor register file (`f0`–`f31`). Other COP1 functs trap CAUSE=6 (same trap path as m5).
- Assembler: `mfc1 t0, f0`, `mtc1 t0, f0`.
- ABI: `sp` is `r4`; stack grows down; 8-byte aligned at call boundaries. A small helper can `push`/`pop` words and check `sp % 8 == 0` after a simulated call.
- Register map tests: `ra,sp,a0–a3,a4,t*,s*,fp,k0` match `docs/isa/design.md`. `r0`–`r2` are not writable ABI slots.
- Tests in `m6-testplan.md`. m1–m5 tests still pass.

## Done

- ISA-043: COP1 opcode is distinct from integer SPECIAL/COP0
- ISA-044: `mfc1`/`mtc1` round-trip a GPR through an FP register
- ISA-045: a non-move COP1 encoding traps CAUSE=6, PC=0x80
- ISA-046: `sp` is `r4`, not `r0`–`r2`
- ISA-047: stack grows down; `sp` stays 8-byte aligned at a call boundary
- ISA-048: argument / return / callee-saved / caller-saved names match `design.md`

## Out of scope

IEEE-754 ops, FPU hardware, ISA-051. Syscall ABI already `done` in m5.
