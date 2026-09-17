# ISA m3 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Python 3 stdlib only (`unittest`).

Run m1–m3:

```bash
python3 -m unittest compiler.tests.test_m1 compiler.tests.test_m2 compiler.tests.test_m3 -v
```

Expected: `Ran 37 tests ... OK`

m3 only:

```bash
python3 -m unittest compiler.tests.test_m3 -v
```

Expected: `Ran 11 tests ... OK`

## ISA-017 — DIV

```bash
python3 -m unittest compiler.tests.test_m3.TestM3.test_ISA_017
```

`div t0, ones, one` → `0xFFFFFFFF`. `div t0, ones, zero` → `t0==0`, Z=1.

## ISA-018 — LW

```bash
python3 -m unittest compiler.tests.test_m3.TestM3.test_ISA_018
```

Bytes `[0x78,0x56,0x34,0x12]` at 0; `lw t0, 0(zero)` → `0x12345678`.

## ISA-019 — SW

```bash
python3 -m unittest compiler.tests.test_m3.TestM3.test_ISA_019
```

`t0=0x12345678`; `sw t0, 0(zero)`; memory bytes `78 56 34 12`.

## ISA-020 — LB / LBU

```bash
python3 -m unittest compiler.tests.test_m3.TestM3.test_ISA_020
```

Byte `0xFF` at 0; `lb` → `0xFFFFFFFF`; `lbu` → `0xFF`.

## ISA-021 — SB

```bash
python3 -m unittest compiler.tests.test_m3.TestM3.test_ISA_021
```

`sb one, 4(zero)`; memory[4]==1; neighbors unchanged.

## ISA-022 — LH / LHU

```bash
python3 -m unittest compiler.tests.test_m3.TestM3.test_ISA_022
```

Half `0x80FF` LE at 8; `lh` → `0xFFFF80FF`; `lhu` → `0x80FF`.

## ISA-023 — SH

```bash
python3 -m unittest compiler.tests.test_m3.TestM3.test_ISA_023
```

`sh` of `0x80FF` at 8 writes `FF 80`.

## ISA-024 — little-endian + alignment

```bash
python3 -m unittest compiler.tests.test_m3.TestM3.test_ISA_024
```

Word round-trip LE; byte 0 is `0x78`. Unaligned `lw` at 1 → CAUSE=8.

## ISA-027 — J

```bash
python3 -m unittest compiler.tests.test_m3.TestM3.test_ISA_027
```

`PC=0`, `j 0x20` → `PC==0x20`. GPRs unchanged.

## ISA-028 — JAL

```bash
python3 -m unittest compiler.tests.test_m3.TestM3.test_ISA_028
```

`PC=0`, `jal 0x20` → `ra==4`, `PC==0x20`.

## ISA-029 — JR / JALR

```bash
python3 -m unittest compiler.tests.test_m3.TestM3.test_ISA_029
```

`jal 0x20` then `jr ra` → `PC==4`. `jalr t0, t1` with `t1==0x40` → `t0==4`, `PC==0x40`.
