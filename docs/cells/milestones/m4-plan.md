# cells m4

Features: CELL-003

## Intent

Each v1 cell is instantiable as an LTspice **BLOCK** symbol (`Prefix X`) whose `Value` is the `yap_cells.lib` `.subckt` name, not a flattened MOSFET netlist and not AO3400. ngspice tests from m1–m3 still pass and still do not require LTspice.

## Work

- `.asy` under `lt-spice/` for INVERTER, NAND, NOR, AND, OR, XOR, TG, MUX2, LATCH, ADDER.
- `SYMATTR Prefix X`, `Value` / `SpiceModel` = subckt name, `ModelFile yap_cells.lib`.
- Pin `SpiceOrder` matches the `.subckt` port list (including `vdd` `gnd`).
- Unittest `compiler/tests/test_cells_m4.py` reads the `.asy` files. No GUI.

## Done

- CELL-003: those ten symbols exist; each is `Prefix X` with `Value` equal to the matching `.subckt`; none flatten to discrete MOSFET pins only

## Out of scope

Later-generation CELL-019–021. Physical CPU boards.
