# Assembler m3 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Python 3 stdlib only (`unittest`).

```bash
python3 -m unittest compiler.tests.test_asm_m1 compiler.tests.test_asm_m2 compiler.tests.test_asm_m3 -v
```

Expected: `Ran 17 tests ... OK`

m3 only:

```bash
python3 -m unittest compiler.tests.test_asm_m3 -v
```

Expected: `Ran 3 tests ... OK`

## COMPILER-012 — data

```bash
python3 -m unittest compiler.tests.test_asm_m3.TestAsmM3.test_COMPILER_012
```

`.word 0x12345678` → `78 56 34 12`. `.byte 1 2`. `.half 0x80FF` → `FF 80`. Unaligned `.word` is an error.

## COMPILER-013 — `.align`

```bash
python3 -m unittest compiler.tests.test_asm_m3.TestAsmM3.test_COMPILER_013
```

`.byte 1` / `.align 2` / `.word 0` — word at offset 4; bytes 1–3 are 0.

## COMPILER-014 — `.equ`

```bash
python3 -m unittest compiler.tests.test_asm_m3.TestAsmM3.test_COMPILER_014
```

`.equ N, 4` / `lw t0, N(sp)` → `imm16==4`. Duplicate `.equ` is an error.
