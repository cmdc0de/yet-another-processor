# power m3 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| POWER-010 | `ngspice -b`: EN=VIN, `v(vdd)` in 3.20–3.40 V; EN=0, `v(vdd)` ≤ 0.3 V. Schematic/netlist still names EN. |
