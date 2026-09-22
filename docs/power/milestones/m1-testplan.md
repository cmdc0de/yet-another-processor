# power m1 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| POWER-001 | `hw/power/` contains SPICE `.cir` / `.subckt` sources |
| POWER-002 | `ngspice -b` of the rail test exits 0 |
| POWER-003 | Tests fail if `ngspice` is not on `PATH` |
| POWER-004 | Sources name nets VIN and VSS; test VIN is DC 5.0 V, VSS is 0 |
| POWER-005 | Sources instantiate subckt `REG33` with pins VIN, VDD, VSS |
| POWER-006 | Printed `v(vdd)` after settling is ≥ 3.20 V and ≤ 3.40 V |
| POWER-007 | Sources state CPU core, SRAM/bus, and MCU I/O use VDD (not VIN) |
