# ISA m6 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Python 3 stdlib only (`unittest`).

Run m1–m6:

```bash
python3 -m unittest compiler.tests.test_m1 compiler.tests.test_m2 compiler.tests.test_m3 compiler.tests.test_m4 compiler.tests.test_m5 compiler.tests.test_m6 -v
```

Expected: `Ran 56 tests ... OK`

m6 only:

```bash
python3 -m unittest compiler.tests.test_m6 -v
```

Expected: `Ran 6 tests ... OK`

## ISA-043 — COP1 opcode

```bash
python3 -m unittest compiler.tests.test_m6.TestM6.test_ISA_043
```

Packed `mfc1` opcode is COP1 (`010001`), not SPECIAL or COP0.

## ISA-044 — MFC1 / MTC1

```bash
python3 -m unittest compiler.tests.test_m6.TestM6.test_ISA_044
```

`mtc1 t0, f0` then `mfc1 t1, f0` copies the value. `f0` is not a GPR.

## ISA-045 — unimplemented COP1

```bash
python3 -m unittest compiler.tests.test_m6.TestM6.test_ISA_045
```

Non-move COP1 traps CAUSE=6, PC=0x80.

## ISA-046 — sp

```bash
python3 -m unittest compiler.tests.test_m6.TestM6.test_ISA_046
```

`sp` is r4 and writable; `zero`/`one`/`ones` still discard writes.

## ISA-047 — stack down, 8-byte call align

```bash
python3 -m unittest compiler.tests.test_m6.TestM6.test_ISA_047
```

`sp=0x200`, two word pushes → `sp==0x1F8`, aligned, addresses decrease.

## ISA-048 — ABI map

```bash
python3 -m unittest compiler.tests.test_m6.TestM6.test_ISA_048
```

`ra=3, a0=5, a3=8, s0=16, s11=27, fp=30, k0=31`. `k0` is not in the user C set.
