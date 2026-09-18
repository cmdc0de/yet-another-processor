# emu-rust m6 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Rustc/cargo 1.74+ (tested with 1.98).

```bash
cargo test --manifest-path emu/rust/Cargo.toml
```

Expected: all tests `ok` (m1–m6).

m6 only:

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_033 test_emu_rust_034 -- --exact
```

Expected: 2 passed.

## EMU-RUST-033 — MFC1/MTC1

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_033 -- --exact
```

Packed `mfc1` opcode is COP1 (`010001`). `mtc1 t0, f0` then `mfc1 t1, f0` copies the value. `f0` is not a GPR.

## EMU-RUST-034 — unimplemented COP1

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_034 -- --exact
```

COP1 word with a non-move `rs` traps CAUSE=6, PC=0x80.
