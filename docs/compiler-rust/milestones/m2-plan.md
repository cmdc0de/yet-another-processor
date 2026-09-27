# compiler-rust m2

Features: COMPILER-RUST-007, COMPILER-RUST-009

## Intent

Compile the design.md example: `fn add(a, b) { return a + b; }` and `fn main() { add(1, 2); }` to YAP1. Calls use `jal` / `jr ra`, args in `a0`–`a3`, return in `a0`. `+`/`-` are ISA `ADD`/`SUB`. m1 empty-`main` tests still pass. Image still halts on `yap-emu`.

## Work

- `compiler/rust/`: parse extra `fn`s, params, `return`, `+`/`-`, calls.
- Example `compiler/rust/examples/add.ys`.
- unittest `compiler/tests/test_compiler_rust_m2.py`; m1 still green.

## Done

- COMPILER-RUST-007: `1+2` (and a subtraction) appear as `ADD`/`SUB` in the payload
- COMPILER-RUST-009: `add(1, 2)` is a `jal` to `add`; `add` returns with `jr ra`; args in `a0`/`a1`

## Out of scope

Later-generation 011–013. No locals-as-a-separate-feature beyond params. No LLVM.
