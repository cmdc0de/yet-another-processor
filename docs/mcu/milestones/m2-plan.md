# mcu m2

Features: MCU-007, MCU-008, MCU-009, MCU-010

## Intent

Poll MMIO devices as in `docs/mcu/design.md`: host-injected ASCII key, serial TX to the sim host, host-injected serial RX, 512-byte storage write-then-read. m1 idle-after-reset tests still pass. Verilog-2001 + Icarus.

## Work

- `hw/mcu/rtl/`: KEY_DATA / SER_DATA / STOR_* behavior; host inject ports live.
- `hw/mcu/sim/tb_m2.v`: inject, poke MMIO on negedge, `$display` results.
- unittest `compiler/tests/test_mcu_m2.py`; m1 still green.

## Done

- MCU-007: inject ASCII, STATUS KEY_READY=1, KEY_DATA read returns that byte and clears the bit
- MCU-008: write SER_DATA; sim host sees that byte (`ser_tx` + `ser_tx_stb`)
- MCU-009: inject serial byte, STATUS SER_RX_READY=1, SER_DATA read returns that byte and clears the bit
- MCU-010: write then read of one 512-byte block (LBA 0) returns the stored words

## Out of scope

Later-generation 012–017. No `irq`. No named STM32. No LBA≥16 / IDX>127 edge cases required in this slice.
