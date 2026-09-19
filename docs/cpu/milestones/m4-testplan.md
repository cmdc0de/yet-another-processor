# cpu m4 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| CPU-016 | `li t0, 0x1000`; `mtc0 t0, ubase`; `mfc0 t1, ubase`; halt → `t1==0x1000` |
| CPU-017 | `li t0, 0xA5A5A5A5`; `mtc1 t0, f0`; `mfc1 t1, f0`; halt → `t1==0xA5A5A5A5` |
| CPU-020 | `lw t0, 1(zero)` then at `0x80`: `mfc0 t1, cause`; halt → `t1==8` |
| CPU-024 | `sys 1` at 0, halt at `0x80` → `CAUSE==3`, `EPC==4` |
| CPU-025 | Set EPC=`0x80` (halt there) and STATUS for supervisor `ERET`; `eret` → halted at `0x80` |
| CPU-028 | `p=0`; `eret` at 0; halt at `0x80` → `CAUSE==7` |
| CPU-029 | `mtc0` STATUS=`4` (TE=1); halt at `0x80` → `CAUSE==7`, `cpu.te==0` |
| CPU-030 | STATUS `IE=1`; `irq()`; `halt` at 0 and at `0x80` → `CAUSE==1` (insn at 0 not executed as halt before trap) |
| CPU-031 | `.word 0x44100000` (COP1, `rs≠0,4`); halt at `0x80` → `CAUSE==6` |
