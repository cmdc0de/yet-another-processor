# Assembler m2 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Python 3 stdlib only (`unittest`).

```bash
python3 -m unittest compiler.tests.test_asm_m1 compiler.tests.test_asm_m2 -v
```

Expected: `Ran 14 tests ... OK`

m2 only:

```bash
python3 -m unittest compiler.tests.test_asm_m2 -v
```

Expected: `Ran 4 tests ... OK`

## COMPILER-008 — labels

```bash
python3 -m unittest compiler.tests.test_asm_m2.TestAsmM2.test_COMPILER_008
```

`loop: nop` then `j loop` — `loop==0`.

## COMPILER-009 — jump/branch targets

```bash
python3 -m unittest compiler.tests.test_asm_m2.TestAsmM2.test_COMPILER_009
```

`j loop` target is 4. `beq loop` after `cmp one, one` is taken to the label.

## COMPILER-010 — forward refs

```bash
python3 -m unittest compiler.tests.test_asm_m2.TestAsmM2.test_COMPILER_010
```

`j loop` then `loop: halt` — `j` at 0 targets 4.

## COMPILER-011 — `.org`

```bash
python3 -m unittest compiler.tests.test_asm_m2.TestAsmM2.test_COMPILER_011
```

`.org 0x80` / `halt` — halt at offset `0x80`, zeros before. `.org` backward is an error.
