# gpu m1

Features: GPU-001, GPU-002, GPU-003, GPU-004, GPU-005, GPU-006

## Intent

Verilog-2001 + Icarus in `gpu/`: one 160×120 RGB888 backbuffer in GPU memory. After reset the buffer is a known fill (all black `0x000000`). Testbench writes a PPM P6. Missing `iverilog`/`vvp` fails tests.

## Work

- `gpu/rtl/` backbuffer; `gpu/sim/` testbench dumps PPM.
- unittest `compiler/tests/test_gpu_m1.py`.
- PPM header `P6 160 120 255`; pixel format `docs/gpu/design.md`.

## Done

- GPU-001: HDL under `gpu/`
- GPU-002: sim builds and runs on Linux
- GPU-003: missing Icarus fails (not skip)
- GPU-004: backbuffer is GPU-local (not CPU SRAM)
- GPU-005: YAP-160 160×120, `0x00RRGGBB`
- GPU-006: dumped PPM matches the known reset fill

## Out of scope

GPU-007–008 (MMIO port, rect fill). Later-generation 009–011. No SPI PHY.
