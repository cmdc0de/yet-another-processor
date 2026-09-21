# mcu m1

Features: MCU-001, MCU-002, MCU-003, MCU-004, MCU-005, MCU-006, MCU-011

## Intent

Verilog-2001 + Icarus in `hw/mcu/`: module `yap_mcu` with the poll MMIO port from `docs/mcu/design.md`. After reset, STATUS reads 0 (idle). Missing `iverilog`/`vvp` fails tests. VDD=3.3.

## Work

- `hw/mcu/rtl/` module `yap_mcu`; `hw/mcu/sim/` testbench reads STATUS after reset.
- unittest `compiler/tests/test_mcu_m1.py`.
- Host injects tied off (`key_we=0`, `ser_rx_we=0`). Drive `we`/`re` on negedge.

## Done

- MCU-001: HDL under `hw/mcu/`
- MCU-002: sim builds and runs on Linux
- MCU-003: missing Icarus fails (not skip)
- MCU-004: port has `clk`, `rst`, `we`, `re`, `addr[7:0]`, `wdata`, `rdata`
- MCU-005: sources name the seven offsets from `design.md`
- MCU-006: after reset, STATUS (0x00) reads 0
- MCU-011: MCU I/O VDD is 3.3 V

## Out of scope

MCU-007–010 (key, serial TX/RX, storage round-trip). Later-generation 012–017. No `irq`. No named STM32.
