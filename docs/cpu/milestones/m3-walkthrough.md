# cpu m3 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3.

```bash
python3 -m unittest compiler.tests.test_cpu_m1 compiler.tests.test_cpu_m2 compiler.tests.test_cpu_m3 -v
```

Expected: `Ran 23 tests ... OK`

m3 only:

```bash
python3 -m unittest compiler.tests.test_cpu_m3 -v
```

Expected: `Ran 4 tests ... OK`

## CPU-014 — load/store address and LE sizes

```bash
python3 -m unittest compiler.tests.test_cpu_m3.TestCpuM3.test_CPU_014
```

`sw`/`lw` of `0xA1B2C3D4` at 16. `sb`/`lbu` of `0x5A` at 20. `sw` at `4(t1)` with `t1=8` lands at address 12.

## CPU-015 — memory port bytes

```bash
python3 -m unittest compiler.tests.test_cpu_m3.TestCpuM3.test_CPU_015
```

`lui`+`ori` `t0=0x12345678`; `sw t0, 0(zero)`; halt; SRAM `0:4` is `78 56 34 12`.

## CPU-026 — user window

```bash
python3 -m unittest compiler.tests.test_cpu_m3.TestCpuM3.test_CPU_026
```

`p=0`, window `[0x1000,0x8000)`, `lw` at 0 → `CAUSE==2`; word at 0 still 0.

## CPU-027 — load/store align

```bash
python3 -m unittest compiler.tests.test_cpu_m3.TestCpuM3.test_CPU_027
```

`lw t0, 1(zero)` → `CAUSE==8`. `sw` to 1 with `t0=0xFFFFFFFF` leaves `mem[0:4]` unchanged.
