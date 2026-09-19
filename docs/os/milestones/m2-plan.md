# os m2

Features: OS-004, OS-005, OS-007, OS-008, OS-009, OS-010, OS-013, OS-014

## Intent

Kernel programs `UBASE=0x1000` / `ULIMIT=0x8000`, sets user `sp=0x8000`, `ERET`s to user at `0x1000` with `P=0`. User runs `sys 1` (`SYS_EXIT`). Trap stub at `0x80` saves `a0`–`a4`, `ra`, `sp`, dispatches CAUSE=3, and **halts without restoring kernel `sp`** (choice A). Dump after halt shows `r4==0x8000`. Layout is `docs/os/design.md`.

## Work

- `os/kernel.s`: after setting kernel `sp`, `mtc0` window, set user `sp=0x8000`, STATUS/EPC, `ERET`. Do not `halt` on the reset path.
- User blob at `.org 0x1000`: `sys 1`.
- Trap at `0x80`: save `a0`–`a4`, `ra`, `sp` on the kernel stack; `mfc0` CAUSE; if 3, load the word at `EPC-4` and take `imm16`; if `imm16==1`, `halt` (leave `sp` as the user value `0x8000`).
- m1 tests: kernel still assembles; `yap-emu` still exits 0. OS-003’s `r4==0x1000` no longer holds after a full user exit — m2 tests replace that check for the new image. Keep a boot-only check only if a separate fixture remains; the main `os/kernel.s` image is the user-exit path.

## Done

- OS-004: dump after halt has `ubase=0x1000`, `ulimit=0x8000`
- OS-005: user code lives at `0x1000` (inside the window)
- OS-007: reset path `ERET`s; user insn at `0x1000` is `sys 1`
- OS-008: after halt, dump `r4` is `00008000`
- OS-009: trap stores those GPRs; kernel stack below `0x1000` contains saved `sp` `0x8000`
- OS-010: `sys 1` from user results in halt (exit 0), not a loop at `0x80`
- OS-013: assembled user `sys 1` has opcode SYS and imm16=1
- OS-014: `yap-emu` on the image exits 0

## Out of scope

`SYS_WRITE`, bad syscall resume, CAUSE 2/8 kill, `KPAN`, later-generation.
