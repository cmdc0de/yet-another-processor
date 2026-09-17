# Assembler m4

Features: COMPILER-015, COMPILER-016, COMPILER-017, COMPILER-020

## Intent

Expand `li` / `move` / `la` per `docs/compiler/design.md`, and add `--run`: load the YAP1 payload into `yap_isa.Cpu` at `load`, set `PC=entry`, step until `halt` or a max-step cap.

## Work

- `move rd, rs` → `add rd, rs, zero` (one word).
- `li rd, imm32`: if signed-16, `addi rd, zero, imm`; else `lui` + `ori`.
- `la rd, label`: if `label - (PC+4)` fits `adr`’s signed 16-bit offset, emit `adr`; else `li rd, address`.
- Pseudos expand in pass 2 (or pass 1 must count 1 vs 2 words for `li`/`la` so `LC` and labels stay correct).
- `--run`: unpack YAP1, copy payload to `Cpu.mem[load:]`, `PC=entry`, step until `halted` or N steps (default 100000); non-zero exit if it does not halt.
- m1–m3 tests still pass.

## Done

- COMPILER-015: `li t0, 1` is one `addi`; `li t0, 0x12345678` is `lui`+`ori` matching that constant
- COMPILER-016: `move t0, sp` encodes `add t0, sp, zero`
- COMPILER-017: `la t0, lab` near the label uses `adr`; a far label uses `li`
- COMPILER-020: assemble `nop`/`halt`, `--run` exits 0; a `j .` infinite loop hits the cap and exits non-zero

## Out of scope

ELF, multi-file link, macros, C compiler (later-generation).
