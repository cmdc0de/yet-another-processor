# cells m2 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and **ngspice** (`ngspice -b` on `PATH`).

```bash
python3 -m unittest compiler.tests.test_cells_m2 compiler.tests.test_cells_m1 -v
```

Expected: `Ran 12 tests ... OK`. m1 still passes.

## CELL-006 — NOR

```bash
python3 -m unittest compiler.tests.test_cells_m2.TestCellsM2.test_CELL_006_nor
```

AB=00 → Y ≥ 3.0 V; 01/10/11 → Y ≤ 0.3 V.

## CELL-007 — AND

```bash
python3 -m unittest compiler.tests.test_cells_m2.TestCellsM2.test_CELL_007_and
```

AB=11 → Y ≥ 3.0 V; 00/01/10 → Y ≤ 0.3 V.

## CELL-008 — OR

```bash
python3 -m unittest compiler.tests.test_cells_m2.TestCellsM2.test_CELL_008_or
```

AB=00 → Y ≤ 0.3 V; 01/10/11 → Y ≥ 3.0 V.

## CELL-009 — XOR

```bash
python3 -m unittest compiler.tests.test_cells_m2.TestCellsM2.test_CELL_009_xor
```

AB=01/10 → Y ≥ 3.0 V; 00/11 → Y ≤ 0.3 V.

## CELL-010 — transmission gate

```bash
python3 -m unittest compiler.tests.test_cells_m2.TestCellsM2.test_CELL_010_tg
```

EN=1: OUT follows IN at VOL/VOH. EN=0: OUT stays mid (does not follow IN).

## CELL-011 — 2:1 mux

```bash
python3 -m unittest compiler.tests.test_cells_m2.TestCellsM2.test_CELL_011_mux2
```

S=0 → Y=A; S=1 → Y=B for A/B in {0, 3.3}, VOL/VOH.
