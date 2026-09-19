# FPGA CPU emulator design (v1)

Simulation of the microcoded CPU. Implements `docs/cpu/design.md`. Guest image is YAP1 (`docs/compiler/design.md`). Architectural state after halt must match `compiler.yap_cpu` on the same image.

Not Physical CPU. Not the board SRAM protocol. Not synthesis.

## Language and simulator

| Knob | v1 |
|------|----|
| HDL | Verilog IEEE 1364-2001 |
| Simulator | Icarus Verilog (`iverilog` then `vvp`) |
| Host | Linux (this sequence’s FPGA-CPU-004) |
| Clock | `clk` rising edge |
| Reset | synchronous, **active-high** `rst`, held ≥ 1 cycle before release |

No SystemVerilog in v1 (Icarus SV is incomplete). Tests must not require a GUI.

## Tree

```
emu/fpga-cpu/
  rtl/           synthesizable later; v1 is sim-only
  sim/           testbench + Python driver
  README.md      how to run iverilog
```

Microcode image is **generated**, not hand-edited: Python `compiler.yap_cpu.ucode.build_rom()` writes `emu/fpga-cpu/rtl/ucode.hex`.

## Microcode ROM

256 × 64 bits. `$readmemh` of `ucode.hex`: 256 lines, 16 hex digits each, value = the Python `pack_cw` integer (bit 0 = LSB = `seq[0]`). Same field map as `docs/cpu/design.md`.

Regenerate the hex in the test/setup path so HDL and `yap_cpu` cannot drift.

## Memory port (testbench SRAM)

Same as `docs/cpu/design.md` CPU-015:

```
addr[31:0]   byte address
wdata[31:0]  store, low `size` bytes, LE
rdata[31:0]  load, low `size` bytes, LE
size         1, 2, or 4
re, we
```

v1 **ready next cycle** (`LAT_MEM=1`). Default SRAM **64KiB**. Window/align checks are **inside the CPU**, before `re`/`we`. Testbench SRAM does not trap.

IRQ: input `irq` sampled on fetch when `IE=1` (`irq_chk`).

## YAP1 load

Python driver, not the Verilog `$readmemh` of a raw `.yap` (header must not land in SRAM):

1. Unpack YAP1 (`compiler.yap1`).
2. Reject short file, bad magic, size mismatch.
3. Write payload bytes to a SRAM hex/bin the testbench `$readmemh`s (or poke via plusargs).
4. After `rst`, CPU `PC=entry` (v1 default 0; if entry ≠ 0 the tb sets PC).
5. Header never in SRAM.

## Driver CLI

```
python3 emu/fpga-cpu/sim.py <image.yap> [--max-cycles N]
```

Default `N=100000`. Exit **0** if `halted`, **1** if cycle cap or sim error.

After halt (or cap), print at least: `pc`, FLAGS, STATUS, CAUSE, EPC, UBASE, ULIMIT, `r0`–`r31` (hex, same idea as `yap-emu` dump) so tests can diff against `yap_cpu`.

Unittests live in `compiler/tests/` or `emu/fpga-cpu/` and shell out to this driver (or import it). They must run with `python3 -m unittest` from repo root after `iverilog` is on `PATH`.

## Reset state

Matches `docs/cpu/design.md`: supervisor, `IE=0`, `TE=0`, `PC=0`, `CAUSE=0`, `uPC=U_FETCH=0`, FLAGS=0, `UBASE=0`, `ULIMIT=mem_size`, not halted.

## Out of this document

FPGA part, pins, synthesis, on-board SRAM/tristate, caches, pipeline.
