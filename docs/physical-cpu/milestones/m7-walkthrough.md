# physical-cpu m7 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3. Electrical check needs **ngspice** (`ngspice -b` on `PATH`). Does not need KiCad.

```bash
sudo apt install ngspice   # if `ngspice -b` is not on PATH
python3 -m unittest compiler.tests.test_physical_cpu_m7 compiler.tests.test_physical_cpu_m6 compiler.tests.test_physical_cpu_m5 compiler.tests.test_physical_cpu_m4 compiler.tests.test_physical_cpu_m3 compiler.tests.test_physical_cpu_m2 compiler.tests.test_physical_cpu_m1 -v
```

Expected: `Ran 12 tests ... OK`. m1–m6 still pass.

## PHYSICAL-CPU-012 — IC GPR bank r16–r31

```bash
python3 -m unittest compiler.tests.test_physical_cpu_m7.TestPhysicalCpuM7.test_PHYSICAL_CPU_012
```

`hw/rf-ic/` spice instantiates 16 `ICREG` bits (`r16`–`r31`), not `LATCH`. Schematic text includes `we16`, `we31`, `qa`, `qb`, `LAT=2`. `ngspice -b` on `hw/rf-ic/rf_ic_test.cir`: load `r16`=1 and `r17`=0; after all `we*`=0, `ra16`/`rb17` select `qa` at VOH ≥ 3.0 V and `qb` at VOL ≤ 0.3 V.
