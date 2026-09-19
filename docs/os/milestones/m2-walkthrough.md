# os m2 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and `yap-emu`.

```bash
cargo build --manifest-path emu/rust/Cargo.toml
python3 -m unittest compiler.tests.test_os_m1 compiler.tests.test_os_m2 -v
```

Expected: `Ran 13 tests ... OK`

m2 only:

```bash
python3 -m unittest compiler.tests.test_os_m2 -v
```

Expected: `Ran 8 tests ... OK`

## OS-004 — UBASE/ULIMIT

```bash
python3 -m unittest compiler.tests.test_os_m2.TestOsM2.test_OS_004
```

After halt, dump has `ubase 00001000` and `ulimit 00008000`.

## OS-005 — user window

```bash
python3 -m unittest compiler.tests.test_os_m2.TestOsM2.test_OS_005
```

Payload at `0x1000` is `sys 1`.

## OS-007 — ERET to user

```bash
python3 -m unittest compiler.tests.test_os_m2.TestOsM2.test_OS_007
```

Reset path is not a lone `halt`. User at `0x1000` is `sys` imm16=1.

## OS-008 — user `sp`

```bash
python3 -m unittest compiler.tests.test_os_m2.TestOsM2.test_OS_008
```

After halt, dump `r4 00008000` (SYS_EXIT choice A: keep user `sp`).

## OS-009 — saved GPRs

```bash
python3 -m unittest compiler.tests.test_os_m2.TestOsM2.test_OS_009
```

Kernel stack word at `0xFFC` is `0x8000` (saved user `sp`).

## OS-010 — sys dispatch

```bash
python3 -m unittest compiler.tests.test_os_m2.TestOsM2.test_OS_010
```

`sys 1` from user exits 0 (does not loop at `0x80`).

## OS-013 — syscall ABI encoding

```bash
python3 -m unittest compiler.tests.test_os_m2.TestOsM2.test_OS_013
```

User `sys 1` opcode is SYS, imm16=1.

## OS-014 — SYS_EXIT halt

```bash
python3 -m compiler.asm os/kernel.s -o /tmp/kernel.yap
cargo run --manifest-path emu/rust/Cargo.toml --quiet -- /tmp/kernel.yap
echo $?
```

Expected: `0`. Dump includes `r4 00008000`.
