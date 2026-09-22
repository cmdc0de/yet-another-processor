# FPU coprocessor design (v1)

COP1 arithmetic on the existing `f0`–`f31` file. Moves stay `mfc1`/`mtc1` (`docs/isa/design.md`). Not MOSFET. Not the GPU FPGA. Not IEEE flags or compare (later).

## Format

| Knob | v1 |
|------|----|
| Format | **IEEE-754 binary32** (single) |
| Width | 32-bit word in `f0`–`f31` |
| Rounding | round ties to even |
| Status flags | none (FPU-014 later) |
| Invalid | canonical qNaN **`0x7FC00000`** |
| Divide by zero | **signed infinity** (sign of the dividend) |
| 0/0 | qNaN `0x7FC00000` |

Integer FLAGS are **not** updated. No FP condition bit in v1.

Golden results: Python 3 `struct.pack("<f", …)` / `unpack` of the same operation on Linux (binary32, not host `float` bits).

## COP1 encodings

Opcode **`010001`**. R-type fields as in the ISA (`rd|rs|rt|shamt|funct`).

Moves (unchanged):

| `rs` | Asm | |
|------|-----|--|
| 00000 | `mfc1 rd, fs` | `rd` = GPR, `rt` = `fs` |
| 00100 | `mtc1 rt, fs` | GPR `rd` field is `rt`; `rt` field = `fs` |

Arithmetic: **`rs = 10000`** (16). Other `rs` (except 0 and 4) still CAUSE=6.

```
31-26 COP1 | 25-21 fd | 20-16 rs=16 | 15-11 fs | 10-6 ft | 5-0 funct
```

`fd = fs ⊗ ft` written to `f[fd]`.

| `funct` | Asm | ⊗ |
|---------|-----|---|
| 000000 | `add.s fd, fs, ft` | + |
| 000001 | `sub.s fd, fs, ft` | − |
| 000010 | `mul.s fd, fs, ft` | × |
| 000011 | `div.s fd, fs, ft` | ÷ |

Any other COP1 `funct` with `rs=16` is CAUSE=6. User and supervisor may execute these ops.

## CAD

| Knob | v1 |
|------|----|
| HDL | Verilog IEEE 1364-2001 |
| Simulator | Icarus Verilog (`iverilog` then `vvp`) |
| Host | Linux |
| Clock | `clk` rising edge |
| Reset | synchronous, active-high `rst` |

Missing `iverilog`/`vvp` fails tests. No GUI. No SystemVerilog.

Assembler: `python3 -m compiler.asm` accepts `add.s` / `sub.s` / `mul.s` / `div.s`.

## Tree

```
fpu/
  rtl/     synthesizable later; v1 is sim-only
  sim/     testbench
```

Module **`yap_fpu`**. Does not live on the GPU FPGA.

## OS save/restore

On trap, the kernel stores `f0`–`f31` (32 LE words, `f0` at the lowest address) to the kernel stack after the integer frame, and restores them before `ERET`. `mfc1`/`mtc1` already exist for that.

## Out of this document

Named FPGA/IC, double, round-mode CSR, FCC / `c.eq.s` / FP branch, MOSFET FPU, attaching `yap_fpu` to `yap_cpu` microcode (golden execute may live in `compiler.yap_isa` for tests).
