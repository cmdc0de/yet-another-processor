# Assembler m1 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Python 3 stdlib only (`unittest`).

```bash
python3 -m unittest compiler.tests.test_asm_m1 -v
```

Expected: `Ran 10 tests ... OK`

CLI smoke (optional):

```bash
printf 'nop\nhalt\n' > /tmp/t.s
python3 -m compiler.asm /tmp/t.s -o /tmp/t.yap
```

`/tmp/t.yap` starts with `YAP1` and is 24 bytes (`16 + 8`).

## COMPILER-001 — .s to YAP1

```bash
python3 -m unittest compiler.tests.test_asm_m1.TestAsmM1.test_COMPILER_001
```

`nop` + `halt` → file > 16 bytes; payload is two instructions.

## COMPILER-002 — CLI `-o`

```bash
python3 -m unittest compiler.tests.test_asm_m1.TestAsmM1.test_COMPILER_002
```

Missing `-o` exits non-zero. With `-o`, the file exists.

## COMPILER-003 — linear payload

```bash
python3 -m unittest compiler.tests.test_asm_m1.TestAsmM1.test_COMPILER_003
```

Three `nop`s → `size==12`; identical words.

## COMPILER-023 — header

```bash
python3 -m unittest compiler.tests.test_asm_m1.TestAsmM1.test_COMPILER_023
```

Magic `YAP1`, `load==0`, `entry==0`, `size==len-16`. Bad size rejected.

## COMPILER-004 — comments

```bash
python3 -m unittest compiler.tests.test_asm_m1.TestAsmM1.test_COMPILER_004
```

`nop ; hi` and `nop # hi` match `nop`.

## COMPILER-005 — case

```bash
python3 -m unittest compiler.tests.test_asm_m1.TestAsmM1.test_COMPILER_005
```

`ADD` equals `add`.

## COMPILER-006 — ABI names

```bash
python3 -m unittest compiler.tests.test_asm_m1.TestAsmM1.test_COMPILER_006
```

`add sp, zero, one` has `rd=4`.

## COMPILER-007 — `off(rs)`

```bash
python3 -m unittest compiler.tests.test_asm_m1.TestAsmM1.test_COMPILER_007
```

`lw t0, 4(sp)` is LW, `rs=sp`, `imm=4`.

## COMPILER-018 — line errors, no output

```bash
python3 -m unittest compiler.tests.test_asm_m1.TestAsmM1.test_COMPILER_018
```

Error on line 3 is `...:3:`; `-o` path absent.

## COMPILER-019 — unknown mnemonic

```bash
python3 -m unittest compiler.tests.test_asm_m1.TestAsmM1.test_COMPILER_019
```

`blorp t0, t0` is an error.
