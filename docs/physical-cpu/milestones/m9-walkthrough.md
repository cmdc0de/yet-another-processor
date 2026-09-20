# physical-cpu m9 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3. Electrical check needs **ngspice** (`ngspice -b` on `PATH`). Does not need KiCad.

```bash
sudo apt install ngspice   # if `ngspice -b` is not on PATH
python3 -m unittest compiler.tests.test_physical_cpu_m9 compiler.tests.test_physical_cpu_m8 compiler.tests.test_physical_cpu_m7 compiler.tests.test_physical_cpu_m6 compiler.tests.test_physical_cpu_m5 compiler.tests.test_physical_cpu_m4 compiler.tests.test_physical_cpu_m3 compiler.tests.test_physical_cpu_m2 compiler.tests.test_physical_cpu_m1 -v
```

Expected: `Ran 14 tests ... OK`. m1–m8 still pass.

## PHYSICAL-CPU-014 — CPU memory port

```bash
python3 -m unittest compiler.tests.test_physical_cpu_m9.TestPhysicalCpuM9.test_PHYSICAL_CPU_014
```

`hw/memport/` schematic text includes `addr0`, `addr31`, `wdata0`, `rdata0`, `sz0`, `re`, `we`, `LAT_MEM=1`. `ngspice -b` on `hw/memport/memport_test.cir`: `sz=word`, `we` writes `wdata` with bit0=1 and bit1=0; after one `clk`, `re` yields `rdata0` at VOH ≥ 3.0 V and `rdata1` at VOL ≤ 0.3 V.
