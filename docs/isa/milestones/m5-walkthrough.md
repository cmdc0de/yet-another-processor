# ISA m5 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Python 3 stdlib only (`unittest`).

Run m1–m5:

```bash
python3 -m unittest compiler.tests.test_m1 compiler.tests.test_m2 compiler.tests.test_m3 compiler.tests.test_m4 compiler.tests.test_m5 -v
```

Expected: `Ran 50 tests ... OK`

m5 only:

```bash
python3 -m unittest compiler.tests.test_m5 -v
```

Expected: `Ran 11 tests ... OK`

## ISA-033 — privilege bit

```bash
python3 -m unittest compiler.tests.test_m5.TestM5.test_ISA_033
```

Reset: P=1, IE=0, PC=0. `mtc0 zero, status` → user (P=0).

## ISA-034 — supervisor-only

```bash
python3 -m unittest compiler.tests.test_m5.TestM5.test_ISA_034
```

User `mtc0` / `eret` → CAUSE=7. Supervisor `mtc0` UBASE succeeds.

## ISA-035 — trap entry

```bash
python3 -m unittest compiler.tests.test_m5.TestM5.test_ISA_035
```

`sys 1` from PC=0: CAUSE=3, EPC=4, P=1, IE=0, PC=0x80.

## ISA-036 — ERET

```bash
python3 -m unittest compiler.tests.test_m5.TestM5.test_ISA_036
```

After `sys 1`, `eret` → PC=4, P restored.

## ISA-037 — base/limit

```bash
python3 -m unittest compiler.tests.test_m5.TestM5.test_ISA_037
```

UBASE=0x100, ULIMIT=0x200: user `lw` at 0 faults; supervisor `lw` at 0 succeeds.

## ISA-038 — protection cause

```bash
python3 -m unittest compiler.tests.test_m5.TestM5.test_ISA_038
```

That user fault is CAUSE=2, PC=0x80.

## ISA-039 — IE

```bash
python3 -m unittest compiler.tests.test_m5.TestM5.test_ISA_039
```

IE=0: `cpu.irq()` does not trap. IE=1: traps.

## ISA-040 — IRQ cause

```bash
python3 -m unittest compiler.tests.test_m5.TestM5.test_ISA_040
```

IRQ trap is CAUSE=1.

## ISA-041 — reserved VM causes

```bash
python3 -m unittest compiler.tests.test_m5.TestM5.test_ISA_041
```

CAUSE translation-miss=4, page-fault=5.

## ISA-042 — TE reserved

```bash
python3 -m unittest compiler.tests.test_m5.TestM5.test_ISA_042
```

`mtc0` STATUS with TE=1 → CAUSE=7; TE stays 0.

## ISA-049 — SYS

```bash
python3 -m unittest compiler.tests.test_m5.TestM5.test_ISA_049
```

`sys 0x12` opcode=SYS, imm16=0x12, CAUSE=3, a0–a3 untouched.
