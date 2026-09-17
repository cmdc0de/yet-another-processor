# ISA m5

Features: ISA-033, ISA-034, ISA-035, ISA-036, ISA-037, ISA-038, ISA-039, ISA-040, ISA-041, ISA-042, ISA-049

## Intent

Make the v1 kernel contract real in `compiler/yap_isa`: STATUS (P, IE, TE, PP, PIE), CSRs, trap entry at `0x80`, `ERET`, one user `[UBASE, ULIMIT)`, `sys`, and reserved VM cause codes. Reset is supervisor, `IE=0`, `TE=0`, `PC=0`. Setting TE traps (CAUSE=7); TE stays 0.

## Work

- CSRs: STATUS, FLAGS, EPC, CAUSE, UBASE, ULIMIT. `mfc0` / `mtc0` per `docs/isa/design.md`.
- User may **read** FLAGS and STATUS. User **write** and other CSR access: CAUSE=7, trap.
- Trap: `CAUSE`, `PIE/PP <- IE/P`, `P=1`, `IE=0`, `PC=0x80`. `EPC` = faulting PC, except **SYS: EPC=PC+4**.
- `eret`: supervisor-only; restore IE/P from PIE/PP, `PC <- EPC`.
- User fetch/load/store: `UBASE <= addr < ULIMIT` and aligned, else CAUSE=2. Supervisor: no window check. Alignment still CAUSE=8, now via the same trap path.
- `sys imm16`: trap CAUSE=3; number = imm16.
- External IRQ: `cpu.irq()`; if `IE=1`, trap CAUSE=1.
- CAUSE 4 and 5 named (translation miss / page fault); no walker.
- Tests in `m5-testplan.md`. m1–m4 tests still pass.

## Done

- ISA-033: STATUS.P user vs supervisor; reset is supervisor
- ISA-034: user `mtc0` / `eret` traps; supervisor succeeds
- ISA-035: trap saves EPC/CAUSE/PP/PIE and vectors to `0x80`
- ISA-036: `eret` resumes
- ISA-037: user access outside `[UBASE, ULIMIT)` faults; supervisor does not
- ISA-038: that fault is CAUSE=2
- ISA-039: `IE` gates `cpu.irq()`
- ISA-040: IRQ trap is CAUSE=1
- ISA-041: CAUSE 4 and 5 are defined
- ISA-042: setting TE traps CAUSE=7; TE stays 0
- ISA-049: `sys` encoding, CAUSE=3, EPC=PC+4, imm16 is the number

## Out of scope

COP1 (ISA-043–045), stack/calling-convention rows (046–048) except names already in m1, ISA-051.
