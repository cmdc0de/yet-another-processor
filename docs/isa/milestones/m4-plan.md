# ISA m4

Features: ISA-030, ISA-032

## Intent

Add B-type `bcc` (all `design.md` cond codes) and SPECIAL `halt`. No delay slot: a taken branch replaces `PC+4`. HALT sets `cpu.halted`; it does not change GPRs or FLAGS.

## Work

- B-type pack/unpack: `opcode=000100`, `cond` in bits 25–22, signed `imm22` word offset: `PC+4 + (sext(imm22)<<2)`.
- Cond codes: EQ NE LT GE LO HS LE GT MI PL per `docs/isa/design.md`.
- Assembler mnemonics: `beq`, `bne`, `blt`, `bge`, `blo`, `bhs`, `ble`, `bgt`, `bmi`, `bpl` with a PC-absolute target (same style as `j`).
- `halt`: SPECIAL funct `101100`; sets `halted`. Further `step` is a no-op.
- Tests in `m4-testplan.md`. m1–m3 tests still pass.

## Done

- ISA-030: each listed cond takes or falls through correctly after CMP/TEST; encoding opcode=Bcc
- ISA-032: `halt` encoding; after `halt`, `halted` is true; GPRs unchanged

## Out of scope

Privilege (ISA-033–040), reserved VM (041–042), coprocessor (043–045), SYS/ABI (046–049), ISA-051.
