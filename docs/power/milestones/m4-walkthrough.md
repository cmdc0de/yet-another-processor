# Power m4 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and **ngspice** (`ngspice -b` on `PATH`).

```bash
python3 -m unittest compiler.tests.test_power_m4 compiler.tests.test_power_m3 compiler.tests.test_power_m2 compiler.tests.test_power_m1 -v
```

Expected: `Ran 10 tests ... OK`. m1–m3 still pass.

## POWER-009 — 5 V I/O level shifter

```bash
python3 -m unittest compiler.tests.test_power_m4.TestPowerM4.test_POWER_009
```

Sources name IO5, IO33, `LVLSH`. `ngspice -b` of `hw/power/lvlsh_test.cir`: HV=5.0 → LV (`v(io33)`) in 3.20–3.40 V; LV=3.3 → HV (`v(io5_up)`) in 4.75–5.25 V.
