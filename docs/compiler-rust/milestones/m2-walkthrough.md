# Rust compiler m2 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3, **Rust** (`cargo`, `rustc` on `PATH`), and `yap-emu`.

```bash
python3 -m unittest compiler.tests.test_compiler_rust_m2 compiler.tests.test_compiler_rust_m1 -v
```

Expected: `Ran 10 tests ... OK`. m1 still passes.

## COMPILER-RUST-007 — add/sub

```bash
python3 -m unittest compiler.tests.test_compiler_rust_m2.TestCompilerRustM2.test_COMPILER_RUST_007
```

Compiled `add.ys` payload contains an `ADD` (`funct=100000`) and a `SUB` (`funct=100010`) from source `+` / `-`.

## COMPILER-RUST-009 — call/return

```bash
python3 -m unittest compiler.tests.test_compiler_rust_m2.TestCompilerRustM2.test_COMPILER_RUST_009
```

A `jal` target is the `add` function (not `_start`); that function ends in `jr ra`. `yap-emu` exits 0.
