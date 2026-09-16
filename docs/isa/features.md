# ISA + ABI features

Prefix: `ISA`

Three of the 32 GPR names are hardwired (no latches): `r0` = 0, `r1` = 1, `r2` = all-ones. Software still sees 32 names; 29 are writable. Physical split: 3 MOSFET ties + 13 MOSFET latches + 16 IC registers.

## Word and registers

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| ISA-001 | ~~32-bit data word and 32-bit addresses~~ | done | m1 |
| ISA-002 | ~~32 architectural GPR names `r0`–`r31`, one file to software~~ | done | m1 |
| ISA-003 | ~~Program counter is architectural (call/return and PC-relative ops can use it)~~ | done | m1 |
| ISA-054 | ~~`r0` hardwired 0; reads 0; writes discarded; ops targeting `r0` still update flags~~ | done | m1 |
| ISA-055 | ~~`r1` hardwired 1 (`0x00000001`); reads 1; writes discarded~~ | done | m1 |
| ISA-056 | ~~`r2` hardwired all-ones (`0xFFFFFFFF`); reads -1; writes discarded~~ | done | m1 |

## Flags

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| ISA-004 | ~~Flags Z, N, C, V updated by ALU and compare~~ | done | m1 |

## Integer ALU

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| ISA-005 | ~~ADD two registers, write `rd`, update flags~~ | done | m1 |
| ISA-006 | ~~SUB two registers, write `rd`, update flags~~ | done | m1 |
| ISA-007 | ~~AND two registers, write `rd`~~ | done | m1 |
| ISA-008 | ~~OR two registers, write `rd`~~ | done | m1 |
| ISA-009 | ~~XOR two registers, write `rd`~~ | done | m1 |
| ISA-010 | ~~Bitwise NOT, write `rd`~~ | done | m1 |
| ISA-011 | ~~Shift left logical~~ | done | m1 |
| ISA-012 | ~~Shift right logical~~ | implemented | m2 |
| ISA-013 | ~~Shift right arithmetic~~ | implemented | m2 |
| ISA-014 | ~~Compare two registers; set flags; no GPR write~~ | done | m1 |
| ISA-052 | ~~Bitwise AND-compare (`TEST`): AND two registers, update flags (at least Z, N), no GPR write~~ | done | m1 |
| ISA-053 | ~~Bitwise XOR-compare (`TEQ`): XOR two registers, update flags (at least Z), no GPR write~~ | done | m1 |
| ISA-015 | ~~ADD/SUB/AND/OR/XOR with immediate~~ | implemented | m2 |
| ISA-016 | ~~Integer multiply instruction~~ | implemented | m2 |
| ISA-017 | Integer divide instruction | open | |

## Memory

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| ISA-018 | Load word | open | |
| ISA-019 | Store word | open | |
| ISA-020 | Load byte | open | |
| ISA-021 | Store byte | open | |
| ISA-022 | Load halfword | open | |
| ISA-023 | Store halfword | open | |
| ISA-024 | Defined endianness for multi-byte memory (LE vs BE is `design.md`) | open | |

## Immediates and addressing

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| ISA-025 | ~~Form a 32-bit constant in a small, fixed number of instructions~~ | implemented | m2 |
| ISA-026 | ~~PC-relative address formation~~ | implemented | m2 |

## Control flow

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| ISA-027 | Unconditional jump | open | |
| ISA-028 | Jump-and-link (call) | open | |
| ISA-029 | Jump register (return / indirect) | open | |
| ISA-030 | Conditional branch on flags (EQ, NE, signed and unsigned LT/GE) | open | |
| ISA-031 | ~~NOP~~ | done | m1 |
| ISA-032 | HALT | open | |

## Privilege and protection

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| ISA-033 | User and supervisor privilege levels | open | |
| ISA-034 | Supervisor-only instructions (status, protection, privilege) | open | |
| ISA-035 | Trap/exception entry saves enough state to return | open | |
| ISA-036 | Return-from-trap | open | |
| ISA-037 | Simple memory protection (base/limit or MPU; pick in `design.md`) | open | |
| ISA-038 | Protection-violation trap | open | |
| ISA-039 | Supervisor interrupt enable/disable | open | |
| ISA-040 | External interrupt trap | open | |

## Reserved VM (ISA contract only; no v1 MMU)

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| ISA-041 | Reserved cause codes for translation miss and page fault | open | |
| ISA-042 | Reserved translation-enable control (ignored or trapped on v1) | open | |

## Coprocessor / FPU hook

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| ISA-043 | Coprocessor opcode space distinct from integer ISA | open | |
| ISA-044 | Move to/from coprocessor registers | open | |
| ISA-045 | Unimplemented coprocessor op traps (software float until FPU exists) | open | |

## ABI

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| ISA-046 | Designated stack-pointer GPR (not `r0`–`r2`) | open | |
| ISA-047 | Stack discipline (growth direction and alignment) | open | |
| ISA-048 | Argument, return-value, callee-saved, and caller-saved assignment (writable GPRs only) | open | |
| ISA-049 | Syscall ABI: trap, number, arguments, return, error | open | |
| ISA-050 | ~~Assembler names: `zero` (`r0`), `one` (`r1`), `ones` (`r2`), plus `sp`, `ra`, `a0`, …~~ | done | m1 |

## Later generation (do not pull into m1)

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| ISA-051 | Full virtual-memory programmer model (page tables, TLB) | open | later-generation |
