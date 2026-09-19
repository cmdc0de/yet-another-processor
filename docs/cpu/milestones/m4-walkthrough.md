# cpu m4 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3.

```bash
python3 -m unittest compiler.tests.test_cpu_m1 compiler.tests.test_cpu_m2 compiler.tests.test_cpu_m3 compiler.tests.test_cpu_m4 -v
```

Expected: `Ran 32 tests ... OK`

m4 only:

```bash
python3 -m unittest compiler.tests.test_cpu_m4 -v
```

Expected: `Ran 9 tests ... OK`

## CPU-016 — CSR file

```bash
python3 -m unittest compiler.tests.test_cpu_m4.TestCpuM4.test_CPU_016
```

`mtc0`/`mfc0` UBASE: `t1==0x1000`.

## CPU-017 — COP1 moves

```bash
python3 -m unittest compiler.tests.test_cpu_m4.TestCpuM4.test_CPU_017
```

`mtc1 t0, f0` then `mfc1 t1, f0` → `t1==0xA5A5A5A5`.

## CPU-020 — control word steers CSRs

```bash
python3 -m unittest compiler.tests.test_cpu_m4.TestCpuM4.test_CPU_020
```

After unaligned `lw`, `mfc0 t1, cause` at `0x80` → `t1==8`.

## CPU-024 — SYS EPC

```bash
python3 -m unittest compiler.tests.test_cpu_m4.TestCpuM4.test_CPU_024
```

`sys 1` at 0, halt at `0x80` → `CAUSE==3`, `EPC==4`.

## CPU-025 — ERET

```bash
python3 -m unittest compiler.tests.test_cpu_m4.TestCpuM4.test_CPU_025
```

EPC=`0x80`, supervisor `ERET` → halted at `0x80`.

## CPU-028 — user ERET

```bash
python3 -m unittest compiler.tests.test_cpu_m4.TestCpuM4.test_CPU_028
```

`p=0`; `eret` → `CAUSE==7`.

## CPU-029 — TE trap

```bash
python3 -m unittest compiler.tests.test_cpu_m4.TestCpuM4.test_CPU_029
```

`mtc0` STATUS with TE=1 → `CAUSE==7`, `te==0`.

## CPU-030 — IRQ

```bash
python3 -m unittest compiler.tests.test_cpu_m4.TestCpuM4.test_CPU_030
```

`IE=1`, `irq()`, halt at 0 and `0x80` → `CAUSE==1`.

## CPU-031 — unimplemented COP1

```bash
python3 -m unittest compiler.tests.test_cpu_m4.TestCpuM4.test_CPU_031
```

COP1 word `0x44100000` → `CAUSE==6`.
