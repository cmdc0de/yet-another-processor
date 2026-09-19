# CPU microarchitecture features

Prefix: `CPU`

v1 implements the frozen ISA with microcoded control and a split register file. Software still sees one 32-name file.

This sequence is the hardware contract the FPGA CPU is written from. Not HDL (FPGA CPU sequence, `emu/fpga-cpu/`). Not MOSFET boards (Physical CPU). Not the bus protocol (Memory + bus). MOSFET cells stay parallel in `lt-spice/`. A clocked model is in scope so features are testable; its path is `design.md` after this catalog.

Control-word layout, port counts, and multi-cycle vs pipeline are `design.md`, not this table.

## Datapath

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| CPU-001 | ~~32-bit datapath and 32-bit addresses~~ | implemented | m1 |
| CPU-002 | ~~PC is a datapath register; sequential fetch is `PC+4`~~ | implemented | m1 |
| CPU-003 | ~~Instruction register holds the current 32-bit instruction~~ | implemented | m1 |
| CPU-004 | ~~Split GPR file: `r0`–`r2` wired, `r3`–`r15` MOSFET bank, `r16`–`r31` IC bank; one file to software~~ | implemented | m1 |
| CPU-005 | ~~Writes to `r0`–`r2` discarded; ALU ops targeting them still update flags~~ | implemented | m1 |
| CPU-006 | ~~Discrete FLAGS (`Z N C V`), not a GPR~~ | implemented | m1 |
| CPU-007 | ~~ALU add/sub with ISA flag rules (add: C=carry; sub/cmp: C=borrow; V=signed overflow)~~ | implemented | m1 |
| CPU-008 | ALU and/or/xor/not; `Z N`; `C=V=0` | open | |
| CPU-009 | Shifter sll/srl/sra; C=last bit shifted out; `V=0` | open | |
| CPU-010 | Flags-only compare paths (`CMP`, `TEST`, `TEQ`) | open | |
| CPU-011 | MUL low 32; DIV with ÷0 → `rd=0`, `Z=1` | open | |
| CPU-012 | imm16 sign-extend, zero-extend, and LUI (`<<16`) onto the datapath | open | |
| CPU-013 | PC-relative address adder (`ADR`) | open | |
| CPU-014 | Load/store effective address `rs+sext(imm16)`; little-endian word/half/byte | open | |
| CPU-015 | Memory port: address, data, size, read/write (wire protocol is Memory + bus) | open | |
| CPU-016 | CSR file: STATUS, FLAGS, EPC, CAUSE, UBASE, ULIMIT | open | |
| CPU-017 | COP1 register file; v1 execute is MFC1/MTC1 only | open | |

## Control

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| CPU-018 | ~~Microcode store and sequencer: each ISA insn is one or more cycles~~ | implemented | m1 |
| CPU-019 | ~~Opcode / funct / Bcc cond dispatch to a microcode entry~~ | implemented | m1 |
| CPU-020 | Control word steers RF, ALU, shifter, PC, FLAGS, CSRs, memory | open | |
| CPU-021 | ~~Fetch: aligned load into IR; unaligned fetch → CAUSE=8~~ | implemented | m1 |
| CPU-022 | ~~HALT stops the sequencer~~ | implemented | m1 |
| CPU-023 | ~~Trap sequence: CAUSE, `PIE/PP←IE/P`, `P=1`, `IE=0`, EPC, `PC=0x80`~~ | implemented | m1 |
| CPU-024 | SYS sets `EPC=PC+4`; other traps set EPC to the faulting PC | open | |
| CPU-025 | ERET sequence: `IE/P←PIE/PP`, `PC←EPC` | open | |
| CPU-026 | User window check on fetch/load/store; fail → CAUSE=2 | open | |
| CPU-027 | Alignment check on load/store; fail → CAUSE=8 | open | |
| CPU-028 | User CSR write and supervisor-only ops → CAUSE=7 | open | |
| CPU-029 | Setting TE=1 → CAUSE=7; TE stays 0 | open | |
| CPU-030 | When IE=1, external IRQ → CAUSE=1 | open | |
| CPU-031 | Unimplemented COP1 op → CAUSE=6 | open | |
| CPU-032 | MOSFET bank and IC bank may take different cycle counts; the model exposes the split | open | |

## Later generation (do not pull into m1)

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| CPU-033 | Instruction cache | open | later-generation |
| CPU-034 | Data cache | open | later-generation |
| CPU-035 | Pipelined control | open | later-generation |
| CPU-036 | Page tables / TLB hardware | open | later-generation |
| CPU-037 | FPU execute (beyond moves) | open | later-generation |
| CPU-038 | 4-region MPU | open | later-generation |
