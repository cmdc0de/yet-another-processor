# physical-cpu m3 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3. Electrical check needs **ngspice** (`ngspice -b` on `PATH`). Does not need KiCad.

```bash
sudo apt install ngspice   # if `ngspice -b` is not on PATH
python3 -m unittest compiler.tests.test_physical_cpu_m3 compiler.tests.test_physical_cpu_m2 compiler.tests.test_physical_cpu_m1 -v
```

Expected: `Ran 8 tests ... OK`. m1–m2 still pass.

## PHYSICAL-CPU-008 — 32-bit ripple adder

```bash
python3 -m unittest compiler.tests.test_physical_cpu_m3.TestPhysicalCpuM3.test_PHYSICAL_CPU_008
```

`hw/adder32/` spice instantiates `ADDER` 32 times; bit-*i* `cout` feeds bit-*i*+1 `cin`. `ngspice -b` on `hw/adder32/adder32_test.cir`: (1) a=b=cin=0 → every `sum` and `cout` at VOL ≤ 0.3 V; (2) a=all-ones, b=0, cin=1 → every `sum` at VOL and `cout` at VOH ≥ 3.0 V. Schematic text includes `a0`, `a31`, `sum0`, `sum31`.
