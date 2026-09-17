# Assembler m1

Features: COMPILER-001, COMPILER-002, COMPILER-003, COMPILER-023, COMPILER-004, COMPILER-005, COMPILER-006, COMPILER-007, COMPILER-018, COMPILER-019

## Intent

`python3 -m compiler.asm in.s -o out.yap` reads a UTF-8 source of `yap_isa` instructions (comments, ABI names, `off(rs)`), writes a YAP1 file (`load=0`, `entry=0`), and fails with `path:line:` without creating the output on error.

## Work

- `compiler/asm.py` (or `compiler/asm/`) CLI and assembler.
- Header helpers: pack/unpack 16-byte YAP1; `size = payload length`.
- Line loop: strip `;` / `#` comments; skip empty; `yap_isa.assemble(line, pc=LC)`; append 4 bytes; `LC += 4`.
- Default `load=0`, `entry=0`. Payload is packed instructions in order (no `.org` yet).
- Tests write a temp `.s`, assemble, check magic/`size`/payload encodings, and error paths.

## Done

- COMPILER-001: `.s` → `.yap` with header + payload
- COMPILER-002: CLI requires input and `-o`
- COMPILER-003: payload bytes are consecutive instructions
- COMPILER-023: magic `YAP1`, `load=0`, `size=file-16`, `entry=0`; reject mismatch in a loader helper
- COMPILER-004: `;` and `#` comments ignored
- COMPILER-005: `ADD` and `add` both work via `yap_isa`
- COMPILER-006: `zero` / `sp` / `t0` accepted
- COMPILER-007: `lw t0, 4(sp)` assembles
- COMPILER-018: bad line → `file:N: ...`, no `-o` file
- COMPILER-019: `blorp t0, t0` is an error

## Out of scope

Labels, `.org`/data/`.equ`, pseudos `li`/`move`/`la`, `--run` (COMPILER-020), ELF, multi-file.
