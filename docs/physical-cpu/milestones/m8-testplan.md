# physical-cpu m8 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| PHYSICAL-CPU-013 | `hw/ucode/` schematic text includes `upc0`, `upc7`, `cw0`, `cw63`, `256×64` (or `256x64`). Spice does not use `LATCH` as the ROM. `ngspice -b`: after reset, `upc*` at VOL and `cw2..cw0` at VOL (NEXT); after one `clk`, `upc0` at VOH and `upc1`–`upc7` at VOL; `cw0`–`cw2` then match ROM[1] at VOL/VOH and differ from ROM[0]. |
