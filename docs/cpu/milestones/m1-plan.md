# cpu m1

Features: CPU-001, CPU-002, CPU-003, CPU-004, CPU-005, CPU-006, CPU-007, CPU-018, CPU-019, CPU-021, CPU-022, CPU-023

## Intent

Stand up `compiler.yap_cpu`: one clock per `step()`, 64-bit microcode from `docs/cpu/design.md`. Fetch a 32-bit insn into IR. `halt` stops. `add`/`sub` retire with ISA flags and `PC+4`. Unaligned fetch traps to `0x80`. Architectural state at halt matches `yap_isa.Cpu` on the same image.

## Work

- Package `compiler.yap_cpu` (`Cpu.step()` = one cycle) plus `ucode.py` (fetch, SPECIAL `add`/`sub`/`halt`, trap).
- Split RF banks as in design (wired / MOSFET / IC) with stall latencies; m1 does not require a cycle-count assertion.
- SRAM + memory port for fetch only (`LAT_MEM=1`). Halt image at `0`; trap tests put `halt` at `0x80`.
- Tests in `compiler/tests/test_cpu_m1.py`. Images via `compiler.yap_isa.assemble` or `compiler.asm`.

## Done

- CPU-001: addresses and datapath values are 32-bit
- CPU-002: `PC` is readable; `add` then `halt` leaves `PC` at the `halt` insn (not still 0)
- CPU-003: after fetch of `halt` at 0, `IR` is the halt word
- CPU-004: `t0` (MOSFET) and `s0` (IC) both read/write; software sees one file
- CPU-005: `add zero, one, one` leaves `r0==0` and sets flags (`Z=0`)
- CPU-006: FLAGS are not a GPR; ADD `1+1` → `Z=0 N=0 C=0 V=0`
- CPU-007: `add t0, one, one` → `t0==2`; `sub t0, one, one` → `t0==0`, `Z=1`
- CPU-018: `halt` takes more than one cycle (fetch + dispatch + halt)
- CPU-019: SPECIAL `halt` and `add` take different microcode entries (halt stops; add retires)
- CPU-021: aligned fetch loads IR; `PC=1` → CAUSE=8
- CPU-022: after `halt`, further `step()` does not advance `uPC` / `PC`
- CPU-023: unaligned fetch: `CAUSE=8`, `P=1`, `IE=0`, `EPC=1`, `PC=0x80`

## Out of scope

CPU-008–017 (logic, shift, mul, imm, loads, CSR/COP1 files as features), CPU-020 full steering, CPU-024–032, later-generation CPU-033–038.
