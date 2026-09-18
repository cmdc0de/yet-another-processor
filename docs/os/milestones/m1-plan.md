# os m1

Features: OS-001, OS-002, OS-003, OS-018, OS-019

## Intent

A kernel source in `os/` assembles to a YAP1 that `yap-emu` loads and **halts**. Reset is at `PC=0`. Payload address `0x80` is a trap stub (`halt` is enough). Kernel `sp` is `0x1000` per `docs/os/design.md`. Proves the assemble → emulate path.

## Work

- `os/kernel.s` (or similar): `.org 0` sets `sp` and `halt`; `.org 0x80` is a `halt` stub.
- Assemble: `python3 -m compiler.asm os/kernel.s -o os/kernel.yap`
- Run: `cargo run --manifest-path emu/rust/Cargo.toml -- os/kernel.yap` exits 0.
- Tests may call the assembler and emulator; dump shows `r4`/`sp` == `0x1000`.

## Done

- OS-001: payload has kernel at 0 and insns at `0x80`
- OS-002: `yap-emu` on that image exits 0 (halted)
- OS-003: after halt, `sp` (`r4`) is `0x1000`
- OS-018: source lives under `os/` and assembles with `compiler.asm`
- OS-019: a test (or walkthrough command) assembles and runs `yap-emu`

## Out of scope

UBASE/ULIMIT, user `ERET`, syscall dispatch, `SYS_WRITE`, panic `KPAN`, later-generation rows.
