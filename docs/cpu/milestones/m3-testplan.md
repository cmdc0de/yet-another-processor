# cpu m3 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| CPU-014 | Store `0xA1B2C3D4` with `sw` at 16, `lw` back → `t0==0xA1B2C3D4`. `sb` of `0x5A` at 20, `lbu` → `0x5A`. Offset: `sw` at `4(t1)` with `t1=8` lands at address 12 |
| CPU-015 | `lui`+`ori` `t0=0x12345678`; `sw t0, 0(zero)`; halt; `mem[0:4]==bytes([0x78,0x56,0x34,0x12])` |
| CPU-026 | `p=0`, window `[0x1000,0x8000)`, `lw t0, 0(zero)`, `halt` at `0x80` → `CAUSE==2`; word at 0 still 0 |
| CPU-027 | `lw t0, 1(zero)` → `CAUSE==8`. `sw t0, 1(zero)` with `t0=0xFFFFFFFF` leaves `mem[0:4]` unchanged |
