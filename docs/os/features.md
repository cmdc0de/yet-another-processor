# Operating system features

Prefix: `OS`

v1: protected kernel, one user window, syscalls, one YAP1 on `yap-emu`. No paging. Implementation lives in `os/`. Tests assemble with `python3 -m compiler.asm` and run on `yap-emu`.

Syscall ABI is `docs/isa/design.md` (`ISA-049`). Memory map and syscall numbers are `docs/os/design.md` (after this catalog).

## Boot and image

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| OS-001 | ~~One YAP1: kernel at reset `PC=0`, trap handler at `0x80`~~ | done | m1 |
| OS-002 | ~~Image reaches halt (or `SYS_EXIT`) on `yap-emu`~~ | done | m1 |
| OS-003 | ~~Kernel stack in supervisor SRAM~~ | done | m1 |

## Protection

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| OS-004 | ~~Kernel programs `UBASE`/`ULIMIT` before entering user~~ | done | m2 |
| OS-005 | ~~User fetch/load/store only inside that window~~ | done | m2 |
| OS-006 | ~~User protection fault (CAUSE=2) is handled by the kernel~~ | implemented | m3 |

## User entry

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| OS-007 | ~~Kernel `ERET` to user entry with `P=0`~~ | done | m2 |
| OS-008 | ~~User `sp` set inside the user window~~ | done | m2 |

## Traps

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| OS-009 | ~~Trap handler saves enough user GPRs to resume (at least `a0`–`a4`, `ra`, `sp`)~~ | done | m2 |
| OS-010 | ~~`sys` (CAUSE=3) dispatches on `imm16`~~ | done | m2 |
| OS-011 | ~~Align fault (CAUSE=8) is handled (exit or errno)~~ | implemented | m3 |
| OS-012 | ~~Unknown CAUSE: kernel panic path (halt, distinguishable dump)~~ | implemented | m3 |

## Syscalls

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| OS-013 | ~~Syscall ABI as ISA-049 (`a0`–`a3` in, `a0` return, `a4` errno)~~ | done | m2 |
| OS-014 | ~~`SYS_EXIT`: machine halts; `a4=0`~~ | done | m2 |
| OS-015 | ~~`SYS_WRITE`: copy user buffer to a kernel log in SRAM (tests read it after halt)~~ | implemented | m3 |
| OS-016 | ~~Bad syscall number: `a4 ≠ 0`, user resumes~~ | implemented | m3 |
| OS-017 | ~~`SYS_WRITE` pointer outside the user window: errno, kernel memory intact~~ | implemented | m3 |

## Build

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| OS-018 | ~~Sources under `os/` assemble with `python3 -m compiler.asm`~~ | done | m1 |
| OS-019 | ~~Tests assemble a YAP1 and run it on `yap-emu`~~ | done | m1 |

## Later generation (do not pull into m1)

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| OS-020 | Page tables / virtual memory | open | later-generation |
| OS-021 | Multiple user processes / preemption | open | later-generation |
| OS-022 | Filesystem | open | later-generation |
| OS-023 | Console, MCU, GPU devices | open | later-generation |
| OS-024 | Same YAP1 on FPGA CPU then MOSFET CPU | open | later-generation |
