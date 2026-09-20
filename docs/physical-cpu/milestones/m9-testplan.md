# physical-cpu m9 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| PHYSICAL-CPU-014 | `hw/memport/` schematic text includes `addr0`, `addr31`, `wdata0`, `rdata0`, `sz0`, `re`, `we`, `LAT_MEM=1`. `ngspice -b`: `sz=word`, `we` writes `wdata` with bit0=1 and bit1=0; after one `clk`, `re` yields `rdata0` at VOH ≥ 3.0 V and `rdata1` at VOL ≤ 0.3 V. |
