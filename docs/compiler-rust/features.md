# Rust compiler features

Prefix: `COMPILER-RUST`

Higher-level language → YAP1. Output must run on `yap-emu`. Not LLVM. Not GCC. Not the Python assembler (`docs/compiler/`).

Implementation: `compiler/rust/`. Tests under `compiler/tests/` and/or that crate. v1 is **Linux**. Language shape and YAP1 layout are `design.md` after this catalog.

## Tree and host

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| COMPILER-RUST-001 | Sources under `compiler/rust/` | open | |
| COMPILER-RUST-002 | Build and tests run on Linux (dev host) | open | |
| COMPILER-RUST-003 | Tests fail if `cargo` / `rustc` is missing | open | |

## Image and CLI

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| COMPILER-RUST-004 | CLI: input path and `-o` YAP1 output | open | |
| COMPILER-RUST-005 | Emits a valid YAP1 (same 16-byte header as the Python assembler) | open | |

## Language

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| COMPILER-RUST-006 | Documented source language (`design.md`) | open | |
| COMPILER-RUST-007 | Integer literals and add/sub in that language | open | |
| COMPILER-RUST-008 | One entry function compiled to reset `PC=0` (or documented entry) | open | |
| COMPILER-RUST-009 | Call/return using the ISA ABI (`sp`, `ra`, args) | open | |

## Run

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| COMPILER-RUST-010 | A compiled program reaches `halt` on `yap-emu` (exit 0) | open | |

## Later generation (do not pull into m1)

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| COMPILER-RUST-011 | Multi-file programs / linking | open | later-generation |
| COMPILER-RUST-012 | C language frontend | open | later-generation |
| COMPILER-RUST-013 | Floating-point in the source language | open | later-generation |
