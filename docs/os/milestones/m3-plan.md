# os m3

Features: OS-006, OS-011, OS-012, OS-015, OS-016, OS-017

## Intent

Finish v1 syscalls and fault handling per `docs/os/design.md`. Default user program `SYS_WRITE`s a short string then `SYS_EXIT`. Bad syscall numbers resume the user with `a4=1`. `SYS_WRITE` outside the window fails with errno and does not smash the kernel. Protection and align faults halt (kill). Other CAUSE values write `KPAN` and halt.

## Work

- Init `YLOG` at `0x0800`. `SYS_WRITE` (imm16=2): check `UBASE <= ptr && ptr+len <= ULIMIT`; copy into the log; set `a0`/`a4`; restore GPRs; `ERET`.
- Unknown `sys` number: `a4=1`, `a0` unchanged, restore, `ERET`.
- CAUSE=2 or 8: halt (optional `KPAN`). Other CAUSE: `magic=KPAN`, halt.
- Default `os/kernel.s` user: write then `sys 1`. Extra `os/*.s` (or `.org` variants) for bad syscall, bad write ptr, `lw` at 0, unaligned `lw`, unimplemented COP1.
- m1–m2 tests: default image still exits 0; dump `r4` still `00008000` after EXIT.

## Done

- OS-015: after halt, log magic `YLOG`, `len>0`, data matches the user string
- OS-016: user `sys 99` then `sys 1`; `a4` was nonzero (store `a4` to user SRAM before exit)
- OS-017: `SYS_WRITE` of ptr `0`; `a4=1`; kernel log `len` still 0 (or unchanged); halt via later `SYS_EXIT`
- OS-006: user `lw` at 0 → halt (exit 0), not a hang
- OS-011: unaligned user `lw` → halt (exit 0)
- OS-012: unimplemented COP1 from user → log magic `KPAN` (`4B 50 41 4E`). Halt.

## Out of scope

Later-generation (paging, processes, devices, FPGA).
