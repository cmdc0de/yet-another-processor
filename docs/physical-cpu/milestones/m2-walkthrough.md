# physical-cpu m2 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3. Electrical check needs **ngspice** (`ngspice -b` on `PATH`). Does not need KiCad.

```bash
sudo apt install ngspice   # if `ngspice -b` is not on PATH
python3 -m unittest compiler.tests.test_physical_cpu_m2 compiler.tests.test_physical_cpu_m1 -v
```

Expected: `Ran 7 tests ... OK`. m1 latch tests still pass.

## PHYSICAL-CPU-005 — FLAGS latch

```bash
python3 -m unittest compiler.tests.test_physical_cpu_m2.TestPhysicalCpuM2.test_PHYSICAL_CPU_005
```

`hw/flags/` schematic includes D, Q, VDD, VSS and WE (CELL `LATCH` EN). Spice instantiates `LATCH` with EN = WE.

## PHYSICAL-CPU-006 — adder ports

```bash
python3 -m unittest compiler.tests.test_physical_cpu_m2.TestPhysicalCpuM2.test_PHYSICAL_CPU_006
```

`hw/adder/` schematic text includes nets `a`, `b`, `cin`, `sum`, `cout`.

## PHYSICAL-CPU-007 — adder truth table

```bash
python3 -m unittest compiler.tests.test_physical_cpu_m2.TestPhysicalCpuM2.test_PHYSICAL_CPU_007
```

`ngspice -b` on `hw/adder/adder_test.cir`: 8 `a,b,cin` rows; `sum`/`cout` at VOL ≤ 0.3 V / VOH ≥ 3.0 V (CELL-012 table).
