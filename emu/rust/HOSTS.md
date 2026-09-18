# yap-emu host targets (v1)

Guest is always YAP 32-bit little-endian. Hosts:

| Feature | OS / arch | Rust triple | Native test |
|---------|-----------|-------------|-------------|
| EMU-RUST-006 | Linux x86_64 | `x86_64-unknown-linux-gnu` | `cargo test --manifest-path emu/rust/Cargo.toml` |
| EMU-RUST-007 | Linux aarch64 | `aarch64-unknown-linux-gnu` | same, on that host |
| EMU-RUST-008 | Windows x86_64 | `x86_64-pc-windows-msvc` or `x86_64-pc-windows-gnu` | same, on that host |
| EMU-RUST-009 | Windows aarch64 | `aarch64-pc-windows-msvc` | same, on that host |
| EMU-RUST-010 | macOS aarch64 | `aarch64-apple-darwin` | same, on that host |

Intel Mac (`x86_64-apple-darwin`) is out of v1 (EMU-RUST-039).

## Install a target std

```bash
rustup target add aarch64-unknown-linux-gnu
rustup target add x86_64-pc-windows-gnu
rustup target add aarch64-pc-windows-msvc
rustup target add aarch64-apple-darwin
```

## Cross-compile from Linux x86_64

`cargo check --target <triple> --manifest-path emu/rust/Cargo.toml` typechecks without a target C toolchain.

`cargo test --no-run --target <triple>` **links** a test binary and needs that target’s linker:

- `x86_64-pc-windows-gnu`: `x86_64-w64-mingw32-gcc` (this repo’s `.cargo/config.toml` points at it).
- `aarch64-unknown-linux-gnu`: `gcc-aarch64-linux-gnu` / `libc6-dev-arm64-cross`.
- `aarch64-pc-windows-msvc`: MSVC ARM64 toolset (typically a Windows box).
- `aarch64-apple-darwin`: Apple clang + SDK (typically a Mac).

From this Linux x86_64 tree, `cargo test --no-run --target x86_64-pc-windows-gnu` is the one that links. The others `cargo check`. Native `cargo test` on each host is the **run** check.

Helper: `emu/rust/scripts/cross-check.sh`
