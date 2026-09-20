# physical-cpu m7 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| PHYSICAL-CPU-012 | `hw/rf-ic/` spice instantiates 16 IC storage bits (`r16`–`r31`) and does **not** instantiate `LATCH` as those bits; schematic text includes `we16`, `we31`, `qa`, `qb`, `LAT=2`. `ngspice -b`: load `r16`=1 and `r17`=0; after all `we*`=0, `ra16`/`rb17` select `qa` at VOH ≥ 3.0 V and `qb` at VOL ≤ 0.3 V. |
