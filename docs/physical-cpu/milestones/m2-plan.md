# physical-cpu m2

Features: PHYSICAL-CPU-005, PHYSICAL-CPU-006, PHYSICAL-CPU-007

## Intent

Add `hw/flags/` (1-bit FLAGS latch: same CELL latch, WE = EN) and `hw/adder/` (1-bit full adder). KiCad 6 schematics parsed as text; ngspice benches use `yap_cells.lib`. m1 latch tests still pass. Same VOL/VOH as cells.

## Work

- `hw/flags/*.kicad_sch`: nets D, WE (or EN), Q, VDD, VSS. Spice: `LATCH` with EN = WE.
- `hw/adder/*.kicad_sch`: nets a, b, cin, sum, cout, VDD, VSS. Spice: `ADDER`.
- Test `.cir` files; unittest `compiler/tests/test_physical_cpu_m2.py`.

## Done

- PHYSICAL-CPU-005: flags-bit schematic is the CELL latch with WE from control
- PHYSICAL-CPU-006: adder schematic has `a`, `b`, `cin`, `sum`, `cout`
- PHYSICAL-CPU-007: adder ngspice matches CELL-012 8-row table at VOL/VOH

## Out of scope

PHYSICAL-CPU-008–015, later-generation 016–020.
