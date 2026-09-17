# Assembler m4 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Python 3 stdlib only (`unittest`).

```bash
python3 -m unittest compiler.tests.test_asm_m1 compiler.tests.test_asm_m2 compiler.tests.test_asm_m3 compiler.tests.test_asm_m4 -v
```

Expected: `Ran 21 tests ... OK`

m4 only:

```bash
python3 -m unittest compiler.tests.test_asm_m4 -v
```

Expected: `Ran 4 tests ... OK`

## COMPILER-015 — `li`

```bash
python3 -m unittest compiler.tests.test_asm_m4.TestAsmM4.test_COMPILER_015
```

`li t0, 1` is one word, `addi t0, zero, 1`. `li t0, 0x12345678` is two words (`lui`+`ori`); stepping them on `Cpu` leaves `t0==0x12345678`.

## COMPILER-016 — `move`

```bash
python3 -m unittest compiler.tests.test_asm_m4.TestAsmM4.test_COMPILER_016
```

`move t0, sp` encodes the same word as `add t0, sp, zero`.

## COMPILER-017 — `la`

```bash
python3 -m unittest compiler.tests.test_asm_m4.TestAsmM4.test_COMPILER_017
```

`lab: nop` / `la t0, lab` is one `adr` word. `la t0, far` / `.org 0x20000` / `far:` is two words (`lui`+`ori`); stepping them leaves `t0==0x20000`.

## COMPILER-020 — `--run`

```bash
python3 -m unittest compiler.tests.test_asm_m4.TestAsmM4.test_COMPILER_020
```

CLI (same checks):

```bash
printf 'nop\nhalt\n' > /tmp/halt.s
python3 -m compiler.asm /tmp/halt.s -o /tmp/h.yap --run
echo $?
```

Expected: `0`.

```bash
printf 'j loop\nloop: j loop\n' > /tmp/loop.s
python3 -m compiler.asm /tmp/loop.s -o /tmp/loop.yap --run --max-steps 1000
echo $?
```

Expected: non-zero (hits the step cap). Default cap without `--max-steps` is 100000.
