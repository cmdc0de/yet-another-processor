# physical-cpu m5 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3. Electrical check needs **ngspice** (`ngspice -b` on `PATH`). Does not need KiCad.

```bash
sudo apt install ngspice   # if `ngspice -b` is not on PATH
python3 -m unittest compiler.tests.test_physical_cpu_m5 compiler.tests.test_physical_cpu_m4 compiler.tests.test_physical_cpu_m3 compiler.tests.test_physical_cpu_m2 compiler.tests.test_physical_cpu_m1 -v
```

Expected: `Ran 10 tests ... OK`. m1–m4 still pass.

## PHYSICAL-CPU-010 — wired r0 r1 r2

```bash
python3 -m unittest compiler.tests.test_physical_cpu_m5.TestPhysicalCpuM5.test_PHYSICAL_CPU_010
```

`hw/wired/` schematic text includes `r0_0`, `r1_0`, `r2_31`. Spice does not instantiate `LATCH`. `ngspice -b` on `hw/wired/wired_test.cir`: every `r0_*` at VOL ≤ 0.3 V; `r1_0` at VOH ≥ 3.0 V and `r1_1`–`r1_31` at VOL; every `r2_*` at VOH.
