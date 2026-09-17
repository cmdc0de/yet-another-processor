# Assembler m3 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| COMPILER-012 | `.word 0x12345678` payload `78 56 34 12`. `.byte 1 2`. `.half 0x80FF` → `FF 80`. `.word` at LC=2 (after one `.half` without align) is an error. |
| COMPILER-013 | `.byte 1` / `.align 2` / `.word 0` — `LC` of the word is 4; bytes 1–3 are 0. |
| COMPILER-014 | `.equ N, 4` / `lw t0, N(sp)` — `imm16==4`. `.equ N, 1` twice is an error. |
