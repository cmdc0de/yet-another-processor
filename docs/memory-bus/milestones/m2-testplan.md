# memory-bus m2 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| MEMORY-BUS-003 | With `re=0` and `we=0`, `DQ` is `z`; during `we` the CPU side is not `z`; during `re` (after `LAT_MEM=1`) SRAM data appears on `DQ` |
| MEMORY-BUS-004 | After a word `0xA5A5A5A5` at addr 0: byte store `size=1` `wdata=0x0000005A` at addr 0 leaves bytes 1–3 `A5`; half store `size=2` at addr 2 does not change bytes 0–1 |
| MEMORY-BUS-005 | On a store, `ce_n=0`, `we_n=0`, `oe_n=1`; on a load, `ce_n=0`, `oe_n=0`, `we_n=1`; idle all three are 1 |
