# ISA m1 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Python 3 stdlib only (`unittest`).

Run all m1 checks:

```bash
python3 -m unittest compiler.tests.test_m1 -v
```

Expected: `Ran 19 tests ... OK`

Single-feature commands below. Each must exit 0.

## ISA-001 — 32-bit word and addresses

```bash
python3 -m unittest compiler.tests.test_m1.TestM1.test_ISA_001
```

Packed instruction is 4 bytes; `PC=0xFFFFFFFC` then one step wraps to `0`.

## ISA-002 — 32 GPRs, one file

```bash
python3 -m unittest compiler.tests.test_m1.TestM1.test_ISA_002
```

`r0`–`r31` readable; `r32` raises `ValueError`.

## ISA-003 — PC + 4

```bash
python3 -m unittest compiler.tests.test_m1.TestM1.test_ISA_003
```

After one R-type step, `PC` is old `PC+4`.

## ISA-004 — FLAGS Z N C V

```bash
python3 -m unittest compiler.tests.test_m1.TestM1.test_ISA_004
```

`add t0, ones, ones` → N=1 Z=0. `add zero, zero, zero` → Z=1 N=0. Signed overflow ADD `0x7FFFFFFF+1` sets V. `sub t1, zero, one` sets C (borrow).

Note: `add t0, one, ones` wraps to 0 (Z=1 C=1) per `design.md`; the test uses `ones, ones` for the N=1 case.

## ISA-005 — ADD

```bash
python3 -m unittest compiler.tests.test_m1.TestM1.test_ISA_005
```

`add t0, one, one` → `t0==2`; opcode=0, funct=ADD.

## ISA-006 — SUB

```bash
python3 -m unittest compiler.tests.test_m1.TestM1.test_ISA_006
```

`sub t0, one, one` → `t0==0`, Z=1.

## ISA-007 — AND

```bash
python3 -m unittest compiler.tests.test_m1.TestM1.test_ISA_007
```

`and t0, ones, one` → `t0==1`.

## ISA-008 — OR

```bash
python3 -m unittest compiler.tests.test_m1.TestM1.test_ISA_008
```

`or t0, zero, one` → `t0==1`.

## ISA-009 — XOR

```bash
python3 -m unittest compiler.tests.test_m1.TestM1.test_ISA_009
```

`xor t0, ones, ones` → `t0==0`.

## ISA-010 — NOT

```bash
python3 -m unittest compiler.tests.test_m1.TestM1.test_ISA_010
```

`not t0, zero` → `t0==0xFFFFFFFF`.

## ISA-011 — SLL

```bash
python3 -m unittest compiler.tests.test_m1.TestM1.test_ISA_011
```

`sll t0, one, 3` → `t0==8`.

## ISA-014 — CMP

```bash
python3 -m unittest compiler.tests.test_m1.TestM1.test_ISA_014
```

After `add t0, one, one`, `cmp t0, one` leaves `t0==2`, Z=0 C=0 N=0. `cmp one, t0` sets C=1. funct=CMP.

## ISA-031 — NOP

```bash
python3 -m unittest compiler.tests.test_m1.TestM1.test_ISA_031
```

`nop` packs as `sll zero, zero, 0`; stepping it does not change GPRs.

## ISA-050 — assembler names

```bash
python3 -m unittest compiler.tests.test_m1.TestM1.test_ISA_050
```

`zero,one,ones,ra,sp,a0,fp,k0` → r0,r1,r2,r3,r4,r5,r30,r31.

## ISA-052 — TEST

```bash
python3 -m unittest compiler.tests.test_m1.TestM1.test_ISA_052
```

`test t0, one` with `t0==2` leaves `t0` unchanged; 2&1==0 so Z=1 (even). `test one, one` → Z=0 (odd). C=V=0. funct=TEST.

## ISA-053 — TEQ

```bash
python3 -m unittest compiler.tests.test_m1.TestM1.test_ISA_053
```

`teq t0, t0` with `t0==2` leaves `t0==2`, Z=1, N=C=V=0. `teq t0, one` → Z=0. funct=TEQ.

## ISA-054 — r0 wired 0

```bash
python3 -m unittest compiler.tests.test_m1.TestM1.test_ISA_054
```

`add zero, one, one` leaves `r0==0` and Z=0 (result would have been 2).

## ISA-055 — r1 wired 1

```bash
python3 -m unittest compiler.tests.test_m1.TestM1.test_ISA_055
```

After `add one, zero, ones`, `r1` is still 1.

## ISA-056 — r2 wired all-ones

```bash
python3 -m unittest compiler.tests.test_m1.TestM1.test_ISA_056
```

After `add ones, zero, zero`, `r2` is still `0xFFFFFFFF`.
