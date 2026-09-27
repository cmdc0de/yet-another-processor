# Physical CPU m11 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3. m1 electrical check needs **ngspice** (`ngspice -b` on `PATH`). Does not need KiCad.

```bash
python3 -m unittest compiler.tests.test_physical_cpu_m11 compiler.tests.test_physical_cpu_m1 -v
```

Expected: `Ran 5 tests ... OK`. m1 still passes.

## PHYSICAL-CPU-016 — 1-bit latch PCB

```bash
python3 -m unittest compiler.tests.test_physical_cpu_m11.TestPhysicalCpuM11.test_PHYSICAL_CPU_016
```

`hw/latch/` contains a `.kicad_pcb`. File text names `IRLML6246`, `IRLML6401`, `MICRO3_SOT23_INF`, and nets `D`, `EN`, `Q`, `VDD`, `VSS`.
