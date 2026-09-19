# os m2 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

`SYS_EXIT` is choice **A**: trap saves GPRs, then `halt` without restoring kernel `sp`.

| ID | Check |
|----|--------|
| OS-004 | After `yap-emu` halt, dump `ubase` is `00001000` and `ulimit` is `00008000`. |
| OS-005 | Payload at `0x1000` is the user `sys 1` word. |
| OS-007 | Payload at 0 is not a lone `halt`; `0x1000` is `sys` with imm16=1. |
| OS-008 | After halt, dump `r4` is `00008000`. |
| OS-009 | After halt, kernel stack (addresses below `0x1000`) contains the word `0x8000` (saved user `sp`). |
| OS-010 | `sys 1` from user results in halt (exit 0), not an infinite loop at `0x80`. |
| OS-013 | Assembled user `sys 1` has opcode SYS and imm16=1. |
| OS-014 | `yap-emu` on the image exits 0. |
