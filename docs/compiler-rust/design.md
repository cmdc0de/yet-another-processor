# Rust compiler design (v1)

A small integer language → **YAP1**. Same on-disk image as `docs/compiler/design.md`. Not LLVM. Not GCC. Not the Python assembler.

## Host and crate

| Knob | v1 |
|------|----|
| Crate path | `compiler/rust/` |
| Package / bin | **`yap-compiler`** |
| Host | Linux |
| Toolchain | `cargo` / `rustc` |

Missing `cargo` or `rustc` fails tests (not skip). No GUI.

## CLI

```
yap-compiler  input.ys  -o output.yap
```

(`cargo run --manifest-path compiler/rust/Cargo.toml --` is the same.) Exit 0 on success. Non-zero on error; **do not** write the output file on failure. Errors: `path:line: message`.

## YAP1

Same 16-byte LE header as the Python assembler:

| Field | v1 |
|-------|-----|
| magic | ASCII `YAP1` |
| load | `0` |
| entry | `0` |
| size | payload bytes |

CPU never executes the header. `yap-emu` loads as today.

### Layout of the payload

| Address | Contents |
|---------|----------|
| `0x0000` | `j _start` |
| `0x0080` | `halt` (trap stub so a stray trap stops) |
| `0x0084` | `_start`: `li sp, 0x8000`, `jal main`, `halt` |
| after that | compiled functions, `main` among them |

`fn main` is the source entry. Its return value is ignored. Stack: **empty descending**, `sp=0x8000`, 8-byte aligned at calls (`docs/isa/design.md`).

## Source language

UTF-8. Suffix **`.ys`**. One program per file. Comments: `//` to end of line.

Identifiers: case-sensitive `[A-Za-z_][A-Za-z0-9_]*`. Keywords: `fn`, `return`.

Integers: decimal or `0x` hex; optional `-`. Values are **i32** (32-bit two’s complement). `+` / `-` are ISA `ADD` / `SUB` (wrap).

```
program  := fn+
fn       := "fn" ident "(" params? ")" "{" stmt* "}"
params   := ident ("," ident)*     // at most 4; map to a0–a3
stmt     := "return" expr ";"
          | ident "=" expr ";"
          | expr ";"
expr     := add
add      := term (("+" | "-") term)*
term     := INT | ident | ident "(" args? ")" | "(" expr ")"
args     := expr ("," expr)*       // at most 4
```

`fn main()` is required, no parameters. Other `fn`s are callable. Assignment introduces a local (callee stack slot). Calls use `jal` / `jr ra`; callee saves `ra`/`sp` as needed. Args in `a0`–`a3`; integer return in `a0`.

No floats, no types besides i32, no modules.

Example that must compile and halt:

```
fn add(a, b) {
  return a + b;
}
fn main() {
  add(1, 2);
}
```

## Out of this document

Multi-file link, C, FP in source, OS syscalls from this language, ELF.
