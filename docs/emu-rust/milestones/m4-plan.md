# emu-rust m4

Features: EMU-RUST-012, EMU-RUST-020, EMU-RUST-021, EMU-RUST-022

## Intent

Fetch stays 32-bit at `PC` with `PC+4` when sequential. Load/store byte/half/word (signed and unsigned loads) are little-endian. `j`/`jal`/`jr`/`jalr` and flag branches (no delay slot) match `docs/isa/design.md`. Unaligned fetch or memory access sets CAUSE=8 and `PC=0x80`. After this, a YAP1 with ALU + `lw`/`sw` + `jal`/`jr` + `beq` + `halt` can run on the Rust emulator.

## Work

- Fetch: aligned word at `PC`; if `PC % 4 != 0`, CAUSE=8, `PC=0x80`.
- Loads/stores: `lb`/`lbu`/`lh`/`lhu`/`lw`/`sb`/`sh`/`sw`; address = `rs + sext(imm16)`; unaligned → CAUSE=8.
- `j`: `PC <- (PC+4)[31:28] || target26 || 00`. `jal`: `r3 <- PC+4` then that jump. `jr`: `PC <- rs`. `jalr`: `rd <- PC+4`, `PC <- rs`.
- `bcc`: if cond taken, `PC <- PC+4 + (sext(imm22)<<2)`; else `PC+4`. Conds: eq ne lt ge lo hs le gt mi pl.
- m1–m3 tests still pass.

## Done

- EMU-RUST-012: sequential `PC+4`; unaligned fetch → CAUSE=8, `PC=0x80`
- EMU-RUST-020: word/half/byte load/store as ISA m3; unaligned `lw` at 1 → CAUSE=8
- EMU-RUST-021: `j`/`jal`/`jr`/`jalr` as ISA-027–029
- EMU-RUST-022: `beq` taken/not-taken and at least `bne`/`blo` as ISA-030

## Out of scope

Dump (005), other hosts (007–010), user/supervisor CSRs, `sys`/`eret`/IRQ, COP1. Align trap is not the full 026 entry sequence.
