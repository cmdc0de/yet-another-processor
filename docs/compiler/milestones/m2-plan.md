# Assembler m2

Features: COMPILER-008, COMPILER-009, COMPILER-010, COMPILER-011

## Intent

Two-pass (or equivalent) assemble: `name:` captures payload `LC`; `j`/`jal`/`beq`/… accept a label; forward refs resolve; `.org imm` sets `LC` and zero-fills gaps. Header `size` still matches payload length including padding. m1 tests still pass.

## Work

- Pass 1: comments, labels, `.org`, instruction sizes (4 bytes each) to build a symbol table.
- Pass 2: `yap_isa.assemble(..., pc=LC)` with label targets turned into absolute addresses (same as m1 immediates).
- `.org imm`: `imm >= load` (v1 `load=0`); `.org` backward is an error (`docs/compiler/design.md`).
- Duplicate labels are an error with `file:line:`.
- Undefined label is an error.

## Done

- COMPILER-008: `loop:` at a `nop` has value equal to that instruction’s address
- COMPILER-009: `j loop` / `beq loop` encode the correct target
- COMPILER-010: a `j` before its `loop:` label still resolves
- COMPILER-011: `.org 0x80` then `halt` puts `halt` at payload offset `0x80`; bytes `0x00–0x7F` are zero if nothing else was emitted

## Out of scope

`.byte`/`.word`, `.align`, `.equ`, `li`/`move`/`la`, `--run`, ELF.
