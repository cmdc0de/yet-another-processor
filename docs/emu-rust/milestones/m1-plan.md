# emu-rust m1

Features: EMU-RUST-001, EMU-RUST-002, EMU-RUST-003, EMU-RUST-004, EMU-RUST-006, EMU-RUST-011, EMU-RUST-023

## Intent

A Rust crate in `emu/rust/` loads one YAP1 file into little-endian SRAM, sets `PC=entry`, fetches 32-bit words, and either **halts** or hits a step cap. Enough to run `halt` (and to prove a non-halt image does not exit 0). Linux x86_64 is the first host.

## Work

- Crate + CLI: YAP1 path required; `--max-steps` default 100000.
- Unpack header (`YAP1`, `load`, `size`, `entry`); reject short file, bad magic, `size != file_len-16`.
- SRAM: 32-bit addresses, LE bytes; copy payload to `[load, load+size)`; header is not mapped; `PC=entry`.
- Step: fetch `u32` LE at `PC`; if the word is `halt`, set halted (further steps no-op). Any other word: `PC+4` and continue (no ALU yet).
- Tests may build fixtures with `python3 -m compiler.asm` or raw YAP1 bytes.
- `cargo test` on Linux x86_64.

## Done

- EMU-RUST-001: CLI takes a YAP1 path; missing path is non-zero
- EMU-RUST-002: short / bad magic / size mismatch rejected
- EMU-RUST-003: payload at `load`, `PC=entry`; header bytes are not in SRAM
- EMU-RUST-004: `halt` image exits 0; a never-halt image with a small `--max-steps` exits non-zero
- EMU-RUST-006: `cargo test` passes on Linux x86_64
- EMU-RUST-011: word `0x12345678` in SRAM is bytes `78 56 34 12`
- EMU-RUST-023: `halt` sets halted; a further step does not run another instruction

## Out of scope

Dump (005), other hosts (007–010), GPRs/flags/ALU, fetch-alignment trap (012’s CAUSE=8), jumps, privilege, COP1, later-generation rows.
