# FPU coprocessor m2 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and **Icarus Verilog** (`iverilog`, `vvp` on `PATH`).

```bash
python3 -m unittest compiler.tests.test_fpu_m2 compiler.tests.test_fpu_m1 -v
```

Expected: `Ran 9 tests ... OK`. m1 still passes.

## FPU-006 — add.s

```bash
python3 -m unittest compiler.tests.test_fpu_m2.TestFpuM2.test_FPU_006
```

`f2=1.0`, `f3=2.0`, add (`funct=0`) into `f1` → `f1=0x40400000`.

## FPU-007 — sub.s

```bash
python3 -m unittest compiler.tests.test_fpu_m2.TestFpuM2.test_FPU_007
```

`f2=1.0`, `f3=0.5`, sub (`funct=1`) into `f1` → `f1=0x3F000000`.

## FPU-008 — mul.s

```bash
python3 -m unittest compiler.tests.test_fpu_m2.TestFpuM2.test_FPU_008
```

`f2=2.0`, `f3=3.0`, mul (`funct=2`) into `f1` → `f1=0x40C00000`.

## FPU-009 — div.s

```bash
python3 -m unittest compiler.tests.test_fpu_m2.TestFpuM2.test_FPU_009
```

`1.0÷2.0` → `0x3F000000`; `1.0÷0.0` → `0x7F800000`; `0.0÷0.0` → `0x7FC00000`.
