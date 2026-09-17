# emu-rust m2

Features: EMU-RUST-013, EMU-RUST-014, EMU-RUST-015

## Intent

Step SPECIAL integer ALU the way `docs/isa/design.md` and the Python `yap_isa.Cpu` do: 32 GPRs with wired `r0`/`r1`/`r2`, FLAGS Z/N/C/V, and ADD/SUB/AND/OR/XOR/NOT/SLL/CMP/TEST/TEQ/NOP. `halt` from m1 still ends a program.

## Work

- GPR file `r0`–`r31`; reads of `r0`/`r1`/`r2` are 0 / 1 / `0xFFFFFFFF`; writes to those three discarded; an ALU op with `rd=r0` still updates flags.
- FLAGS Z N C V on ADD/SUB/CMP as design; TEST: Z N, C=V=0; TEQ: Z, N=C=V=0; logic/SLL as ISA.
- Decode SPECIAL `funct` for this slice only; unknown opcodes still `PC+4` (m1).
- Tests may use `python3 -m compiler.asm` or `yap_isa.assemble` words. m1 tests still pass.

## Done

- EMU-RUST-013: `r0`/`r1`/`r2` wired as above; `r3`–`r31` writable
- EMU-RUST-014: ADD/SUB/CMP set Z N C V per design.md
- EMU-RUST-015: ADD, SUB, AND, OR, XOR, NOT, SLL, CMP, TEST, TEQ, NOP match encodings and results; `nop` is `sll zero, zero, 0`

## Out of scope

Dump (005), other hosts (007–010), unaligned fetch trap (012), SRL/SRA/variable shifts (016), immediates, LUI/ADR, MUL/DIV, load/store, jumps/branches, privilege, COP1.
