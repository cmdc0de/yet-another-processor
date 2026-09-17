# emu-rust m2 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Rustc/cargo 1.74+ (tested with 1.98).

```bash
cargo test --manifest-path emu/rust/Cargo.toml
```

Expected: all tests `ok` (m1 CLI + library, including `test_emu_rust_013` / `014` / `015`).

m2 only:

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_013 test_emu_rust_014 test_emu_rust_015 -- --exact
```

Expected: 3 passed.

## EMU-RUST-013 — GPRs

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_013 -- --exact
```

`r0`==0, `r1`==1, `r2`==`0xFFFFFFFF`. `add t0, one, one` → `t0==2`. Write `r0` discarded; `add zero, one, one` still sets Z=0.

## EMU-RUST-014 — FLAGS

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_014 -- --exact
```

`add t0, one, ones` wraps to 0, Z=1, C=1. `sub t0, zero, one` → `t0==0xFFFFFFFF`, N=1, C=1 (borrow).

## EMU-RUST-015 — SPECIAL ALU

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_015 -- --exact
```

`nop` is `sll zero, zero, 0` (word 0). `and`/`or`/`xor`/`not`/`sll`/`cmp`/`test`/`teq` match `yap_isa.Cpu` on the same words.
