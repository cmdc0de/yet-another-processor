# os m1 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and a built `yap-emu` (`cargo build --manifest-path emu/rust/Cargo.toml`).

```bash
cargo build --manifest-path emu/rust/Cargo.toml
python3 -m unittest compiler.tests.test_os_m1 -v
```

Expected: `Ran 5 tests ... OK`

## OS-001 — trap at 0x80

```bash
python3 -m unittest compiler.tests.test_os_m1.TestOsM1.test_OS_001
```

Assembled payload at `0x80` is `halt`, and that word is not the same as the reset insn at 0.

## OS-002 — halt on yap-emu

```bash
python3 -m compiler.asm os/kernel.s -o /tmp/kernel.yap
cargo run --manifest-path emu/rust/Cargo.toml --quiet -- /tmp/kernel.yap
echo $?
```

Expected: exit `0`.

## OS-003 — kernel `sp`

Same run as OS-002. After m2 the image enters user then `SYS_EXIT`; dump `r4` is `00008000` (user `sp`). Kernel still uses `0x1000` as its stack base before `ERET`.

```bash
python3 -m unittest compiler.tests.test_os_m1.TestOsM1.test_OS_003
```

## OS-018 — assemble from `os/`

```bash
python3 -m compiler.asm os/kernel.s -o /tmp/kernel.yap
echo $?
```

Expected: `0`.

## OS-019 — assemble and run in a test

```bash
python3 -m unittest compiler.tests.test_os_m1.TestOsM1.test_OS_019
```

Assemble from `os/` and `yap-emu` both succeed.
