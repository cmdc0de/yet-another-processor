# compiler-rust m1 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| COMPILER-RUST-001 | `compiler/rust/` contains a `Cargo.toml` and crate sources |
| COMPILER-RUST-002 | `cargo build --manifest-path compiler/rust/Cargo.toml` exits 0 |
| COMPILER-RUST-003 | Tests fail if `cargo` or `rustc` is not on `PATH` |
| COMPILER-RUST-004 | `yap-compiler` (via `cargo run -- … --`) accepts an input `.ys` and `-o` |
| COMPILER-RUST-005 | Output starts with `YAP1`; `load=0`, `entry=0`; `size == file_len-16` |
| COMPILER-RUST-006 | Input is `.ys` with `fn main()` as in `docs/compiler-rust/design.md` |
| COMPILER-RUST-008 | Payload is loaded at 0; first word is a `j` (opcode `000010`) to `_start` |
| COMPILER-RUST-010 | `yap-emu` on the image exits 0 |
