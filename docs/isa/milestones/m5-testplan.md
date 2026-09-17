# ISA m5 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| ISA-033 | Reset: P=1, IE=0, PC=0. Clearing P via `mtc0` puts the model in user. |
| ISA-034 | User `mtc0` to UBASE → trap CAUSE=7. Supervisor `mtc0` UBASE succeeds. User `eret` → CAUSE=7. |
| ISA-035 | `sys 1` from PC=0: CAUSE=3, EPC=4, P=1, IE=0, PC=0x80, PP/PIE saved. |
| ISA-036 | After that `sys`, `eret` → PC=4, P restored to previous. |
| ISA-037 | UBASE=0x100, ULIMIT=0x200, user `lw` at 0 → fault. Same `lw` in supervisor succeeds. |
| ISA-038 | That user fault is CAUSE=2, PC=0x80. |
| ISA-039 | IE=0, `cpu.irq()` does not trap. IE=1, `cpu.irq()` traps. |
| ISA-040 | That trap is CAUSE=1. |
| ISA-041 | Named constants CAUSE translation-miss=4 and page-fault=5; distinct from 2 and 3. |
| ISA-042 | Supervisor `mtc0` STATUS with TE=1 → trap CAUSE=7; TE stays 0. |
| ISA-049 | `sys 0x12` opcode=SYS, imm16=0x12, CAUSE=3, a0–a3 untouched by the trap itself. |
