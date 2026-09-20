# physical-cpu m2 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| PHYSICAL-CPU-005 | `hw/flags/` schematic includes D, Q, VDD, VSS and WE or EN; spice instantiates `LATCH` |
| PHYSICAL-CPU-006 | `hw/adder/` schematic text includes `a`, `b`, `cin`, `sum`, `cout` |
| PHYSICAL-CPU-007 | `ngspice -b` on the adder test `.cir`: 8 `a,b,cin` rows; sum/cout at VOL ≤ 0.3 V / VOH ≥ 3.0 V |
