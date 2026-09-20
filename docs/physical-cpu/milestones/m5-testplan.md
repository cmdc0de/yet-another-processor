# physical-cpu m5 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| PHYSICAL-CPU-010 | `hw/wired/` schematic text includes `r0_0`, `r1_0`, `r2_31`; spice does not instantiate `LATCH`; `ngspice -b`: every `r0_*` at VOL ≤ 0.3 V; `r1_0` at VOH ≥ 3.0 V and `r1_1`–`r1_31` at VOL; every `r2_*` at VOH. |
