# os m3 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and `yap-emu`.

```bash
cargo build --manifest-path emu/rust/Cargo.toml
python3 -m unittest compiler.tests.test_os_m1 compiler.tests.test_os_m2 compiler.tests.test_os_m3 -v
```

Expected: `Ran 19 tests ... OK`

m3 only:

```bash
python3 -m unittest compiler.tests.test_os_m3 -v
```

Expected: `Ran 6 tests ... OK`

## OS-015 — SYS_WRITE kernel log

```bash
python3 -m unittest compiler.tests.test_os_m3.TestOsM3.test_OS_015
```

Default image: SRAM `0x0800` is `YLOG`; `len` equals the user string length (`yap`); bytes at `0x0808` match. `yap-emu` exits 0.

## OS-016 — bad syscall number

```bash
python3 -m unittest compiler.tests.test_os_m3.TestOsM3.test_OS_016
```

Fixture `os/user_bad_sys.s`: `sys 99`, `sw a4` at `0x1100`, `sys 1`. That word is ≠ 0. Exit 0.

## OS-017 — SYS_WRITE outside window

```bash
python3 -m unittest compiler.tests.test_os_m3.TestOsM3.test_OS_017
```

Fixture `os/user_bad_write.s`: `sys 2` with `a0=0`; log `len` still 0; then `sys 1` exits 0.

## OS-006 — protection fault

```bash
python3 -m unittest compiler.tests.test_os_m3.TestOsM3.test_OS_006
```

Fixture `os/user_prot.s`: user `lw` at 0. Image still halts (exit 0).

## OS-011 — align fault

```bash
python3 -m unittest compiler.tests.test_os_m3.TestOsM3.test_OS_011
```

Fixture `os/user_align.s`: unaligned `lw` in user. Halt, exit 0.

## OS-012 — unknown CAUSE / KPAN

```bash
python3 -m unittest compiler.tests.test_os_m3.TestOsM3.test_OS_012
```

Fixture `os/user_cop1.s`: COP1 non-move from user. Log magic `KPAN` (`4B 50 41 4E`). Halt.
