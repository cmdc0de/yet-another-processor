# emu-rust m4 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| EMU-RUST-012 | `add` at PC=0 → PC==4. Step with `PC=1` → CAUSE=8 and PC==0x80. |
| EMU-RUST-020 | Bytes `[0x78,0x56,0x34,0x12]` at 0; `lw t0, 0(zero)` → `0x12345678`. `sw` of that word writes `78 56 34 12`. `lb` of `0xFF` → `0xFFFFFFFF`; `lbu` → `0xFF`. `lh`/`lhu`/`sb`/`sh` as ISA-020–023. Unaligned `lw` at 1 → CAUSE=8. |
| EMU-RUST-021 | PC=0, `j` to 0x20 → PC==0x20. `jal` to 0x20 → `ra==4`, PC==0x20. `jr ra` after that → PC==4. `jalr t0, t1` with t1==0x40 → t0==PC+4, PC==0x40. |
| EMU-RUST-022 | `cmp one, one` then `beq 0x20` → PC==0x20. `cmp one, zero` then `beq 0x20` → PC==8. `test one, one` then `bne 0x20` taken. `cmp zero, one` then `blo 0x20` taken. |
