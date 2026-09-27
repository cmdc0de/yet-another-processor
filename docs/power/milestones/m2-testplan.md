# power m2 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| POWER-008 | `hw/power/` schematic/netlist names `AP2112M-3.3TRG1`. Nets VIN, VDD (VOUT), VSS (GND), EN present. `ngspice -b` of the rail test: `v(vdd)` is ≥ 3.20 V and ≤ 3.40 V. m1 tests still pass. |
