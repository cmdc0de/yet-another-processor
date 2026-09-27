# Power m3 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and **ngspice** (`ngspice -b` on `PATH`).

```bash
python3 -m unittest compiler.tests.test_power_m3 compiler.tests.test_power_m2 compiler.tests.test_power_m1 -v
```

Expected: `Ran 9 tests ... OK`. m1–m2 still pass.

## POWER-010 — EN on/off

```bash
python3 -m unittest compiler.tests.test_power_m3.TestPowerM3.test_POWER_010
```

`ngspice -b` of `hw/power/en_test.cir`: EN=VIN, `v(vdd)` in 3.20–3.40 V; EN=0, `v(vdd)` ≤ 0.3 V. Schematic/netlist names EN.
