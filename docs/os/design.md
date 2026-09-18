# OS design (v1)

Kernel + one user program in **one YAP1** (`load=0`, `entry=0`). Runs on `yap-emu`. No paging, no devices. Output is a **kernel log in SRAM** that tests read after halt.

ISA trap vector **0x80** and reset **PC=0** stay as `docs/isa/design.md`.

## Memory map

Addresses are payload/CPU addresses. SRAM size ≥ 64KiB (emulator default).

| Region | Addresses | Notes |
|--------|-----------|--------|
| Reset | `0x0000` | Kernel entry. May `j` to later kernel text. |
| Trap vector | `0x0080` | ISA-fixed. First insn of the trap stub. |
| Kernel text/data | `0x0000`–`0x07FF` | Includes reset and `0x80`. Supervisor only. |
| Kernel log | `0x0800`–`0x08FF` | 256 bytes. Format below. |
| Kernel stack | grows down from `0x1000` | Empty at `sp=0x1000`. Must not store below `0x0900`. |
| User window | `[0x1000, 0x8000)` | `UBASE=0x1000`, `ULIMIT=0x8000` (28KiB). |
| User text | `0x1000`… | User entry. |
| User stack | grows down from `0x8000` | `sp=0x8000` at first `ERET`. Last valid user byte is `0x7FFF`. |

`UBASE`/`ULIMIT` are set **before** the first user `ERET`. Kernel fetch/load/store at `< 0x1000` is supervisor (no window check). User access outside `[0x1000, 0x8000)` is CAUSE=2.

Raising `ULIMIT` later (more SRAM) is a kernel constant change only. The ISA already accepts any 32-bit window. Do not set `ULIMIT` past physical SRAM.

User stack is **empty descending**: initial `sp=ULIMIT` is not dereferenced; the first push decrements, then stores, so the first word is at `0x7FFC`.

## Kernel log (`0x0800`)

Little-endian.

```
+0  u32 magic   ASCII `YLOG` (bytes `59 4C 4F 47`)
+4  u32 len     bytes of payload used (0..248)
+8  u8  data[]  up to 248 bytes
```

`SYS_WRITE` appends to `data` and increases `len`, truncating if full. Panic may set `magic` to ASCII `KPAN` (`4B 50 41 4E`) and `halt`.

## Syscalls

`sys imm16`. Args `a0`–`a3`. Success: `a0` = return, `a4` = 0. Failure: `a4` ≠ 0 (`ISA-049`).

| imm16 | Name | Args | Success | Failure `a4` |
|-------|------|------|---------|----------------|
| 1 | `SYS_EXIT` | `a0` unused | halt; `a4` stays 0 | — |
| 2 | `SYS_WRITE` | `a0` = user ptr, `a1` = len | `a0` = bytes copied | 1 bad ptr/len or outside window; 2 log full (0 bytes) |

Any other `imm16`: `a4 = 1`, `a0` unchanged, `ERET` to user.

`SYS_WRITE` ptr must satisfy `UBASE <= ptr` and `ptr+len <= ULIMIT` (and `len` fits in 32-bit). No copy if the check fails.

## Traps

Stub at `0x80` uses `k0` as scratch. Saves at least `a0`–`a4`, `ra`, `sp` on the kernel stack, reads `CAUSE`, dispatches, restores, `ERET`.

| CAUSE | Kernel action |
|-------|----------------|
| 3 | syscall dispatch |
| 2 | protection: treat as kill — `SYS_EXIT` path (halt). Optional: set log panic magic. |
| 8 | align: same as protection (halt) in v1 |
| other | panic magic `KPAN`, halt |

v1 does not resume the user after CAUSE 2 or 8.

## User entry

1. Set kernel `sp`.
2. `mtc0` UBASE=`0x1000`, ULIMIT=`0x8000`.
3. Set user `sp=0x8000` (in the saved frame or in `sp` before drop).
4. STATUS: `P=0`, `IE=0`, `TE=0`; `PP`/`PIE` such that `ERET` enters user.
5. `EPC` = user entry (`0x1000`).
6. `ERET`.

User ends with `sys 1` (`SYS_EXIT`).

## Out of this document

Paging, multiple processes, filesystems, UART/MCU/GPU, FPGA/MOSFET bring-up.
