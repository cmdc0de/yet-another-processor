# compiler-rust m1

Features: COMPILER-RUST-001, COMPILER-RUST-002, COMPILER-RUST-003, COMPILER-RUST-004, COMPILER-RUST-005, COMPILER-RUST-006, COMPILER-RUST-008, COMPILER-RUST-010

## Intent

Rust crate `compiler/rust/` (`yap-compiler`) compiles `fn main() {}` to YAP1 (`load=0`, `entry=0`) as in `docs/compiler-rust/design.md`. Image reaches `halt` on `yap-emu`. Missing `cargo`/`rustc` fails tests.

## Work

- `compiler/rust/` crate + CLI `-o`.
- Example/empty `fn main() {}`.
- unittest `compiler/tests/test_compiler_rust_m1.py` (invokes `cargo`; runs `yap-emu` on the image).

## Done

- COMPILER-RUST-001: sources under `compiler/rust/`
- COMPILER-RUST-002: `cargo build` on Linux
- COMPILER-RUST-003: missing `cargo`/`rustc` fails (not skip)
- COMPILER-RUST-004: CLI input path and `-o`
- COMPILER-RUST-005: output is YAP1 (`YAP1` magic, `load=0`, `entry=0`; size matches payload)
- COMPILER-RUST-006: `.ys` / `fn main` as in `design.md`
- COMPILER-RUST-008: `fn main` is the source entry; payload starts at `PC=0`
- COMPILER-RUST-010: `yap-emu` on that image exits 0

## Out of scope

COMPILER-RUST-007, 009 (add/sub, user `fn` call/return). Later-generation 011–013. No LLVM.
