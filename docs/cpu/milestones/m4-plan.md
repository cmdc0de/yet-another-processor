# cpu m4

Features: CPU-016, CPU-017, CPU-020, CPU-024, CPU-025, CPU-028, CPU-029, CPU-030, CPU-031

## Intent

Finish the clocked model’s kernel contract. `mfc0`/`mtc0` talk to the CSR file. `sys` sets `EPC=PC+4`. `eret` restores privilege and `PC`. User CSR writes and supervisor-only ops trap. TE stays 0. COP1 moves work; other COP1 traps. `irq()` while `IE=1` is CAUSE=1. m1–m3 tests still pass.

## Work

- Microcode for `mfc0`/`mtc0` (`re_csr`/`we_csr`, `csr_idx` from `IR.rt`), `mfc1`/`mtc1` (32 `f` regs), `sys` (`seq=TRAP` cause 3), `eret` (`seq=ERET`).
- User may read STATUS and FLAGS; any user `mtc0`, user `mfc0` of other CSRs, user `eret` → CAUSE=7.
- `mtc0 status` with TE=1 → CAUSE=7; TE remains 0.
- Fetch `irq_chk`: if `IE=1` and `cpu.irq()` pending → CAUSE=1, `EPC=PC`.
- Unknown COP1 (`rs` not MFC1/MTC1) → CAUSE=6.
- Control word already steers RF/ALU/shifter/PC/FLAGS/memory; this slice adds CSR fields (CPU-020).
- Tests in `compiler/tests/test_cpu_m4.py`. Halt at `0x80` for trap-to-halt images.

## Done

- CPU-016: supervisor `mtc0`/`mfc0` UBASE; after `mfc0 t0, ubase`, `t0` matches
- CPU-017: `mtc1 t0, f0` then `mfc1 t1, f0` → `t1==t0`
- CPU-020: `mfc0` after an align trap returns CAUSE=8 (CSR steered, not a GPR)
- CPU-024: `sys 1` → CAUSE=3, `EPC==PC+4` of the `sys` (4 if `sys` at 0)
- CPU-025: `mtc0` EPC=`0x80` (halt there), `mtc0` status so `ERET` stays supervisor, `eret` → halt at `0x80`
- CPU-028: `p=0`, `eret` → CAUSE=7
- CPU-029: `mtc0` STATUS with TE=1 → CAUSE=7; `te==0`
- CPU-030: `IE=1`, `cpu.irq()`, fetch → CAUSE=1
- CPU-031: COP1 word that is not MFC1/MTC1 → CAUSE=6

## Out of scope

Jumps/branches (not in catalog), later-generation CPU-033–038.
