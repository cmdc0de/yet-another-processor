# emu-rust m3

Features: EMU-RUST-016, EMU-RUST-017, EMU-RUST-018, EMU-RUST-019

## Intent

Step the remaining integer ops that do not need SRAM load/store or traps: variable/right shifts, immediates, LUI/ADR, MUL/DIV. Behavior matches `docs/isa/design.md` and `yap_isa.Cpu`. m1–m2 tests still pass.

## Work

- SPECIAL: SRL, SRA, SLLV, SRLV, SRAV (shamt or `rt & 31`; flags as ISA: C = last bit shifted out, V=0).
- I-type: ADDI sign-extends imm16; ANDI/ORI/XORI zero-extend.
- LUI: `rd <- imm16 << 16`, FLAGS unchanged. ADR: `rd <- PC+4+sext(imm16)`, FLAGS unchanged.
- MUL: low 32 bits, Z/N, C=V=0. DIV: unsigned `rs // rt`; divisor 0 → result 0, Z=1.
- Unknown opcodes still `PC+4`.

## Done

- EMU-RUST-016: SRL/SRA and SLLV/SRLV/SRAV match ISA m2 checks
- EMU-RUST-017: ADDI/ANDI/ORI/XORI match ISA-015
- EMU-RUST-018: LUI then ORI forms `0x12345678`; ADR at PC=0 with imm 16 → 20
- EMU-RUST-019: MUL low-32 as ISA-016; DIV by 0 → 0

## Out of scope

Dump (005), other hosts (007–010), unaligned traps (012/020), jumps/branches, privilege, COP1.
