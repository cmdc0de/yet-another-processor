# physical-cpu m1 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| PHYSICAL-CPU-001 | `hw/` contains at least one `.kicad_sch` |
| PHYSICAL-CPU-002 | That schematic (or its spice view) instantiates `LATCH` / describes the CELL latch |
| PHYSICAL-CPU-003 | Schematic text includes nets `D`, `EN`, `Q`, `VDD`, `VSS` |
| PHYSICAL-CPU-004 | `ngspice -b` on the latch test `.cir`: follow D=0 then D=3.3 at EN=1; hold after EN=0 (same VOL ≤ 0.3 V / VOH ≥ 3.0 V as cells) |
