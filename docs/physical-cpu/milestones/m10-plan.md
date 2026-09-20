# physical-cpu m10

Features: PHYSICAL-CPU-015

## Intent

1-bit MOSFET ALU using CELL `ADDER`, `AND`, `OR`, `XOR`, `INVERTER`, `MUX2`. New slice `hw/alu/`. KiCad 6 parsed as text; ngspice on `yap_cells.lib`. m1–m9 still pass. Same VOL/VOH, 5 pF on `y` and `cout`.

## Work

- `hw/alu/*.kicad_sch`: nets `a`, `b`, `cin`, `y`, `cout`, `op0`–`op2` (`alu_op` 0–4), `VDD`, `VSS`. Instantiates `ADDER` plus logic cells. Not `LATCH`.
- `hw/alu/*_test.cir`: same ports; DC (or `.control` `op`/`alter`) vectors for ADD, SUB, AND, XOR.
- unittest `compiler/tests/test_physical_cpu_m10.py`.

## Done

- PHYSICAL-CPU-015: MOSFET add/sub/logic; ngspice ADD `1+0+0` → `y` VOH `cout` VOL; SUB `1−0` → `y` VOH; AND `1∧1` → `y` VOH; XOR `1⊕1` → `y` VOL

## Out of scope

Later-generation 016–020. No shifter, MUL, DIV, FLAGS, 32-bit copies, no fab.
