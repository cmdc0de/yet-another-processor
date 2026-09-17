# Assembler m1 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| COMPILER-001 | Assemble `nop` + `halt` → file longer than 16 bytes; payload is two instructions. |
| COMPILER-002 | Missing `-o` exits non-zero. With `-o out.yap`, that path exists after success. |
| COMPILER-003 | Three `nop`s → `size==12`; payload is three identical `nop` words. |
| COMPILER-023 | First 4 bytes `YAP1`; `load==0`, `entry==0`, `size==len(file)-16`. |
| COMPILER-004 | `nop ; hi` and `nop # hi` produce the same payload as `nop`. |
| COMPILER-005 | `ADD t0, one, one` payload equals `add t0, one, one`. |
| COMPILER-006 | `add sp, zero, one` encodes `rd=4`. |
| COMPILER-007 | `lw t0, 4(sp)` encodes opcode LW, `rs=sp`, `imm=4`. |
| COMPILER-018 | Error on line 3 prints `...:3:`; `-o` path is absent. |
| COMPILER-019 | `blorp t0, t0` is an error. |
