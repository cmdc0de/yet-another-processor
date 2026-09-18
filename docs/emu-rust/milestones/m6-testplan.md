# emu-rust m6 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| EMU-RUST-033 | Packed `mfc1` opcode is COP1 (`010001`). `mtc1 t0, f0` then `mfc1 t1, f0` copies the value. Writing `f0` does not change `r0`–`r31` except the intended GPR on `mfc1`. |
| EMU-RUST-034 | COP1 word with a non-move `rs` traps CAUSE=6, PC=0x80. |
