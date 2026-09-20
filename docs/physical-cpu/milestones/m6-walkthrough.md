# physical-cpu m6 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3. Electrical check needs **ngspice** (`ngspice -b` on `PATH`). Does not need KiCad.

```bash
sudo apt install ngspice   # if `ngspice -b` is not on PATH
python3 -m unittest compiler.tests.test_physical_cpu_m6 compiler.tests.test_physical_cpu_m5 compiler.tests.test_physical_cpu_m4 compiler.tests.test_physical_cpu_m3 compiler.tests.test_physical_cpu_m2 compiler.tests.test_physical_cpu_m1 -v
```

Expected: `Ran 11 tests ... OK`. m1–m5 still pass.

## PHYSICAL-CPU-011 — MOSFET GPR bank r3–r15

```bash
python3 -m unittest compiler.tests.test_physical_cpu_m6.TestPhysicalCpuM6.test_PHYSICAL_CPU_011
```

`hw/rf-mosfet/` spice instantiates `LATCH` 13 times (`r3`–`r15`) and a `MUX2` read mux. Schematic text includes `we3`, `we15`, `qa`, `qb`, `LAT=1`. `ngspice -b` on `hw/rf-mosfet/rf_mosfet_test.cir`: load `r3`=1 and `r4`=0; after all `we*`=0, `ra3`/`rb4` select `qa` at VOH ≥ 3.0 V and `qb` at VOL ≤ 0.3 V.
