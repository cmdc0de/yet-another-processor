# gpu m1 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| GPU-001 | `gpu/` contains Verilog-2001 `.v` files |
| GPU-002 | `iverilog` + `vvp` of the GPU sim exits 0 |
| GPU-003 | Tests fail if `iverilog` or `vvp` is not on `PATH` |
| GPU-004 | RTL stores pixels in a GPU-local array (not a CPU SRAM module) |
| GPU-005 | Sources or PPM state 160×120 and RGB888 (`0x00RRGGBB` / P6) |
| GPU-006 | PPM P6 dump is 160×120 and every pixel is `00 00 00` after reset |
