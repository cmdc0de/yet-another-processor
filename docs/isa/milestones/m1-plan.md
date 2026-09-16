# ISA m1

Features: ISA-001, ISA-002, ISA-003, ISA-004, ISA-005, ISA-006, ISA-007, ISA-008, ISA-009, ISA-010, ISA-011, ISA-014, ISA-031, ISA-050, ISA-052, ISA-053, ISA-054, ISA-055, ISA-056

## Intent

Make the v1 programmer model real as a checkable Python module the assembler will import: 32-bit words, 32 GPR names, wired `zero`/`one`/`ones`, PC, FLAGS, R-type ADD/SUB/AND/OR/XOR/NOT/SLL, NOP, and flags-only CMP, TEST, and TEQ. Encodings match `docs/isa/design.md`.

## Work

- `compiler/` module: GPR names (ABI names from design), instruction pack/unpack for SPECIAL ops in this slice, FLAGS bits, 32-bit PC step of +4.
- Behavioral step for those ops only (wired regs, flags, CMP/TEST/TEQ without a GPR write).
- Tests for each feature ID in `m1-testplan.md`.

## Done

- ISA-001: words and addresses are 32-bit in the model
- ISA-002: `r0`–`r31` exist as one file
- ISA-003: PC is readable; sequential op does `PC+4`
- ISA-004: ADD/SUB/CMP set Z N C V per design.md; TEST sets Z N and clears C V; TEQ sets Z and clears N C V
- ISA-005–010: ADD SUB AND OR XOR NOT match encodings and results
- ISA-011: SLL `rd, rs, shamt` matches encoding and result
- ISA-014: CMP sets flags from `rs - rt` and does not write a GPR
- ISA-031: `nop` is `sll zero, zero, 0`
- ISA-050: `zero`/`one`/`ones`/`ra`/`sp`/… resolve to the design.md map
- ISA-052: TEST sets flags from `rs AND rt` and does not write a GPR
- ISA-053: TEQ sets flags from `rs XOR rt` and does not write a GPR
- ISA-054: read `r0` is 0; write `r0` discarded; ADD into `r0` still sets flags
- ISA-055: `r1` reads 1; writes discarded
- ISA-056: `r2` reads `0xFFFFFFFF`; writes discarded

## Out of scope

SRL/SRA, immediates, MUL/DIV, load/store, jumps/branches, HALT, privilege, syscalls, coprocessor, ISA-051.
