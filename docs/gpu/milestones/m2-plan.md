# gpu m2

Features: GPU-007, GPU-008

## Intent

CPU-visible MMIO as in `docs/gpu/design.md`: CMD/COLOR/X0/Y0/X1/Y1. CMD=1 fills `[X0,X1) × [Y0,Y1)` in the YAP-160 backbuffer, clipped to 160×120. Testbench pokes the port, dumps PPM. m1 black-reset tests still pass. Verilog-2001 + Icarus.

## Work

- `gpu/rtl/`: MMIO write port (`addr`, `wdata`, `we` or equivalent) implementing the six registers.
- `gpu/sim/`: drive a fill (e.g. red 8×8 at origin), dump PPM.
- unittest `compiler/tests/test_gpu_m2.py`; m1 still green.

## Done

- GPU-007: software can write the backbuffer through the documented offsets
- GPU-008: rectangle fill paints COLOR inside the rect and leaves outside pixels unchanged (reset black)

## Out of scope

Later-generation 009–011. No SPI PHY, no blit-from-CPU-SRAM, no vsync.
