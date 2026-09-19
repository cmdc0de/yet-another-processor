# cpu m1 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3.

```bash
python3 -m unittest compiler.tests.test_cpu_m1 -v
```

Expected: `Ran 12 tests ... OK`

## CPU-001 — 32-bit datapath

```bash
python3 -m unittest compiler.tests.test_cpu_m1.TestCpuM1.test_CPU_001
```

`add t0, one, one` then `halt`: `t0==2`; `t0` and `PC` fit in 32 bits.

## CPU-002 — PC + 4

```bash
python3 -m unittest compiler.tests.test_cpu_m1.TestCpuM1.test_CPU_002
```

Same image: after halt, `PC==4` (address of the `halt` insn).

## CPU-003 — instruction register

```bash
python3 -m unittest compiler.tests.test_cpu_m1.TestCpuM1.test_CPU_003
```

`halt` at 0: after halt, `IR` equals the halt encoding.

## CPU-004 — split GPR file

```bash
python3 -m unittest compiler.tests.test_cpu_m1.TestCpuM1.test_CPU_004
```

`add t0, one, one` then `add s0, t0, one` then halt → `t0==2`, `s0==3`.

## CPU-005 — wired writes discarded

```bash
python3 -m unittest compiler.tests.test_cpu_m1.TestCpuM1.test_CPU_005
```

`add zero, one, one`; halt → `r0==0`; `Z==0`.

## CPU-006 — discrete FLAGS

```bash
python3 -m unittest compiler.tests.test_cpu_m1.TestCpuM1.test_CPU_006
```

`add t0, one, one`; halt → flags `(Z,N,C,V)==(0,0,0,0)`; FLAGS is not a GPR.

## CPU-007 — ADD/SUB

```bash
python3 -m unittest compiler.tests.test_cpu_m1.TestCpuM1.test_CPU_007
```

`add t0, one, one` → 2. `sub t0, one, one` → `t0==0`, `Z=1`.

## CPU-018 — multi-cycle

```bash
python3 -m unittest compiler.tests.test_cpu_m1.TestCpuM1.test_CPU_018
```

`halt` at 0: cycle count at halt `> 1`.

## CPU-019 — dispatch

```bash
python3 -m unittest compiler.tests.test_cpu_m1.TestCpuM1.test_CPU_019
```

`halt`-only image stops; `add`+`halt` image has `t0==2`.

## CPU-021 — fetch align

```bash
python3 -m unittest compiler.tests.test_cpu_m1.TestCpuM1.test_CPU_021
```

`PC=1`, `halt` at `0x80`: `CAUSE==8`. Aligned `halt` at 0 does not set CAUSE=8.

## CPU-022 — HALT holds

```bash
python3 -m unittest compiler.tests.test_cpu_m1.TestCpuM1.test_CPU_022
```

After halt, further `step()` leaves `PC` and `halted` unchanged.

## CPU-023 — trap sequence

```bash
python3 -m unittest compiler.tests.test_cpu_m1.TestCpuM1.test_CPU_023
```

`PC=1`, `halt` at `0x80`: `CAUSE==8`, `P==1`, `IE==0`, `EPC==1`, `PC==0x80`, then halt.
