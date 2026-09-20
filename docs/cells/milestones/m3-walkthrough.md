# cells m3 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and **ngspice** (`ngspice -b` on `PATH`).

```bash
python3 -m unittest compiler.tests.test_cells_m3 compiler.tests.test_cells_m2 compiler.tests.test_cells_m1 -v
```

Expected: `Ran 17 tests ... OK`. m1–m2 still pass.

## CELL-012 — 1-bit adder

```bash
python3 -m unittest compiler.tests.test_cells_m3.TestCellsM3.test_CELL_012_adder_table
```

All 8 `a,b,cin` rows: `sum` and `cout` at VOL/VOH for a full adder.

## CELL-013 — latch follow

```bash
python3 -m unittest compiler.tests.test_cells_m3.TestCellsM3.test_CELL_013_latch_follow
```

EN=1, D=0 then D=3.3: Q at VOL then VOH.

## CELL-015 — per-cell benches

```bash
python3 -m unittest compiler.tests.test_cells_m3.TestCellsM3.test_CELL_015_benches
```

`lt-spice/*_test.cir` exists for INVERTER, NAND, NOR, AND, OR, XOR, TG, MUX2, LATCH, ADDER and instantiates that `.subckt`.

## CELL-016 — latch hold

```bash
python3 -m unittest compiler.tests.test_cells_m3.TestCellsM3.test_CELL_016_latch_hold
```

`.tran`: after EN falls, D 3.3→0 leaves Q ≥ 3.0 V; D 0→3.3 leaves Q ≤ 0.3 V.

## CELL-017 — adder corners

```bash
python3 -m unittest compiler.tests.test_cells_m3.TestCellsM3.test_CELL_017_adder_corners
```

0+0+cin0 → sum and cout ≤ 0.3 V; 1+1+cin1 → both ≥ 3.0 V.
