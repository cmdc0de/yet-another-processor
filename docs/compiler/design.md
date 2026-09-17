# Assembler design (v1)

Python assembler: one `.s` file → one **YAP1** image. Instruction encodings are `docs/isa/design.md`. This file freezes source syntax and the on-disk format.

Implementation lives in `compiler/` and must call `compiler.yap_isa` to pack ops. Do not duplicate opcode tables.

## YAP1 file format

Little-endian, like the ISA. The CPU never executes the header. A loader (host CLI, later MCU/Rust emulator) reads the header, copies the payload, and sets `PC`.

```
offset  size  name    meaning
0       4     magic   ASCII `YAP1` (file bytes `59 41 50 31`)
4       4     load    SRAM address of payload byte 0 (u32)
8       4     size    payload length in bytes (u32); must equal file_size − 16
12      4     entry   PC after load (u32, absolute)
16      size  payload raw LE bytes
```

Total file size = `16 + size`. No checksum in v1.

### v1 defaults

| Field | v1 |
|-------|-----|
| `load` | `0` |
| `entry` | `0` (reset vector). Trap handler is payload bytes at address `0x80`, not a second format. |
| `size` | whatever `.org` / data produced |

CLI may override `load` / `entry` later; the assembler default is both `0`.

### Loader rules

1. Reject if file shorter than 16 bytes or `magic != "YAP1"`.
2. Reject if `size != file_len - 16`.
3. Copy payload to SRAM `[load, load+size)`.
4. Set `PC = entry`.
5. Do not map the 16-byte header into SRAM unless a future flag says so (v1: never).

`yap_isa.Cpu` host path (`COMPILER-020`): same steps, then `step` until `halted` or a step limit.

Intel HEX is an optional *programming* dump of the payload only, not a second architecture. ELF is out of v1 (`COMPILER-024`).

## Source language

- Encoding: UTF-8.
- One statement per line. Empty lines ignored.
- Comments: from `;` or `#` to end of line (not inside quotes, v1 has no strings yet except data directives we may add later).
- Mnemonics and register names: **case-insensitive**.
- Labels and `.equ` names: **case-sensitive**, `[A-Za-z_][A-Za-z0-9_]*`.
- Immediates: decimal or `0x` hex; optional leading `-`.

### Instructions

Any mnemonic `compiler.yap_isa.assemble()` already accepts, with the same operand forms (`rd, rs, rt`, `off(rs)`, `sys imm`, `mfc0 rd, csr`, …).

Branch/jump targets in source may be:

- absolute immediates (`j 0x20`, `beq 0x20`) as today, or
- labels (`j loop`, `beq done`). The assembler converts labels to the encoding `assemble(..., pc=current)` expects.

Location counter `LC` is a **payload address** (what the CPU will see), not a file offset. File offset = `16 + (LC - load)` once `load` is known (v1 `load=0` so file offset = `16 + LC`).

### Labels

`name:` at the start of a line (optional instruction after it). Value = current `LC`. Forward refs allowed (`COMPILER-010`).

### Directives

| Directive | Effect |
|-----------|--------|
| `.org imm` | `LC = imm` (payload address). Gaps are filled with `0`. `imm` must be `>= load` (v1 `load=0`). |
| `.byte imm...` | emit u8s, advance `LC` by 1 each |
| `.half imm...` | emit u16 LE, `LC += 2` each; error if unaligned unless `.align` first |
| `.word imm...` | emit u32 LE, `LC += 4` each; error if unaligned |
| `.align n` | pad `0` until `LC % 2^n == 0` (`n` is the log2, so `.align 2` is 4-byte) |
| `.equ name, imm` | name may be used as an immediate; not a label |

`.org` below current `LC` is an error (no overlap).

### Pseudos

| Pseudo | Expansion |
|--------|-----------|
| `nop` | already a real op in `yap_isa` (`sll zero, zero, 0`) |
| `move rd, rs` | `add rd, rs, zero` |
| `li rd, imm32` | if `imm` fits signed 16: `addi rd, zero, imm`; else `lui rd, hi` + `ori rd, rd, lo` |
| `la rd, label` | if `label - (PC+4)` fits `adr`: `adr rd, rel`; else `li rd, address` |

`PC` for `adr`/`bcc`/`j` is the address of **that** instruction (`LC` before emitting it).

## CLI

```
python3 -m compiler.asm  input.s  -o output.yap
```

- Default output name: input with `.yap` if `-o` omitted (optional; if unimplemented, `-o` is required — `COMPILER-002` requires `-o`).
- Exit 0 on success. Non-zero on error; **do not** write/truncate the output file on failure (`COMPILER-018`).
- Errors: `path:line: message`.

v1 does not assemble multiple files or link.

## Host run

```
python3 -m compiler.asm  input.s  -o out.yap --run
```

`--run` is `COMPILER-020`: load YAP1 as above into `Cpu`, step until `halt` or a configurable max steps (default e.g. 100000), then exit non-zero if it did not halt.

## Out of this document

- ELF, PE, multi-file link
- Macro processor
- C compiler
- Rust emulator image load (same YAP1 rules when that sequence starts)
