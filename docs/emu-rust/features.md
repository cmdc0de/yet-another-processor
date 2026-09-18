# Rust OS emulator features

Prefix: `EMU-RUST`

Guest is the YAP 32-bit little-endian machine (`docs/isa/design.md`). Image is YAP1 (`docs/compiler/design.md`). This sequence is a host CPU+SRAM so OS work can start; it does not model the MOSFET/IC register-file split.

Hosts (v1): Linux x86_64, Linux aarch64, Windows x86_64, Windows aarch64, macOS aarch64. Not macOS x86_64.

Implementation lives in `emu/rust/`.

## Host CLI and image

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| EMU-RUST-001 | ~~CLI takes a YAP1 path~~ | done | m1 |
| EMU-RUST-002 | ~~Reject short files, bad `YAP1` magic, or `size != file_len - 16`~~ | done | m1 |
| EMU-RUST-003 | ~~Copy payload to SRAM at `load`, set `PC=entry`; do not map the 16-byte header~~ | done | m1 |
| EMU-RUST-004 | ~~Run until `halt` or a max-step cap (default 100000); non-zero exit if it does not halt~~ | done | m1 |
| EMU-RUST-005 | After the run, print PC, FLAGS, CSRs, and the 32 GPRs | claimed | m5 |

## Host platforms

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| EMU-RUST-006 | ~~Builds and runs tests on Linux x86_64~~ | done | m1 |
| EMU-RUST-007 | Builds and runs tests on Linux aarch64 | open | |
| EMU-RUST-008 | Builds and runs tests on Windows x86_64 | open | |
| EMU-RUST-009 | Builds and runs tests on Windows aarch64 | open | |
| EMU-RUST-010 | Builds and runs tests on macOS aarch64 | open | |

## Machine state

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| EMU-RUST-011 | ~~32-bit addresses and little-endian SRAM~~ | done | m1 |
| EMU-RUST-012 | ~~Fetch a 32-bit insn at `PC`; sequential `PC+4`; unaligned fetch traps CAUSE=8~~ | done | m4 |
| EMU-RUST-013 | ~~32 GPRs; `r0=0`, `r1=1`, `r2=0xFFFFFFFF`; writes to `r0`–`r2` discarded; ops targeting `r0` still update flags~~ | done | m2 |
| EMU-RUST-014 | ~~FLAGS Z, N, C, V per `docs/isa/design.md`~~ | done | m2 |

## Integer execute

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| EMU-RUST-015 | ~~SPECIAL ALU: ADD, SUB, AND, OR, XOR, NOT, SLL, CMP, TEST, TEQ, NOP; flags as ISA~~ | done | m2 |
| EMU-RUST-016 | ~~SRL, SRA, and variable shifts (SLLV, SRLV, SRAV)~~ | done | m3 |
| EMU-RUST-017 | ~~ADDI (sign-extend), ANDI/ORI/XORI (zero-extend)~~ | done | m3 |
| EMU-RUST-018 | ~~LUI and ADR~~ | done | m3 |
| EMU-RUST-019 | ~~MUL and DIV (DIV by 0 → result 0, as ISA)~~ | done | m3 |
| EMU-RUST-020 | ~~Load/store word, half, byte (signed and unsigned loads); unaligned → CAUSE=8~~ | done | m4 |
| EMU-RUST-021 | ~~J, JAL, JR, JALR~~ | done | m4 |
| EMU-RUST-022 | ~~Conditional branches on flags (all `design.md` cond codes); no delay slot~~ | done | m4 |
| EMU-RUST-023 | ~~HALT sets halted; further steps are no-ops~~ | done | m1 |

## Privilege, traps, protection

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| EMU-RUST-024 | User and supervisor; reset: supervisor, `IE=0`, `TE=0`, `PC=0` | claimed | m5 |
| EMU-RUST-025 | MFC0/MTC0; user may read FLAGS and STATUS; other user CSR access → CAUSE=7 | claimed | m5 |
| EMU-RUST-026 | Trap entry: CAUSE, PIE/PP, `P=1`, `IE=0`, `PC=0x80`; EPC = faulting PC except SYS uses `PC+4` | claimed | m5 |
| EMU-RUST-027 | ERET is supervisor-only; restores IE/P from PIE/PP, `PC=EPC` | claimed | m5 |
| EMU-RUST-028 | One user window `[UBASE, ULIMIT)`; user fetch/load/store outside → CAUSE=2 | claimed | m5 |
| EMU-RUST-029 | `IE` and a host-injected external IRQ → CAUSE=1 | claimed | m5 |
| EMU-RUST-030 | `sys` → CAUSE=3 | claimed | m5 |
| EMU-RUST-031 | Setting `TE=1` traps CAUSE=7 and leaves `TE=0` | claimed | m5 |
| EMU-RUST-032 | CAUSE codes 4 (translation miss) and 5 (page fault) exist; v1 does not generate them | claimed | m5 |

## COP1

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| EMU-RUST-033 | 32 FPU registers; MFC1/MTC1 | open | |
| EMU-RUST-034 | Unimplemented COP1 ops trap CAUSE=6 | open | |

## Later generation (do not pull into m1)

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| EMU-RUST-035 | Full virtual memory / TLB (with ISA-051) | open | later-generation |
| EMU-RUST-036 | MOSFET vs IC GPR split or cycle-accurate timing | open | later-generation |
| EMU-RUST-037 | Host MMIO devices (console, MCU, GPU framebuffer) | open | later-generation |
| EMU-RUST-038 | ELF load | open | later-generation |
| EMU-RUST-039 | macOS x86_64 host | open | later-generation |
