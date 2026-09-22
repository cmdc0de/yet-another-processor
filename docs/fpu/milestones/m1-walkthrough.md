# FPU coprocessor m1 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and **Icarus Verilog** (`iverilog`, `vvp` on `PATH`).

```bash
python3 -m unittest compiler.tests.test_fpu_m1 -v
```

Expected: `Ran 5 tests ... OK`.

## FPU-001 — HDL tree

```bash
python3 -m unittest compiler.tests.test_fpu_m1.TestFpuM1.test_FPU_001
```

`fpu/` contains Verilog-2001 `.v` files.

## FPU-002 — sim runs

```bash
python3 -m unittest compiler.tests.test_fpu_m1.TestFpuM1.test_FPU_002
```

`iverilog` + `vvp` of the FPU sim exits 0.

## FPU-003 — Icarus required

```bash
python3 -m unittest compiler.tests.test_fpu_m1.TestFpuM1.test_FPU_003
```

Fails if `iverilog` or `vvp` is not on `PATH`.

## FPU-004 — binary32

```bash
python3 -m unittest compiler.tests.test_fpu_m1.TestFpuM1.test_FPU_004
```

Sources name IEEE-754 binary32.

## FPU-005 — reset zeros

```bash
python3 -m unittest compiler.tests.test_fpu_m1.TestFpuM1.test_FPU_005
```

After reset, dumped `f0`–`f31` are 32 words of `0`.
