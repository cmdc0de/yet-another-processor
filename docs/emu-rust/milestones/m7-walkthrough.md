# emu-rust m7 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Rustc/cargo 1.74+ (tested with 1.98). Hosts are documented in `emu/rust/HOSTS.md`.

Native (this Linux x86_64 box):

```bash
cargo test --manifest-path emu/rust/Cargo.toml
```

Expected: all existing tests `ok`. `test_emu_rust_006` runs; 007–010 are `cfg`’d for the other hosts.

Install target stdlibs (once):

```bash
rustup target add aarch64-unknown-linux-gnu x86_64-pc-windows-gnu aarch64-pc-windows-msvc aarch64-apple-darwin
```

Typecheck every remaining v1 triple (no target C library required):

```bash
sh emu/rust/scripts/cross-check.sh
```

Expected: `cargo check` OK for all four; `cargo test --no-run --target x86_64-pc-windows-gnu` links (needs `x86_64-w64-mingw32-gcc`).

## EMU-RUST-007 — Linux aarch64

```bash
cargo check --target aarch64-unknown-linux-gnu --manifest-path emu/rust/Cargo.toml
```

Expected: `Finished`. Linking `cargo test --no-run --target aarch64-unknown-linux-gnu` needs `gcc-aarch64-linux-gnu` (not on this box). Native run:

```bash
cargo test --manifest-path emu/rust/Cargo.toml
```

on Linux aarch64; `test_emu_rust_007` asserts `linux` / `aarch64`.

## EMU-RUST-008 — Windows x86_64

```bash
cargo test --no-run --target x86_64-pc-windows-gnu --manifest-path emu/rust/Cargo.toml
```

Expected: test `.exe` artifacts under `emu/rust/target/x86_64-pc-windows-gnu/`. Native run on Windows x86_64: `cargo test --manifest-path emu/rust/Cargo.toml` (`test_emu_rust_008`).

## EMU-RUST-009 — Windows aarch64

```bash
cargo check --target aarch64-pc-windows-msvc --manifest-path emu/rust/Cargo.toml
```

Expected: `Finished`. `cargo test --no-run` for this triple needs the MSVC ARM64 linker (Windows). Native run on Windows aarch64: `cargo test --manifest-path emu/rust/Cargo.toml` (`test_emu_rust_009`).

## EMU-RUST-010 — macOS aarch64

```bash
cargo check --target aarch64-apple-darwin --manifest-path emu/rust/Cargo.toml
```

Expected: `Finished`. Linking needs Apple clang/SDK. Native run on macOS aarch64: `cargo test --manifest-path emu/rust/Cargo.toml` (`test_emu_rust_010`).
