# cpu m2 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3.

```bash
python3 -m unittest compiler.tests.test_cpu_m1 compiler.tests.test_cpu_m2 -v
```

Expected: `Ran 19 tests ... OK`

m2 only:

```bash
python3 -m unittest compiler.tests.test_cpu_m2 -v
```

Expected: `Ran 7 tests ... OK`

## CPU-008 — logic

```bash
python3 -m unittest compiler.tests.test_cpu_m2.TestCpuM2.test_CPU_008
```

`and t0, ones, one` → 1, `Z=0`; `xor t0, one, one` → 0, `Z=1`; `C=V=0`.

## CPU-009 — shifter

```bash
python3 -m unittest compiler.tests.test_cpu_m2.TestCpuM2.test_CPU_009
```

`sll t0, one, 1` → 2; C is the bit shifted out (`0`). `sra` of `ones` stays negative.

## CPU-010 — compares

```bash
python3 -m unittest compiler.tests.test_cpu_m2.TestCpuM2.test_CPU_010
```

`cmp one, one` → `Z=1`, `t0` unchanged; `test one, zero` → `Z=1`.

## CPU-011 — MUL/DIV

```bash
python3 -m unittest compiler.tests.test_cpu_m2.TestCpuM2.test_CPU_011
```

`mul t0, one, one` → 1; `div t0, one, zero` → `t0==0`, `Z=1`.

## CPU-012 — immediates / LUI

```bash
python3 -m unittest compiler.tests.test_cpu_m2.TestCpuM2.test_CPU_012
```

`addi t0, one, -1` → 0, `Z=1`; `andi t0, ones, 0xFF` → `0xFF`; `lui t0, 1` → `0x10000`.

## CPU-013 — ADR

```bash
python3 -m unittest compiler.tests.test_cpu_m2.TestCpuM2.test_CPU_013
```

`adr t0, 4` at `PC=0` then halt → `t0==8`.

## CPU-032 — RF split cycles

```bash
python3 -m unittest compiler.tests.test_cpu_m2.TestCpuM2.test_CPU_032
```

`add t0, t0, one; halt` uses fewer cycles than `add s0, s0, one; halt`.
