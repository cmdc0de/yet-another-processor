# fpu m3 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

R-type: `rd|rs|rt|shamt|funct` = `fd|16|fs|ft|funct`. Opcode `010001`.

| ID | Check |
|----|--------|
| FPU-010 | `add.s f1, f2, f3` word has opcode COP1, `rs=16`, `fd=1`, `fs=2`, `ft=3`, `funct=0`. `sub.s`/`mul.s`/`div.s` use `funct` 1/2/3. |
| FPU-011 | YAP1: user `mtc1` `f0=0xA5A5A5A5`, `SYS_WRITE`, `mfc1 f0`, `SYS_EXIT`. After halt, that GPR is `0xA5A5A5A5`. Kernel trap dirties `f0` before restore. `yap-emu` exits 0. |
