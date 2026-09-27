# Rust compiler m1 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3, **Rust** (`cargo`, `rustc` on `PATH`), and `yap-emu` (or a cargo build of `emu/rust`).

```bash
python3 -m unittest compiler.tests.test_compiler_rust_m1 -v
```

Expected: `Ran 8 tests ... OK`.

## COMPILER-RUST-001 — crate tree

```bash
python3 -m unittest compiler.tests.test_compiler_rust_m1.TestCompilerRustM1.test_COMPILER_RUST_001
```

`compiler/rust/` contains a `Cargo.toml` and crate sources.

## COMPILER-RUST-002 — cargo build

```bash
python3 -m unittest compiler.tests.test_compiler_rust_m1.TestCompilerRustM1.test_COMPILER_RUST_002
```

`cargo build --manifest-path compiler/rust/Cargo.toml` exits 0.

## COMPILER-RUST-003 — cargo required

```bash
python3 -m unittest compiler.tests.test_compiler_rust_m1.TestCompilerRustM1.test_COMPILER_RUST_003
```

Fails if `cargo` or `rustc` is not on `PATH`.

## COMPILER-RUST-004 — CLI

```bash
python3 -m unittest compiler.tests.test_compiler_rust_m1.TestCompilerRustM1.test_COMPILER_RUST_004
```

`yap-compiler` (via `cargo run`) accepts an input `.ys` and `-o`.

## COMPILER-RUST-005 — YAP1 header

```bash
python3 -m unittest compiler.tests.test_compiler_rust_m1.TestCompilerRustM1.test_COMPILER_RUST_005
```

Output starts with `YAP1`; `load=0`, `entry=0`; `size == file_len-16`.

## COMPILER-RUST-006 — `.ys` / `fn main`

```bash
python3 -m unittest compiler.tests.test_compiler_rust_m1.TestCompilerRustM1.test_COMPILER_RUST_006
```

Input is `.ys` with `fn main()` as in `docs/compiler-rust/design.md`.

## COMPILER-RUST-008 — `j` to `_start`

```bash
python3 -m unittest compiler.tests.test_compiler_rust_m1.TestCompilerRustM1.test_COMPILER_RUST_008
```

Payload is loaded at 0; first word is a `j` (opcode `000010`) to `_start` (`0x84`).

## COMPILER-RUST-010 — halt on yap-emu

```bash
python3 -m unittest compiler.tests.test_compiler_rust_m1.TestCompilerRustM1.test_COMPILER_RUST_010
```

`yap-emu` on the image exits 0.
