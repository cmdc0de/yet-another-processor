# Assembler m3

Features: COMPILER-012, COMPILER-013, COMPILER-014

## Intent

Emit LE data and named constants. `.equ` names work as immediates (and in `.byte`/`.word`). `.align n` pads zeros until `LC % 2^n == 0`. Unaligned `.half`/`.word` is an error unless aligned first. m1–m2 tests still pass.

## Work

- Pass 1: account for data sizes when advancing `LC` (and `.align` padding).
- Pass 2: emit bytes; `.equ` substitutes before `yap_isa.assemble` / data emit.
- `.word` requires `LC % 4 == 0`; `.half` requires `LC % 2 == 0`.
- `.equ` is not a label; duplicate `.equ` or clash with a label is an error.
- Multiple immediates per `.byte`/`.half`/`.word` line, comma or space separated.

## Done

- COMPILER-012: `.word 0x12345678` is LE `78 56 34 12`; `.byte 1,2`; `.half 0x80FF` is `FF 80`
- COMPILER-013: `.byte 1` then `.align 2` then `.word 0` — word at a 4-byte boundary, zeros in the gap
- COMPILER-014: `.equ N, 4` then `lw t0, N(sp)` encodes `imm=4`

## Out of scope

`li`/`move`/`la`, `--run`, ELF, multi-file.
