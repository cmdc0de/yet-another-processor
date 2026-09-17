# ISA m3

Features: ISA-017, ISA-018, ISA-019, ISA-020, ISA-021, ISA-022, ISA-023, ISA-024, ISA-027, ISA-028, ISA-029

Also implement: `jalr` (design.md; link + register jump).

## Intent

Finish `DIV`, add little-endian load/store, and add unconditional control transfer (`j`, `jal`, `jr`, `jalr`). No delay slot: the jump replaces the usual `PC+4`. Alignment faults record CAUSE=8 without the rest of the trap ISA.

## Work

- SPECIAL `div`; I-type load/store; J-type `j`/`jal`; SPECIAL `jr`/`jalr`.
- Byte-addressable LE memory. Address = `rs + sext(imm16)`.
- `DIV`: unsigned 32-bit `rd = rs / rt`; `rt==0` → `rd=0`, Z=1. Flags Z N, C=V=0.
- Halfword aligned to 2, word to 4, else CAUSE=8. Loads/stores do not change FLAGS.
- `j`: `PC <- (PC+4)[31:28] || target26 || 00`
- `jal`: `r3 <- PC+4`, then same jump as `j`
- `jr`: `PC <- rs`
- `jalr rd, rs`: `rd <- PC+4`, `PC <- rs` (usual `jalr ra, rs`)
- Jumping does **not** also add 4. Link value is the sequential next instruction (`PC+4` of the jump).
- Tests in `m3-testplan.md`. m1 and m2 tests still pass.

## Done

- ISA-017: `div` including divide-by-zero
- ISA-018–023: `lw`/`sw`/`lb`/`lbu`/`sb`/`lh`/`lhu`/`sh`
- ISA-024: LE round-trip; unaligned `lw` → CAUSE=8
- ISA-027: `j` sets PC to the encoded target
- ISA-028: `jal` writes `ra` (`r3`) with `PC+4` and jumps
- ISA-029: `jr rs` sets PC from a register; `jalr` links and jumps

## Out of scope

Bcc (ISA-030), HALT (ISA-032), privilege, SYS, coprocessor, ABI stack, ISA-051.
