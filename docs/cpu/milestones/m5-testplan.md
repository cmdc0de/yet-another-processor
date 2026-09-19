# cpu m5 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| CPU-039 | `j 0x20` at 0; `halt` at `0x20` → halted, `PC==0x20` |
| CPU-040 | `jal 0x20` at 0; `halt` at `0x20` → `ra==4`, `PC==0x20` |
| CPU-041 | `addi t0, zero, 0x20`; `jr t0`; `halt` at `0x20` → `PC==0x20` |
| CPU-042 | `addi t0, zero, 0x20`; `jalr t1, t0`; `halt` at `0x20` → `t1==8`, `PC==0x20` |
| CPU-043 | `cmp one, one`; `beq 0x20`; halt at `0x20` → `PC==0x20`. `cmp one, zero`; `beq 0x20`; halt at 8 → `PC==8`. `cmp zero, one`; `blo 0x20` taken; `bhs 0x20` not taken |
