# emu-rust m3 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| EMU-RUST-016 | `sll t0, one, 3` then `srl t0, t0, 2` → `t0==2`. `srlv t0, t0, one` → 1. `lui t0, 0x8000` then `sra t0, t0, 1` → `0xC0000000`, N=1. `srav t0, t0, one` → `0xE0000000`. `sllv t0, one, t1` with `t1==3` → 8. |
| EMU-RUST-017 | `addi t0, one, -1` → 0, Z=1. `andi t0, ones, 0x00FF` → `0xFF`. `ori t0, zero, 1` → 1. `xori t0, ones, 0` → `0xFFFFFFFF`. |
| EMU-RUST-018 | `lui t0, 0x1234` → `0x12340000`, FLAGS unchanged. `ori t0, t0, 0x5678` → `0x12345678`. `PC=0`, `adr t0, 16` → `t0==20`. |
| EMU-RUST-019 | `mul t0, one, ones` → `0xFFFFFFFF`. `mul t0, ones, ones` → 1. `div t0, ones, one` → `0xFFFFFFFF`. `div t0, ones, zero` → 0, Z=1. |
