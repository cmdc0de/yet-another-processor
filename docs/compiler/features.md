# Python assembler (v1) features

Prefix: `COMPILER`

Machine image is **YAP1**: 16-byte little-endian header plus a raw payload. Encodings live in `docs/isa/`; this sequence is source files → YAP1.

## CLI and image

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| COMPILER-001 | ~~Assemble one UTF-8 `.s` file into a YAP1 file (header + little-endian payload)~~ | done | m1 |
| COMPILER-002 | ~~CLI: input path and `-o` output path~~ | done | m1 |
| COMPILER-003 | ~~Linear payload: bytes laid out by location counter (no linker)~~ | done | m1 |
| COMPILER-023 | ~~Write and validate the 16-byte YAP1 header (`magic`, `load`, `size`, `entry`)~~ | done | m1 |

## Source syntax

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| COMPILER-004 | ~~Comments: `;` or `#` through end of line~~ | done | m1 |
| COMPILER-005 | ~~Mnemonics case-insensitive; uses `yap_isa` for all v1 ops already in `assemble()`~~ | done | m1 |
| COMPILER-006 | ~~ABI register names (`zero`, `sp`, `ra`, `a0`, `f0`, …)~~ | done | m1 |
| COMPILER-007 | ~~Memory operands `off(rs)`~~ | done | m1 |

## Symbols and control

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| COMPILER-008 | ~~Label definition `name:`~~ | done | m2 |
| COMPILER-009 | ~~Labels as `j` / `jal` / `bcc` targets~~ | done | m2 |
| COMPILER-010 | ~~Forward references resolved (two-pass or equivalent)~~ | done | m2 |
| COMPILER-011 | ~~`.org imm` sets the location counter (payload address)~~ | done | m2 |

## Data and layout

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| COMPILER-012 | ~~`.byte` / `.half` / `.word` emit LE data~~ | done | m3 |
| COMPILER-013 | ~~`.align n` pads zeros to 2^n~~ | done | m3 |
| COMPILER-014 | ~~`.equ name, imm` named constants~~ | done | m3 |

## Pseudos

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| COMPILER-015 | `li rd, imm32` → `lui`+`ori` (or `addi` when it fits) | claimed | m4 |
| COMPILER-016 | `move rd, rs` → `add rd, rs, zero` | claimed | m4 |
| COMPILER-017 | `la rd, label` → `adr` or `lui`+`ori` as needed | claimed | m4 |

## Errors and host run

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| COMPILER-018 | ~~Errors include file and line; no output file on failure~~ | done | m1 |
| COMPILER-019 | ~~Unknown mnemonic / bad operand is an error~~ | done | m1 |
| COMPILER-020 | Load a YAP1 image into `yap_isa.Cpu` (skip header, copy payload to `load`, `PC=entry`) and run until `halt` | claimed | m4 |

## Later generation (do not pull into m1)

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| COMPILER-021 | Multi-file link / `.text`+`.data` sections | open | later-generation |
| COMPILER-022 | Macros, C language, LLVM/Rust compiler | open | later-generation |
| COMPILER-024 | ELF as a host-only container | open | later-generation |
