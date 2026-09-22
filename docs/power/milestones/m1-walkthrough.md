# Power m1 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and **ngspice** (`ngspice -b` on `PATH`). On Debian/Kali: `sudo apt install ngspice`. Missing `ngspice` is a failed test, not a skip.

```bash
python3 -m unittest compiler.tests.test_power_m1 -v
```

Expected: `Ran 7 tests ... OK`.

## POWER-001 — HDL/SPICE tree

```bash
python3 -m unittest compiler.tests.test_power_m1.TestPowerM1.test_POWER_001
```

`hw/power/` contains SPICE `.cir` / `.subckt` sources.

## POWER-002 — sim runs

```bash
python3 -m unittest compiler.tests.test_power_m1.TestPowerM1.test_POWER_002
```

`ngspice -b` of the rail test exits 0.

## POWER-003 — ngspice required

```bash
python3 -m unittest compiler.tests.test_power_m1.TestPowerM1.test_POWER_003
```

Fails if `ngspice` is not on `PATH`.

## POWER-004 — VIN and VSS

```bash
python3 -m unittest compiler.tests.test_power_m1.TestPowerM1.test_POWER_004
```

Sources name nets VIN and VSS; test VIN is DC 5.0 V, VSS is 0.

## POWER-005 — REG33

```bash
python3 -m unittest compiler.tests.test_power_m1.TestPowerM1.test_POWER_005
```

Sources instantiate subckt `REG33` with pins VIN, VDD, VSS.

## POWER-006 — VDD window

```bash
python3 -m unittest compiler.tests.test_power_m1.TestPowerM1.test_POWER_006
```

Printed `v(vdd)` after settling is ≥ 3.20 V and ≤ 3.40 V.

## POWER-007 — domain on VDD

```bash
python3 -m unittest compiler.tests.test_power_m1.TestPowerM1.test_POWER_007
```

Sources state CPU core, SRAM/bus, and MCU I/O use VDD (not VIN).
