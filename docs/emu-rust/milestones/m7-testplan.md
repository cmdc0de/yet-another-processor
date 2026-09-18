# emu-rust m7 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| EMU-RUST-007 | `cargo test --no-run --target aarch64-unknown-linux-gnu --manifest-path emu/rust/Cargo.toml` succeeds. Native `cargo test` on Linux aarch64 is OK when that host is used. |
| EMU-RUST-008 | `cargo test --no-run --target x86_64-pc-windows-gnu` (or `-msvc`) succeeds. Native `cargo test` on Windows x86_64 is OK when that host is used. |
| EMU-RUST-009 | `cargo test --no-run --target aarch64-pc-windows-msvc` succeeds. Native `cargo test` on Windows aarch64 is OK when that host is used. |
| EMU-RUST-010 | `cargo test --no-run --target aarch64-apple-darwin` succeeds (may need a macOS linker). Native `cargo test` on macOS aarch64 is OK when that host is used. |
