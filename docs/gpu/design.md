# FPGA GPU design (v1)

Display engine on a **separate** FPGA from the CPU emulator. One backbuffer. OS blits through an MMIO port. Not 3D. Not MCU. Not CPU SRAM scanout.

## CAD

| Knob | v1 |
|------|----|
| HDL | Verilog IEEE 1364-2001 |
| Simulator | Icarus Verilog (`iverilog` then `vvp`) |
| Host | Linux |
| Clock | `clk` rising edge |
| Reset | synchronous, active-high `rst` |

Missing `iverilog`/`vvp` fails tests. No GUI. No SystemVerilog.

## Tree

```
gpu/
  rtl/     synthesizable later; v1 is sim-only
  sim/     testbench + PPM dump
```

## Framebuffer

| Knob | v1 |
|------|----|
| Mode name | **YAP-160** |
| Size | **160 × 120** pixels |
| Pixel | **RGB888** in a 32-bit word: `0x00RRGGBB` (bits 23:16 R, 15:8 G, 7:0 B). LE in memory. |
| Storage | GPU-local array (not CPU SRAM) |
| Origin | (0,0) top-left; `x` right, `y` down |

Index: `fb[y * 160 + x]`.

## CPU port (MMIO)

32-bit word writes. Addresses are byte offsets from the GPU base (base is a later system-map choice; the GPU itself sees these offsets).

| Offset | Name | Write |
|--------|------|--------|
| 0x00 | CMD | `1` = fill rectangle |
| 0x04 | COLOR | `0x00RRGGBB` |
| 0x08 | X0 | left, inclusive |
| 0x0C | Y0 | top, inclusive |
| 0x10 | X1 | right, **exclusive** |
| 0x14 | Y1 | bottom, **exclusive** |

Fill paints `[X0, X1) × [Y0, Y1)` with COLOR, clipped to 160×120. Empty if X1≤X0 or Y1≤Y0. One pixel is `X1=X0+1`, `Y1=Y0+1`.

Reads of these regs return the last written value (optional for tests). v1 has no IRQ.

## Sim output

Testbench writes a **PPM P6** of the backbuffer (160×120, binary RGB). That is the v1 “scanout”.

## Physical output (later)

Intended board PHY: **SPI** to an LCD. Not implemented in v1. HDMI is not the v1 choice.

## Out of this document

FPGA part number, SPI command set, HDMI, OS MMIO base address, vsync, double-buffer swap.
