# cells m4 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3. Does **not** need LTspice or ngspice.

```bash
python3 -m unittest compiler.tests.test_cells_m4 -v
```

Expected: `Ran 1 test ... OK`.

m1–m3 still pass if `ngspice` is on `PATH`:

```bash
python3 -m unittest compiler.tests.test_cells_m1 compiler.tests.test_cells_m2 compiler.tests.test_cells_m3 compiler.tests.test_cells_m4 -v
```

## CELL-003 — LTspice symbols

```bash
python3 -m unittest compiler.tests.test_cells_m4.TestCellsM4.test_CELL_003_symbols
```

For INVERTER, NAND, NOR, AND, OR, XOR, TG, MUX2, LATCH, ADDER: an `.asy` in `lt-spice/` has `Prefix X`, `Value` or `SpiceModel` equal to that name, and `ModelFile` contains `yap_cells.lib`.
