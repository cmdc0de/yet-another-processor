# CPU microarchitecture design (v1)

Multi-cycle, microcoded, **not** pipelined (`CPU-035` later). Implements `docs/isa/design.md`. FPGA HDL (`emu/fpga-cpu/`) is a later sequence and must match this cycle contract. MOSFET boards are Physical CPU. Wire protocol beyond the memory port is Memory + bus.

Clocked golden model: Python package **`compiler.yap_cpu`**, same role as `compiler.yap_isa` but **one `step()` = one clock**. Architectural state after each retired insn and at halt must match `yap_isa.Cpu`. Extra cycles are required (split RF, fetch, mem). Microcode table lives with that package (`compiler/yap_cpu/ucode.py`). v1 has no separate microcode assembler.

## Clock and sequencer

- One control-word fetch and execute per clock.
- Hidden: `IR`, `A`, `B`, `ALUOUT`, `MAR`, `MDR`, `uPC`.
- Architectural: `PC`, GPRs, FLAGS, CSRs, COP1 `f0`–`f31`, SRAM.

**`PC` holds the current instruction address until that insn retires or traps.** Fetch does not increment. Successful paths end with `PC ← PC+4` or `PC ← target`. No delay slot.

Reset: supervisor, `IE=0`, `TE=0`, `PC=0`, `CAUSE=0`, `uPC=U_FETCH`, not halted. `UBASE=0`, `ULIMIT=mem_size` (same defaults as `yap_isa.Cpu`). FLAGS=0.

`uPC` is 8 bits (**256** control words). ROM width **64 bits**, little-endian in the model; two 32-bit ICs on the board later.

### Sequencer ops (`seq`)

| `seq` | Name | Next `uPC` / effect |
|-------|------|---------------------|
| 0 | NEXT | `uPC+1` |
| 1 | DISPATCH | `uPC ← map(IR)` |
| 2 | GOTO | `uPC ← uimm` |
| 3 | HALT | `halted=1`; `uPC` unchanged |
| 4 | TRAP | trap hardware (below), then `uPC ← U_FETCH` |
| 5 | ERET | `IE/P ← PIE/PP`, `PC ← EPC`, `uPC ← U_FETCH` |
| 6 | SKIP_IF | if micro-cond then `uPC+2` else `uPC+1` |
| 7 | SKIP_UNLESS | inverse of SKIP_IF |

Reserved `uPC` bases (implementation fills the rest): `U_FETCH=0x00`. Dispatch maps unknown encodings to a TRAP-7 word.

### Trap hardware (`seq=TRAP`)

In **one** cycle:

- `CAUSE ←` code (from `uimm`, unless IRQ sampled this fetch)
- `PIE/PP ← IE/P`
- `P ← 1`, `IE ← 0`
- `EPC ← PC+4` if code is SYS (3), else `EPC ← PC`
- `PC ← 0x80`

IRQ sample: at the first fetch cycle, if `IE=1` and host `irq` pending → TRAP code 1, `EPC=PC` (insn not executed).

## Control word (64-bit)

Bit 0 is LSB.

| Bits | Field | Meaning |
|------|-------|---------|
| 2:0 | `seq` | table above |
| 10:3 | `uimm` | GOTO target or TRAP cause |
| 14:11 | `alu_op` | 0 ADD, 1 SUB, 2 AND, 3 OR, 4 XOR, 5 NOT, 6 SLL, 7 SRL, 8 SRA, 9 MUL, 10 DIV, 11 PASS_A, 12 PASS_B, 13 LUI |
| 17:15 | `a_sel` | 0 `A` (RF), 1 `PC`, 2 `EPC`, 3 `MDR`, 4 CSR rdata, 5 `0`, 6 `4`, 7 J-target `(PC+4)[31:28] \|\| IR[25:0] \|\| 00` |
| 20:18 | `b_sel` | 0 `B` (RF), 1 sext16(imm), 2 zext16(imm), 3 shamt, 4 `rt[4:0]`, 5 `4`, 6 `0`, 7 `(sext22(imm22)<<2)` |
| 23:21 | `dst` | 0 none, 1 RF, 2 `PC`, 3 `IR`, 4 `MAR`, 5 `MDR`, 6 CSR, 7 FLAGS from ALU |
| 24 | `re_a` | start RF read → `A` |
| 25 | `re_b` | start RF read → `B` |
| 26 | `we_rf` | write `ALUOUT` (or `MDR` on a load path) to `rd` |
| 27 | `we_ir` | `IR ←` mem rdata |
| 28 | `mem_re` | |
| 29 | `mem_we` | |
| 31:30 | `mem_sz` | 0 byte, 1 half, 2 word |
| 32 | `we_flags` | FLAGS from ALU this cycle |
| 33 | `re_csr` | |
| 34 | `we_csr` | |
| 35 | `we_pc` | `PC ← ALUOUT` (jumps and `PC+4`) |
| 37:36 | `idx_a` | 0 `rs`, 1 `rt`, 2 `rd`, 3 `ra` (`r3`) |
| 39:38 | `idx_b` | 0 `rs`, 1 `rt`, 2 `rd`, 3 `0` |
| 40 | `load_sext` | byte/half load sign-extend |
| 41 | `irq_chk` | sample IRQ (fetch) |
| 44:42 | `flag_mode` | 0 add, 1 sub, 2 logic, 3 shift, 4 teq, 5 test, 6 muldiv |
| 47:45 | `csr_idx` | 0 = `IR.rt`, else 1 STATUS, 2 FLAGS, 3 EPC, 4 CAUSE, 5 UBASE, 6 ULIMIT |
| 63:48 | reserved | 0 |

`PC+4` uses `a_sel=PC`, `b_sel=5` (constant 4), `alu_op=ADD`, `we_pc`. LUI uses `alu_op=LUI` (`ALUOUT = imm16<<16`).

## Split register file

One architectural file, three physical sources:

| Index | Bank | Read latency (cycles after `re_*`) | Write latency (cycles `we_rf` occupies) |
|-------|------|--------------------------------------|----------------------------------------|
| `r0`–`r2` | wired | 0 (data combinational) | n/a (write discarded) |
| `r3`–`r15` | MOSFET | **1** (`LAT_MOSFET`) | **1** |
| `r16`–`r31` | IC | **2** (`LAT_IC`) | **2** |

Raising the latencies later is a constant change; the split must remain visible (`CPU-032`).

- Two read ports, one write port.
- Sequencer **stalls** (repeats the same `uPC`, does not advance `seq`) while a started read/write’s bank is busy. Microcode is bank-agnostic.
- No write-to-read forwarding. Microcode reads operands before writeback.
- Wired reads ignore `re_*` latency; writes to `r0`–`r2` still set FLAGS if `we_flags`.

`r16`–`r31` include `s0`–`s11`, `t6`, `t7`, `fp`, `k0`. `t0`–`t5` are MOSFET (`r10`–`r15`).

## ALU and FLAGS

Combinational in the cycle operands are valid. v1 **MUL and DIV are one ALU cycle** (low 32; ÷0 → `rd=0`, `Z=1`). Physical MOSFET may later expand MUL/DIV into iterative microcode without changing the ISA; FPGA v1 matches this one-cycle rule.

`flag_mode` selects the ISA rule set (`docs/isa/design.md`). Loads, stores, and jumps: `we_flags=0`.

Shifter and mul/div share the ALU_OP map. On the board they may be separate ICs; the control word does not change.

## Memory port (`CPU-015`)

Not the SRAM board protocol.

```
addr[31:0]   byte address, naturally aligned for size
wdata[31:0]  store value in low `size` bytes (LE)
rdata[31:0]  load value in low `size` bytes (LE)
size         1, 2, or 4
re, we
```

v1 **ready next cycle** (`LAT_MEM=1`). Window and align checks occur **before** `re`/`we`. Fail → `seq=TRAP` (CAUSE 2 or 8), no SRAM write.

Byte/half extract and `load_sext` happen on the CPU side from `rdata`.

## IR fields

Hardwired from `IR` (ISA formats). Dispatch uses `opcode`; SPECIAL uses `funct`; COP0/COP1 use `rs` (MFC/MTC). Unknown opcode, unknown SPECIAL `funct`, COP0 `rs` not MFC0/MTC0 → TRAP 7. COP1 `rs` not MFC1/MTC1 → TRAP 6.

User `re_csr` allowed only for STATUS and FLAGS; any user `we_csr` or other CSR read → TRAP 7. `mtc0 STATUS` with TE=1 → TRAP 7, TE stays 0.

ERET in user → TRAP 7 (never `seq=ERET`).

## Fetch (microcode sketch)

1. `irq_chk`. If taken, trap 1.
2. If `PC % 4 ≠ 0` → trap 8.
3. If user and not `UBASE ≤ PC < ULIMIT` → trap 2.
4. `MAR ← PC`, `mem_re`, size=4; wait `LAT_MEM`; `IR ← rdata`.
5. `seq=DISPATCH`.

Execute routines read RF (stall on bank), ALU, optional mem, writeback, then `PC ← PC+4` (or target) and GOTO `U_FETCH`.

SYS: no RF ALU; `seq=TRAP` `uimm=3`.

HALT: `seq=HALT`.

## Out of this document

HDL, MOSFET schematics, cache, pipeline, page tables, FPU execute, 4-region MPU, tristate bus timing.
