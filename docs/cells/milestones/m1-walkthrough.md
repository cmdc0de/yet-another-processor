# cells m1 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and **ngspice** (`ngspice -b` on `PATH`). On Debian/Kali: `sudo apt install ngspice`. Missing `ngspice` is a failed test, not a skip.

```bash
python3 -m unittest compiler.tests.test_cells_m1 -v
```

Expected: `Ran 6 tests ... OK`.

## CELL-001 — 3.3 V rails

```bash
python3 -m unittest compiler.tests.test_cells_m1.TestCellsM1.test_CELL_001_rails
```

`lt-spice/inverter_test.cir` and `nand_test.cir` have `VDD … DC 3.3` and node `0` as ground.

## CELL-002 — IRLML6246 / IRLML6401

```bash
python3 -m unittest compiler.tests.test_cells_m1.TestCellsM1.test_CELL_002_models
```

`lt-spice/yap_cells.lib` `.model` names are IRLML6246 and IRLML6401; inverter/NAND instantiate those parts.

## CELL-004 — inverter

```bash
python3 -m unittest compiler.tests.test_cells_m1.TestCellsM1.test_CELL_004_inverter
```

Vin=0 → Vout ≥ 3.0 V; Vin=3.3 → Vout ≤ 0.3 V.

## CELL-005 — NAND

```bash
python3 -m unittest compiler.tests.test_cells_m1.TestCellsM1.test_CELL_005_nand
```

AB=00,01,10 → Y ≥ 3.0 V; AB=11 → Y ≤ 0.3 V.

## CELL-014 — VOH/VOL

```bash
python3 -m unittest compiler.tests.test_cells_m1.TestCellsM1.test_CELL_014_levels
```

Same settled points as CELL-004/005.

## CELL-018 — ngspice batch

```bash
python3 -m unittest compiler.tests.test_cells_m1.TestCellsM1.test_CELL_018_ngspice_batch
```

Unittest runs `ngspice -b` (no LTspice/GUI).
