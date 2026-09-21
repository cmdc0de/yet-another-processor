# mcu m1 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| MCU-001 | `hw/mcu/` contains Verilog-2001 `.v` files |
| MCU-002 | `iverilog` + `vvp` of the MCU sim exits 0 |
| MCU-003 | Tests fail if `iverilog` or `vvp` is not on `PATH` |
| MCU-004 | Bench drives `clk`, `rst`, `we`, `re`, `addr[7:0]`, `wdata[31:0]`, `rdata[31:0]` as in `docs/mcu/design.md` |
| MCU-005 | Sources name STATUS 0x00, KEY_DATA 0x04, SER_DATA 0x08, STOR_LBA 0x0C, STOR_IDX 0x10, STOR_DATA 0x14, STOR_CMD 0x18 |
| MCU-006 | After reset, a STATUS read (offset 0x00) returns 0 |
| MCU-011 | HDL or sim sources state VDD=3.3 (no 5 V MCU model) |
