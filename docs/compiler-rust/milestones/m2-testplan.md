# compiler-rust m2 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| COMPILER-RUST-007 | Compiled `add.ys` payload contains an `ADD` (`funct=100000`) and a `SUB` (`funct=100010`) from source `+` / `-` |
| COMPILER-RUST-009 | Same image: a `jal` target is the `add` function (not `_start`); that function ends in `jr ra`. `yap-emu` exits 0 |

For 007, the example must include a `-` (e.g. `return a + b - 0;` or a second expression) so `SUB` is present.
