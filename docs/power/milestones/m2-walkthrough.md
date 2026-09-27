# Power m2 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and **ngspice** (`ngspice -b` on `PATH`).

```bash
python3 -m unittest compiler.tests.test_power_m2 compiler.tests.test_power_m1 -v
```

Expected: `Ran 8 tests ... OK`. m1 still passes.

## POWER-008 — AP2112M-3.3TRG1

```bash
python3 -m unittest compiler.tests.test_power_m2.TestPowerM2.test_POWER_008
```

`hw/power/` schematic/netlist names `AP2112M-3.3TRG1`. Nets VIN, VDD (VOUT), VSS (GND), EN present. `ngspice -b` of the rail test: `v(vdd)` is ≥ 3.20 V and ≤ 3.40 V.
