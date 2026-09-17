# ISA m3 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| ISA-017 | `div t0, ones, one` → `0xFFFFFFFF`. `div t0, ones, zero` → `t0==0`, Z=1. funct=DIV. |
| ISA-018 | Bytes `[0x78,0x56,0x34,0x12]` at 0; `lw t0, 0(zero)` → `0x12345678`. opcode=LW. |
| ISA-019 | `t0=0x12345678`; `sw t0, 0(zero)`; memory bytes `78 56 34 12`. |
| ISA-020 | Byte `0xFF` at 0; `lb` → `0xFFFFFFFF`; `lbu` → `0xFF`. |
| ISA-021 | `sb one, 4(zero)`; memory[4]==1; neighbors unchanged. |
| ISA-022 | Half `0x80FF` LE at 8; `lh` → `0xFFFF80FF`; `lhu` → `0x80FF`. |
| ISA-023 | `sh` of `0x80FF` at 8 writes `FF 80`. |
| ISA-024 | Word round-trip LE; byte 0 is `0x78`. Unaligned `lw` at 1 → CAUSE=8. |
| ISA-027 | `PC=0`, `j` to `0x20` → `PC==0x20`. opcode=J. GPRs unchanged. |
| ISA-028 | `PC=0`, `jal` to `0x20` → `ra==4`, `PC==0x20`. opcode=JAL. |
| ISA-029 | `jal` to `0x20` then `jr ra` → `PC==4`. `jalr t0, t1` with `t1==0x40` → `t0==PC+4`, `PC==0x40`. funct=JR / JALR. |
