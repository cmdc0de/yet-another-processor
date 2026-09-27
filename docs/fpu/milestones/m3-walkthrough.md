# FPU coprocessor m3 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3. FPU-011 also needs `yap-emu` (or a cargo build of `emu/rust`).

```bash
python3 -m unittest compiler.tests.test_fpu_m3 compiler.tests.test_fpu_m2 compiler.tests.test_fpu_m1 -v
```

Expected: `Ran 11 tests ... OK`. m1–m2 still pass.

## FPU-010 — assembler encodings

```bash
python3 -m unittest compiler.tests.test_fpu_m3.TestFpuM3.test_FPU_010
```

`add.s f1, f2, f3` word has opcode COP1, `rs=16`, `fd=1`, `fs=2`, `ft=3`, `funct=0`. `sub.s`/`mul.s`/`div.s` use `funct` 1/2/3.

## FPU-011 — kernel FP save/restore

```bash
python3 -m unittest compiler.tests.test_fpu_m3.TestFpuM3.test_FPU_011
```

User `mtc1` `f0=0xA5A5A5A5`, `SYS_WRITE`, `mfc1 f0` into `t1`, `SYS_EXIT`. After halt `t1` (`r11`) is `0xA5A5A5A5`. Kernel trap dirties `f0` before restore. `yap-emu` exits 0.
