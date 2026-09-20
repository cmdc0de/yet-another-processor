# physical-cpu m8 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3. Electrical check needs **ngspice** (`ngspice -b` on `PATH`). Does not need KiCad.

```bash
sudo apt install ngspice   # if `ngspice -b` is not on PATH
python3 -m unittest compiler.tests.test_physical_cpu_m8 compiler.tests.test_physical_cpu_m7 compiler.tests.test_physical_cpu_m6 compiler.tests.test_physical_cpu_m5 compiler.tests.test_physical_cpu_m4 compiler.tests.test_physical_cpu_m3 compiler.tests.test_physical_cpu_m2 compiler.tests.test_physical_cpu_m1 -v
```

Expected: `Ran 13 tests ... OK`. m1–m7 still pass.

## PHYSICAL-CPU-013 — microcode ROM and uPC

```bash
python3 -m unittest compiler.tests.test_physical_cpu_m8.TestPhysicalCpuM8.test_PHYSICAL_CPU_013
```

`hw/ucode/` schematic text includes `upc0`, `upc7`, `cw0`, `cw63`, `256x64`. Spice does not use `LATCH` as the ROM. `ngspice -b` on `hw/ucode/ucode_test.cir`: after reset, `upc*` at VOL and `cw2..cw0` at VOL (NEXT); after one `clk`, `upc0` at VOH and `upc1`–`upc7` at VOL; `cw0`–`cw2` match ROM[1] at VOL/VOH and differ from ROM[0].
