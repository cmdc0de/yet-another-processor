# emu-rust m5

Features: EMU-RUST-005, EMU-RUST-024, EMU-RUST-025, EMU-RUST-026, EMU-RUST-027, EMU-RUST-028, EMU-RUST-029, EMU-RUST-030, EMU-RUST-031, EMU-RUST-032

## Intent

STATUS (P, IE, TE, PP, PIE), CSRs, trap entry at `0x80`, `ERET`, one user `[UBASE, ULIMIT)`, `sys`, reserved VM cause codes, host IRQ inject — matching `docs/isa/design.md` and `yap_isa.Cpu`. After a run, the CLI prints PC, FLAGS, CSRs, and GPRs. Reset: supervisor, `IE=0`, `TE=0`, `PC=0`. Setting TE traps (CAUSE=7); TE stays 0.

## Work

- CSRs: STATUS, FLAGS, EPC, CAUSE, UBASE, ULIMIT. `mfc0`/`mtc0` per design. User may read FLAGS and STATUS; user write and other CSR access → CAUSE=7.
- Trap: CAUSE, PIE/PP ← IE/P, P=1, IE=0, PC=0x80. EPC = faulting PC except SYS uses PC+4. Align (CAUSE=8) uses this same path.
- `eret`: supervisor-only; restore IE/P, PC ← EPC.
- User fetch/load/store: `UBASE <= addr < ULIMIT` else CAUSE=2. Supervisor skips the window. Alignment still CAUSE=8.
- `sys`: CAUSE=3. `cpu.irq()` if IE=1 → CAUSE=1.
- Named CAUSE 4 and 5; v1 does not generate them.
- CLI after halt (and after a non-halt run): print PC, FLAGS, CSRs, r0–r31 (hex).
- m1–m4 tests still pass.

## Done

- EMU-RUST-005: after `halt`, CLI prints PC, FLAGS, CSRs, GPRs
- EMU-RUST-024: reset supervisor, IE=0, TE=0, PC=0; clearing P is user
- EMU-RUST-025: user `mtc0` UBASE → CAUSE=7; supervisor succeeds; user may `mfc0` FLAGS/STATUS
- EMU-RUST-026: `sys` from PC=0 → CAUSE=3, EPC=4, PC=0x80, P=1, IE=0
- EMU-RUST-027: then `eret` → PC=4, P restored
- EMU-RUST-028: user `lw` outside `[UBASE,ULIMIT)` faults; supervisor does not
- EMU-RUST-029: IE=0, `irq()` no trap; IE=1, `irq()` CAUSE=1
- EMU-RUST-030: `sys` → CAUSE=3
- EMU-RUST-031: `mtc0` STATUS with TE=1 → CAUSE=7, TE stays 0
- EMU-RUST-032: CAUSE 4 and 5 are named constants; distinct from 2 and 3

## Out of scope

Other hosts (007–010), COP1 (033–034), later-generation rows.
