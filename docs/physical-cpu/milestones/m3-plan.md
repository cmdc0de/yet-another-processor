# physical-cpu m3

Features: PHYSICAL-CPU-008

## Intent

32-bit ripple adder: 32 copies of the m2 1-bit CELL `ADDER`, `cout` of bit *i* into `cin` of bit *i*+1. New slice `hw/adder32/` (do not overwrite `hw/adder/`). KiCad 6 parsed as text; ngspice on `yap_cells.lib`. m1–m2 tests still pass. Same VOL ≤ 0.3 V / VOH ≥ 3.0 V, 5 pF.

## Work

- `hw/adder32/*.kicad_sch`: 32 `ADDER` instances. Nets `a0`–`a31`, `b0`–`b31`, `sum0`–`sum31`, `cin` (into bit 0), `cout` (from bit 31), `VDD`, `VSS`. Bit *i* `cout` feeds bit *i*+1 `cin`.
- `hw/adder32/*_test.cir`: 32 `ADDER` subckts, same ripple; 5 pF on each `sum` bit and final `cout`.
- unittest `compiler/tests/test_physical_cpu_m3.py`.

## Done

- PHYSICAL-CPU-008: 32 adder bits, ripple `cin`/`cout`; ngspice all-zero and all-ones+1 at VOL/VOH

## Out of scope

PHYSICAL-CPU-009–015, later-generation 016–020. No subtract/logic ALU (015), no 32-bit register (009).
