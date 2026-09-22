# fpu m1 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| FPU-001 | `fpu/` contains Verilog-2001 `.v` files |
| FPU-002 | `iverilog` + `vvp` of the FPU sim exits 0 |
| FPU-003 | Tests fail if `iverilog` or `vvp` is not on `PATH` |
| FPU-004 | Sources name IEEE-754 binary32 (or `binary32`) |
| FPU-005 | After reset, dumped `f0`–`f31` are 32 words of `0` |
