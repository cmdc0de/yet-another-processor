# emu-rust m7

Features: EMU-RUST-007, EMU-RUST-008, EMU-RUST-009, EMU-RUST-010

## Intent

The same `emu/rust` crate **builds and `cargo test`s** on the remaining v1 hosts: Linux aarch64, Windows x86_64, Windows aarch64, macOS aarch64. No host asm. Guest stays YAP 32-bit LE.

## Work

- Keep the crate `std`-only and endian-explicit (already true).
- Document target triples and how to run tests on each host.
- On this Linux x86_64 box: `rustup target add` + `cargo test --no-run --target <triple>` for each (proves **build**).
- **Run** is `cargo test --manifest-path emu/rust/Cargo.toml` on that OS/arch (or qemu-user / a CI runner). Walkthrough will say which checks are cross-compile vs native.

## Done

- EMU-RUST-007: Linux aarch64 (`aarch64-unknown-linux-gnu`)
- EMU-RUST-008: Windows x86_64 (`x86_64-pc-windows-msvc` or `x86_64-pc-windows-gnu`)
- EMU-RUST-009: Windows aarch64 (`aarch64-pc-windows-msvc`)
- EMU-RUST-010: macOS aarch64 (`aarch64-apple-darwin`)

## Out of scope

Intel Mac (039), later-generation rows, OS kernel.
