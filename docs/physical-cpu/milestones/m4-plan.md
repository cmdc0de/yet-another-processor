# physical-cpu m4

Features: PHYSICAL-CPU-009

## Intent

32-bit MOSFET register: 32 copies of the m1 CELL `LATCH`, one write-enable `WE` tied to every `EN`. New slice `hw/reg32/` (do not overwrite `hw/latch/`). KiCad 6 parsed as text; ngspice on `yap_cells.lib`. m1–m3 tests still pass. Same VOL ≤ 0.3 V / VOH ≥ 3.0 V, 5 pF. EN high = load, same as the 1-bit latch.

## Work

- `hw/reg32/*.kicad_sch`: 32 `LATCH` instances. Nets `d0`–`d31`, `q0`–`q31`, `WE` (to every `EN`), `VDD`, `VSS`.
- `hw/reg32/*_test.cir`: 32 `LATCH` subckts, shared `WE`; 5 pF on each `q` bit.
- unittest `compiler/tests/test_physical_cpu_m4.py`.

## Done

- PHYSICAL-CPU-009: 32 latches, one `WE`; ngspice follow when `WE`=1 and hold when `WE`=0 at VOL/VOH

## Out of scope

PHYSICAL-CPU-010–015, later-generation 016–020. No wired `r0`–`r2` (010), no two-port GPR banks (011–012).
