# cpu m5 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3.

```bash
python3 -m unittest compiler.tests.test_cpu_m1 compiler.tests.test_cpu_m2 compiler.tests.test_cpu_m3 compiler.tests.test_cpu_m4 compiler.tests.test_cpu_m5 -v
```

Expected: `Ran 37 tests ... OK`

m5 only:

```bash
python3 -m unittest compiler.tests.test_cpu_m5 -v
```

Expected: `Ran 5 tests ... OK`

## CPU-039 — `j`

```bash
python3 -m unittest compiler.tests.test_cpu_m5.TestCpuM5.test_CPU_039
```

`j 0x20` at 0; `halt` at `0x20` → halted, `PC==0x20`.

## CPU-040 — `jal`

```bash
python3 -m unittest compiler.tests.test_cpu_m5.TestCpuM5.test_CPU_040
```

`jal 0x20` at 0; `halt` at `0x20` → `ra==4`, `PC==0x20`.

## CPU-041 — `jr`

```bash
python3 -m unittest compiler.tests.test_cpu_m5.TestCpuM5.test_CPU_041
```

`addi t0, zero, 0x20`; `jr t0`; `halt` at `0x20` → `PC==0x20`.

## CPU-042 — `jalr`

```bash
python3 -m unittest compiler.tests.test_cpu_m5.TestCpuM5.test_CPU_042
```

`addi t0, zero, 0x20`; `jalr t1, t0`; `halt` at `0x20` → `t1==8`, `PC==0x20`.

## CPU-043 — `bcc`

```bash
python3 -m unittest compiler.tests.test_cpu_m5.TestCpuM5.test_CPU_043
```

`cmp one, one`; `beq 0x20` → `PC==0x20`. `cmp one, zero`; `beq 0x20`; halt at 8 → `PC==8`. `blo` taken; `bhs` not taken after `cmp zero, one`.
