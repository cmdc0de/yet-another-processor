# ISA m4 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| ISA-030 | `PC=0`, `cmp one, one` then `beq 0x20` → taken, `PC==0x20`. `cmp one, zero` then `beq 0x20` → not taken, `PC==8` (cmp +4, beq +4). `test one, one` then `bne 0x20` → taken (odd). `cmp zero, one` then `blo 0x20` taken; `bhs 0x20` not taken. opcode=Bcc. |
| ISA-032 | `halt` funct=HALT. After step, `halted` is true; GPRs unchanged. |

Assembler names for the conds: `beq` EQ, `bne` NE, `blt` LT, `bge` GE, `blo` LO, `bhs` HS, `ble` LE, `bgt` GT, `bmi` MI, `bpl` PL.
