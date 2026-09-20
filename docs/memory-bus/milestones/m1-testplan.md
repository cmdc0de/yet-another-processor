# memory-bus m1 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| MEMORY-BUS-001 | After `we` (or `re`) on clock 0, write data is committed / `rdata` valid on clock 1, not combinational on clock 0 |
| MEMORY-BUS-002 | Bench drives `addr[31:0]`, `size` 1/2/4, `re`, `we` as in `docs/memory-bus/design.md` |
| MEMORY-BUS-006 | `hw/bus/` contains Verilog-2001 sources |
| MEMORY-BUS-007 | Store word `0xA5A5A5A5` at an aligned address; load word returns `0xA5A5A5A5` |
| MEMORY-BUS-008 | Tests fail if `iverilog` or `vvp` is not on `PATH` |
| MEMORY-BUS-009 | HDL or sim sources state VDD=3.3 (no 5 V SRAM model) |
