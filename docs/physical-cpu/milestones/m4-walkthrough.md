# physical-cpu m4 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3. Electrical check needs **ngspice** (`ngspice -b` on `PATH`). Does not need KiCad.

```bash
sudo apt install ngspice   # if `ngspice -b` is not on PATH
python3 -m unittest compiler.tests.test_physical_cpu_m4 compiler.tests.test_physical_cpu_m3 compiler.tests.test_physical_cpu_m2 compiler.tests.test_physical_cpu_m1 -v
```

Expected: `Ran 9 tests ... OK`. m1–m3 still pass.

## PHYSICAL-CPU-009 — 32-bit MOSFET register

```bash
python3 -m unittest compiler.tests.test_physical_cpu_m4.TestPhysicalCpuM4.test_PHYSICAL_CPU_009
```

`hw/reg32/` spice instantiates `LATCH` 32 times with one `WE` on every `EN`. `ngspice -b` on `hw/reg32/reg32_test.cir`: `WE`=1 D=0 then D=all-ones → every `q` at VOL ≤ 0.3 V then VOH ≥ 3.0 V; `WE`=0 D flipped → every `q` holds VOH. Schematic text includes `d0`, `d31`, `q0`, `q31`, `WE`.
