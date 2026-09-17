# ISA m4 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Python 3 stdlib only (`unittest`).

Run m1–m4:

```bash
python3 -m unittest compiler.tests.test_m1 compiler.tests.test_m2 compiler.tests.test_m3 compiler.tests.test_m4 -v
```

Expected: `Ran 39 tests ... OK`

m4 only:

```bash
python3 -m unittest compiler.tests.test_m4 -v
```

Expected: `Ran 2 tests ... OK`

## ISA-030 — Bcc

```bash
python3 -m unittest compiler.tests.test_m4.TestM4.test_ISA_030
```

`cmp one, one` then `beq 0x20` taken (`PC==0x20`). `cmp one, zero` then `beq 0x20` not taken (`PC==8`). `test one, one` then `bne 0x20` taken (odd). `cmp zero, one` then `blo` taken, `bhs` not taken. opcode=Bcc.

Odd/even: `test rs, one` then `bne` (odd) or `beq` (even).

## ISA-032 — HALT

```bash
python3 -m unittest compiler.tests.test_m4.TestM4.test_ISA_032
```

`halt` funct=HALT. After step, `halted` is true; GPRs unchanged; further `step` is a no-op.
