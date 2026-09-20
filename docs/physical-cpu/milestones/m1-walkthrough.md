# physical-cpu m1 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3. Electrical check needs **ngspice** (`ngspice -b` on `PATH`). Does not need KiCad.

```bash
python3 -m unittest compiler.tests.test_physical_cpu_m1 -v
```

Expected: `Ran 4 tests ... OK`.

## PHYSICAL-CPU-001 — hw tree

```bash
python3 -m unittest compiler.tests.test_physical_cpu_m1.TestPhysicalCpuM1.test_PHYSICAL_CPU_001
```

`hw/` contains at least one `.kicad_sch`.

## PHYSICAL-CPU-002 — CELL latch

```bash
python3 -m unittest compiler.tests.test_physical_cpu_m1.TestPhysicalCpuM1.test_PHYSICAL_CPU_002
```

Schematic / spice view instantiates `LATCH` (EN high = load).

## PHYSICAL-CPU-003 — ports

```bash
python3 -m unittest compiler.tests.test_physical_cpu_m1.TestPhysicalCpuM1.test_PHYSICAL_CPU_003
```

Schematic text includes nets `D`, `EN`, `Q`, `VDD`, `VSS`.

## PHYSICAL-CPU-004 — ngspice follow/hold

```bash
python3 -m unittest compiler.tests.test_physical_cpu_m1.TestPhysicalCpuM1.test_PHYSICAL_CPU_004
```

`ngspice -b` on `hw/latch/latch_test.cir`: follow D=0 then D=3.3 at EN=1; hold after EN=0 (VOL ≤ 0.3 V / VOH ≥ 3.0 V).
