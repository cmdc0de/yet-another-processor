# ISA + ABI design

Custom 32-bit RISC, load/store, flags, microcoded control. Formats are MIPS-shaped so decode is regular. **Not** MIPS-compatible (wired `r0`–`r2`, flags, base/limit protection, traps).

v1 protection is **one user base/limit**, not a multi-region MPU.

## Word, endianness, fetch

- Data word and address: 32-bit (`ISA-001`).
- Instructions: **fixed 32-bit**, naturally aligned. Unaligned fetch traps (CAUSE=8).
- Endianness: **little-endian**. Byte 0 of a word is bits `[7:0]`.
- PC is architectural (`ISA-003`). Sequential fetch: `PC <- PC + 4`.
- Reset: supervisor, `IE=0`, `TE=0`, `PC=0`.

## GPRs

32 names, one file (`ISA-002`). 5-bit `rd` / `rs` / `rt`.

| Reg | Asm | Value | Writes |
|-----|-----|-------|--------|
| `r0` | `zero` | `0x00000000` | discarded; **flags still update** (`ISA-054`) |
| `r1` | `one` | `0x00000001` | discarded (`ISA-055`) |
| `r2` | `ones` | `0xFFFFFFFF` | discarded (`ISA-056`) |
| `r3`–`r31` | (ABI names) | latches / IC | normal |

`NOP` is `sll zero, zero, 0` (`ISA-031`).

## Flags (`ISA-004`)

Separate FLAGS register (not a GPR). Matches the MOSFET flags block on the physical CPU.

| Bit | Name | Meaning |
|-----|------|---------|
| 0 | Z | result == 0 |
| 1 | N | result bit 31 |
| 2 | C | ADD: carry out. SUB/CMP: **borrow** (1 if unsigned `rs < rt`) |
| 3 | V | signed overflow |

Updated by: `ADD`/`SUB`/`CMP` (Z N C V), `TEST` (Z N; C=V=0), `TEQ` (Z; N=C=V=0), `AND`/`OR`/`XOR`/`NOT` (Z N; C=V=0), shifts (Z N; C=last bit shifted out; V=0), `MUL`/`DIV` (Z N; C=V=0). Loads, stores, and jumps do not change FLAGS.

## CSRs (coprocessor 0)

Accessed with `MFC0` / `MTC0`. User **read** of FLAGS and STATUS is allowed. User **write** and all other CSR access: privilege trap (CAUSE=7).

| Index | Name | Role |
|-------|------|------|
| 0 | STATUS | bits below |
| 1 | FLAGS | also written by ALU |
| 2 | EPC | PC to resume |
| 3 | CAUSE | exception code |
| 4 | UBASE | user address base (inclusive) |
| 5 | ULIMIT | user address limit (exclusive) |

STATUS:

| Bit | Name | |
|-----|------|--|
| 0 | IE | interrupt enable (`ISA-039`) |
| 1 | P | 1 = supervisor, 0 = user (`ISA-033`) |
| 2 | TE | translation enable; **v1 must be 0**. Setting it is reserved (`ISA-042`) |
| 8 | PIE | previous IE (saved on trap) |
| 9 | PP | previous P |

## Privilege, traps, protection

On trap (`ISA-035`):

- `CAUSE <- code`
- `PIE/PP <- IE/P`
- `P <- 1`, `IE <- 0`
- `PC <- 0x00000080` (trap vector)
- `EPC`: faulting instruction PC, except **SYS uses `EPC = PC+4`** so `ERET` skips the `sys`

`ERET` (`ISA-036`): supervisor-only. `IE/P <- PIE/PP`, `PC <- EPC`.

CAUSE:

| Code | Meaning |
|------|---------|
| 0 | reset |
| 1 | external interrupt (`ISA-040`) |
| 2 | protection (`ISA-038`) |
| 3 | SYS |
| 4 | reserved translation miss (`ISA-041`) |
| 5 | reserved page fault (`ISA-041`) |
| 6 | unimplemented coprocessor op (`ISA-045`) |
| 7 | illegal / privileged instruction |
| 8 | alignment |

Protection (`ISA-037`): **one user window**. User fetch, load, and store require `UBASE <= addr < ULIMIT` and correct alignment; otherwise CAUSE=2. Supervisor does not check base/limit. No page tables in v1 (`ISA-051` stays later-generation). A later 4-region MPU can reuse `UBASE`/`ULIMIT` as region 0; it is not part of this contract.

## Formats

```
R:  31-26 opcode | 25-21 rd | 20-16 rs | 15-11 rt | 10-6 shamt | 5-0 funct
I:  31-26 opcode | 25-21 rd | 20-16 rs | 15-0 imm16
J:  31-26 opcode | 25-0 target26
B:  31-26 opcode | 25-22 cond | 21-0 imm22
```

`opcode = 000000` is SPECIAL (R-type, decode `funct`).

Immediates:

- `ADDI`: **sign-extend** imm16
- `ANDI` / `ORI` / `XORI`: **zero-extend** imm16
- J: `target26` is a word address in the current 256 MiB region: `(PC+4)[31:28] || target26 || 00`
- Bcc: signed `imm22` word offset: `PC+4 + (sext(imm22) << 2)`

## Opcode map (primary)

| op | Mnemonic | Form | Feature |
|----|----------|------|---------|
| 000000 | SPECIAL | R | ALU, JR, … |
| 000010 | J | J | ISA-027 |
| 000011 | JAL | J | ISA-028; `r3 <- PC+4` |
| 000100 | Bcc | B | ISA-030 |
| 001000 | ADDI | I | ISA-015 |
| 001001 | ADR | I | ISA-026; `rd <- (PC+4) + sext(imm16)` |
| 001010 | SYS | I | ISA-049; imm16 = number; trap CAUSE=3 |
| 001100 | ANDI | I | ISA-015 |
| 001101 | ORI | I | ISA-015 |
| 001110 | XORI | I | ISA-015 |
| 001111 | LUI | I | ISA-025; `rd <- imm16 << 16` |
| 010000 | COP0 | R | MFC0 / MTC0 |
| 010001 | COP1 | R | MFC1 / MTC1 (`ISA-043`, `ISA-044`); other functs CAUSE=6 |
| 100000 | LB | I | ISA-020 sign-extend |
| 100001 | LH | I | ISA-022 sign-extend |
| 100011 | LW | I | ISA-018 |
| 100100 | LBU | I | ISA-020 zero-extend |
| 100101 | LHU | I | ISA-022 zero-extend |
| 101000 | SB | I | ISA-021 |
| 101001 | SH | I | ISA-023 |
| 101011 | SW | I | ISA-019 |

Load/store address = `rs + sext(imm16)`. Halfword aligned to 2, word to 4, else CAUSE=8.

`LUI rd, imm` then `ORI rd, rd, lo` forms any 32-bit constant (`ISA-025`).

## SPECIAL `funct`

| funct | Mnemonic | Notes |
|-------|----------|-------|
| 000000 | SLL | `rd = rs << shamt` (`ISA-011`) |
| 000010 | SRL | (`ISA-012`) |
| 000011 | SRA | (`ISA-013`) |
| 000100 | SLLV | `rd = rs << rt[4:0]` |
| 000110 | SRLV | |
| 000111 | SRAV | |
| 001000 | JR | `PC <- rs` (`ISA-029`) |
| 001001 | JALR | `rd <- PC+4; PC <- rs` |
| 011000 | MUL | `rd = low 32 of rs * rt` (`ISA-016`); implementation later |
| 011010 | DIV | `rd = rs / rt` (`ISA-017`); divide by zero: `rd=0`, Z=1 |
| 100000 | ADD | (`ISA-005`) |
| 100010 | SUB | (`ISA-006`) |
| 100100 | AND | (`ISA-007`) |
| 100101 | OR | (`ISA-008`) |
| 100110 | XOR | (`ISA-009`) |
| 100111 | NOT | `rd = ~rs` (`ISA-010`); `rt` unused. Equivalent to `xor rd, rs, ones` |
| 101000 | TEST | `rs AND rt`, flags only (`ISA-052`) |
| 101001 | TEQ | `rs XOR rt`, flags only (`ISA-053`) |
| 101010 | CMP | `rs - rt`, flags only (`ISA-014`) |
| 101100 | HALT | (`ISA-032`) |
| 101101 | ERET | supervisor (`ISA-036`) |

## Bcc `cond`

| cond | Name | Taken when |
|------|------|------------|
| 0000 | EQ | Z |
| 0001 | NE | ~Z |
| 0010 | LT | N xor V |
| 0011 | GE | ~(N xor V) |
| 0100 | LO | C (unsigned lower after CMP/SUB) |
| 0101 | HS | ~C |
| 0110 | LE | Z \| (N xor V) |
| 0111 | GT | ~(Z \| (N xor V)) |
| 1000 | MI | N |
| 1001 | PL | ~N |

Odd: `test rs, one` then `bcc NE`. Even: `bcc EQ`.

## COP0 `rs` field

| rs | Mnemonic |
|----|----------|
| 00000 | MFC0 — `rd <- csr[rt]` |
| 00100 | MTC0 — `csr[rt] <- rd` |

CSR index is the 5-bit `rt` field. Supervisor-only write (`ISA-034`).

## COP1

v1: `MFC1` / `MTC1` only (`ISA-044`). Any other COP1 funct: CAUSE=6 (`ISA-045`) so software float can run until the FPU coprocessor exists. FP registers live in the coprocessor, not the integer file.

## ABI (`ISA-046`–`ISA-050`)

Stack **grows down**, 8-byte aligned at call boundaries. `sp` is `r4`.

| Reg | Name | Role |
|-----|------|------|
| r0 | zero | wired 0 |
| r1 | one | wired 1 |
| r2 | ones | wired -1 |
| r3 | ra | return address; caller-saved |
| r4 | sp | stack pointer; callee-saved |
| r5–r8 | a0–a3 | args; **a0** is the integer return value |
| r9 | a4 / err | 5th arg / syscall errno |
| r10–r15 | t0–t5 | caller-saved |
| r16–r27 | s0–s11 | callee-saved |
| r28–r29 | t6–t7 | caller-saved |
| r30 | fp | frame pointer; callee-saved (optional use) |
| r31 | k0 | trap scratch; not for the user C ABI |

Calls: `jal` / `jalr ra, rs`. Return: `jr ra`. Callee saves `s*`, `fp`, and `sp`.

Syscall (`ISA-049`): `sys imm16`. Number = imm16. Args in `a0`–`a3`. Success: `a0` = return, `a4` = 0. Failure: `a4` ≠ 0.

## Out of this document

- Microcode ROM layout (CPU sequence)
- Memory map besides reset `PC=0` and trap `0x80`
- MUL/DIV in MOSFET hardware vs iterative microcode (ALU design)
- IEEE-754 (FPU sequence)
- 4-region MPU (later hardware; not v1)
