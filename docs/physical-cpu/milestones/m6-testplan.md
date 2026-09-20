# physical-cpu m6 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| PHYSICAL-CPU-011 | `hw/rf-mosfet/` spice instantiates `LATCH` 13 times (`r3`–`r15`) and a read mux (`MUX2` or `TG`); schematic text includes `we3`, `we15`, `qa`, `qb`, `LAT=1`. `ngspice -b`: load `r3`=1 and `r4`=0; after all `we*`=0, `ra3`/`rb4` select `qa` at VOH ≥ 3.0 V and `qb` at VOL ≤ 0.3 V. |
