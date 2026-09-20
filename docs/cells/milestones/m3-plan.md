# cells m3

Features: CELL-012, CELL-013, CELL-015, CELL-016, CELL-017

## Intent

Add the static D-latch and 1-bit full adder on the m1/m2 ngspice harness (`docs/cells/design.md`: EN active-high, MOSFET-only adder). Every v1 cell then has a `*_test.cir` under `lt-spice/`. m1–m2 tests still pass.

## Work

- `.subckt LATCH` (D, EN, Q): EN=1 transparent, EN=0 hold. Built from existing cells (e.g. mux/TG + inverter).
- `.subckt ADDER` (a, b, cin, sum, cout). MOSFET cells only.
- `latch_test.cir`, `adder_test.cir`. CELL-015: inverter through mux already have benches; this slice adds latch and adder so each of CELL-004–013 has a test `.cir`.
- Unittest `compiler/tests/test_cells_m3.py` runs `ngspice -b`. Latch hold is a **transient** (not only `.op`): load, then EN=0, then D flips, Q stays.

## Done

- CELL-012: adder `sum`/`cout` at VOH/VOL for the CELL-017 vectors (and the rest of the 8-row table)
- CELL-013: EN=1 → Q follows D; EN=0 → Q holds
- CELL-015: `lt-spice/` contains a `*_test.cir` that instantiates each of INVERTER, NAND, NOR, AND, OR, XOR, TG, MUX2, LATCH, ADDER
- CELL-016: after EN falls, D 0→3.3 (and 3.3→0) leaves Q unchanged in the `.tran`
- CELL-017: 0+0+cin0 → sum=0,cout=0; 1+1+cin1 → sum=1,cout=1

## Out of scope

CELL-003, later-generation 019–021.
