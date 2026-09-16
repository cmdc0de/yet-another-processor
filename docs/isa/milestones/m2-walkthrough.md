# ISA m2 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Python 3 stdlib only (`unittest`).

Run m1 + m2:

```bash
python3 -m unittest compiler.tests.test_m1 compiler.tests.test_m2 -v
```

Expected: `Ran 26 tests ... OK`

m2 only:

```bash
python3 -m unittest compiler.tests.test_m2 -v
```

Expected: `Ran 7 tests ... OK`

## ISA-012 — SRL / SRLV

```bash
python3 -m unittest compiler.tests.test_m2.TestM2.test_ISA_012
```

`sll t0, one, 3` then `srl t0, t0, 2` → `t0==2`. `srlv t0, t0, one` → `t0==1`. funct=SRL / SRLV.

## ISA-013 — SRA / SRAV

```bash
python3 -m unittest compiler.tests.test_m2.TestM2.test_ISA_013
```

`lui t0, 0x8000` → `0x80000000`. `sra t0, t0, 1` → `0xC0000000`, N=1. `srav t0, t0, one` → `0xE0000000`.

## ISA-015 — ALU immediates

```bash
python3 -m unittest compiler.tests.test_m2.TestM2.test_ISA_015
```

`addi t0, one, -1` → 0, Z=1. `andi t0, ones, 0x00FF` → `0xFF`. `ori t0, zero, 1` → 1. `xori t0, ones, 0` → `0xFFFFFFFF`.

## ISA-016 — MUL

```bash
python3 -m unittest compiler.tests.test_m2.TestM2.test_ISA_016
```

`mul t0, one, ones` → `0xFFFFFFFF`. `mul t0, ones, ones` → 1. Zero product sets Z. funct=MUL.

## ISA-025 — LUI + ORI constant

```bash
python3 -m unittest compiler.tests.test_m2.TestM2.test_ISA_025
```

`lui t0, 0x1234` → `0x12340000`, FLAGS unchanged. `ori t0, t0, 0x5678` → `0x12345678`. opcode=LUI.

## ISA-026 — ADR

```bash
python3 -m unittest compiler.tests.test_m2.TestM2.test_ISA_026
```

`PC=0`, `adr t0, 16` → `t0==20`. opcode=ADR. FLAGS unchanged.

## sllv

```bash
python3 -m unittest compiler.tests.test_m2.TestM2.test_sllv
```

`sllv t0, one, t1` with `t1==3` → `t0==8`. funct=SLLV.
