# emu-rust m3 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Rustc/cargo 1.74+ (tested with 1.98).

```bash
cargo test --manifest-path emu/rust/Cargo.toml
```

Expected: all tests `ok` (m1–m3).

m3 only:

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_016 test_emu_rust_017 test_emu_rust_018 test_emu_rust_019 -- --exact
```

Expected: 4 passed.

## EMU-RUST-016 — shifts

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_016 -- --exact
```

`sll t0, one, 3` / `srl t0, t0, 2` → 2. `srlv` by `one` → 1. `lui t0, 0x8000` / `sra t0, t0, 1` → `0xC0000000`, N=1. `srav` by `one` → `0xE0000000`. `sllv t0, one, t1` with `t1==3` → 8.

## EMU-RUST-017 — immediates

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_017 -- --exact
```

`addi t0, one, -1` → 0, Z=1. `andi t0, ones, 0x00FF` → `0xFF`. `ori t0, zero, 1` → 1. `xori t0, ones, 0` → `0xFFFFFFFF`.

## EMU-RUST-018 — LUI and ADR

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_018 -- --exact
```

`lui t0, 0x1234` → `0x12340000`, FLAGS unchanged. `ori t0, t0, 0x5678` → `0x12345678`. `PC=0`, `adr t0, 16` → 20.

## EMU-RUST-019 — MUL and DIV

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_019 -- --exact
```

`mul t0, one, ones` → `0xFFFFFFFF`. `mul t0, ones, ones` → 1. `div t0, ones, one` → `0xFFFFFFFF`. `div t0, ones, zero` → 0, Z=1.
