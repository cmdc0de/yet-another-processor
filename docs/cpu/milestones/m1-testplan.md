# cpu m1 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| CPU-001 | `add t0, one, one` then `halt`: `t0` and `PC` fit in 32 bits (`t0==2`) |
| CPU-002 | same image: after halt, `PC` equals the address of the `halt` insn (`4` if `add` is 4 bytes at 0) |
| CPU-003 | `halt` at 0: after the model has fetched, `IR ==` halt encoding |
| CPU-004 | `add t0, one, one`; `add s0, t0, one`; halt → `t0==2`, `s0==3` |
| CPU-005 | `add zero, one, one`; halt → `r0==0`; `Z==0` |
| CPU-006 | `add t0, one, one`; halt → flags `(Z,N,C,V)==(0,0,0,0)`; FLAGS is not `r0`–`r31` |
| CPU-007 | `add t0, one, one` → 2; then a second image `sub t0, one, one` → `t0==0`, `Z=1` |
| CPU-018 | `halt` at 0: cycle count at halt `> 1` |
| CPU-019 | `halt`-only image stops; `add`+`halt` image has `t0==2` (not treated as halt) |
| CPU-021 | `PC=1`, `halt` at `0x80`: `CAUSE==8`; aligned `halt` at 0 does not set CAUSE=8 |
| CPU-022 | after halt, `step()` leaves `PC` and `halted` unchanged |
| CPU-023 | `PC=1`, `halt` at `0x80`: `CAUSE==8`, `P==1`, `IE==0`, `EPC==1`, `PC==0x80`, then halt |
