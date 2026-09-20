# physical-cpu m10 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3. Electrical check needs **ngspice** (`ngspice -b` on `PATH`). Does not need KiCad.

```bash
sudo apt install ngspice   # if `ngspice -b` is not on PATH
python3 -m unittest compiler.tests.test_physical_cpu_m10 compiler.tests.test_physical_cpu_m9 compiler.tests.test_physical_cpu_m8 compiler.tests.test_physical_cpu_m7 compiler.tests.test_physical_cpu_m6 compiler.tests.test_physical_cpu_m5 compiler.tests.test_physical_cpu_m4 compiler.tests.test_physical_cpu_m3 compiler.tests.test_physical_cpu_m2 compiler.tests.test_physical_cpu_m1 -v
```

Expected: `Ran 15 tests ... OK`. m1–m9 still pass.

## PHYSICAL-CPU-015 — MOSFET ALU add/sub/logic

```bash
python3 -m unittest compiler.tests.test_physical_cpu_m10.TestPhysicalCpuM10.test_PHYSICAL_CPU_015
```

`hw/alu/` schematic text includes `a`, `b`, `y`, `op0`. Spice instantiates `ADDER` and `AND`/`XOR`. `ngspice -b` on `hw/alu/alu_test.cir`: ADD a=1 b=0 cin=0 → `y` VOH ≥ 3.0 V, `cout` VOL ≤ 0.3 V; SUB a=1 b=0 → `y` VOH; AND a=1 b=1 → `y` VOH; XOR a=1 b=1 → `y` VOL.
