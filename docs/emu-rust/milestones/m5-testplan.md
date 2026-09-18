# emu-rust m5 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| EMU-RUST-005 | Assemble `halt`, run the CLI; stdout contains `pc`, `flags`, `cause` (or CSR names), and `t0`/`r10` (or r0–r31). |
| EMU-RUST-024 | Reset: P=1, IE=0, PC=0. `mtc0` STATUS with P=0 → user. |
| EMU-RUST-025 | User `mtc0` UBASE → CAUSE=7. Supervisor `mtc0` UBASE succeeds. User `mfc0` FLAGS does not trap. |
| EMU-RUST-026 | `sys 1` at PC=0: CAUSE=3, EPC=4, P=1, IE=0, PC=0x80. |
| EMU-RUST-027 | After that `sys`, `eret` → PC=4, P restored. |
| EMU-RUST-028 | UBASE=0x100, ULIMIT=0x200, user `lw` at 0 → fault; same `lw` in supervisor succeeds. |
| EMU-RUST-029 | IE=0, `irq()` does not trap. IE=1, `irq()` traps CAUSE=1. |
| EMU-RUST-030 | `sys` → CAUSE=3. |
| EMU-RUST-031 | Supervisor `mtc0` STATUS with TE=1 → CAUSE=7; TE stays 0. |
| EMU-RUST-032 | Constants translation-miss=4 and page-fault=5; a normal `add` does not set them. |
