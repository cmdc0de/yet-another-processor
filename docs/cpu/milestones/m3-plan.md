# cpu m3

Features: CPU-014, CPU-015, CPU-026, CPU-027

## Intent

Data memory on the clocked model. Address is `rs+sext(imm16)`. Word/half/byte load/store are little-endian and do not write FLAGS. User window and alignment are checked **before** `re`/`we`. m1–m2 tests still pass.

## Work

- Microcode for `lw`/`lh`/`lb`/`lbu`/`lhu`/`sw`/`sh`/`sb`: read `rs`, `MAR ← rs+sext(imm16)`, size, `mem_re`/`mem_we`, write `rd` from `MDR` (sign/zero extend on loads).
- Memory port: `addr`, `wdata`/`rdata`, size ∈ {1,2,4}, `re`/`we`, `LAT_MEM=1`.
- Before `re`/`we`: if user and not `UBASE ≤ addr && addr+size-1 < ULIMIT` → TRAP 2; if misaligned → TRAP 8; no SRAM write.
- Fetch already checks PC window when `p=0` (complete CPU-026). Tests may set `cpu.p=0` (ERET is later).
- Tests in `compiler/tests/test_cpu_m3.py`.

## Done

- CPU-014: `sw` then `lw` of a word; `sb`/`lb` LE byte; address uses `rs+sext(imm16)`
- CPU-015: after `sw t0, 0(zero)` with `t0=0x12345678`, SRAM bytes at 0 are `78 56 34 12`
- CPU-026: `p=0`, `UBASE=0x1000`, `ULIMIT=0x8000`, `lw` at 0 → CAUSE=2; SRAM unchanged
- CPU-027: `lw` from address 1 → CAUSE=8; `sw` to 1 does not write SRAM

## Out of scope

CPU-016–017, CPU-020, CPU-024–025, CPU-028–031, jumps/branches (not in catalog), later-generation CPU-033–038.
