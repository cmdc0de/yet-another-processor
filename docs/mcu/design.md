# MCU I/O design (v1)

Microcontroller **bridge**. CPU polls MMIO. Keyboard, serial, and storage are sim-side devices behind that port. Not GPU. Not SRAM. Not OS drivers. Not a named STM32.

## Rails

| Knob | v1 |
|------|----|
| VDD | 3.3 V (same as the bus; no 5 V part on v1) |
| VSS | 0 V (net **VSS**) |

## CAD

| Knob | v1 |
|------|----|
| HDL | Verilog IEEE 1364-2001 |
| Simulator | Icarus Verilog (`iverilog` then `vvp`) |
| Host | Linux |
| Clock | `clk` rising edge |
| Reset | synchronous, active-high `rst` |

Missing `iverilog`/`vvp` fails tests. No GUI. No SystemVerilog. Behavioral devices; not a vendor MCU.

## Tree

```
hw/mcu/
  rtl/     synthesizable later; v1 is sim-only
  sim/     testbench + host inject
```

Module: **`yap_mcu`**.

## CPU port (MMIO)

32-bit word accesses. Addresses are **byte offsets** from the MCU base (base is a later system-map choice; the MCU sees these offsets). `addr[1:0]` ignored. `re` and `we` mutually exclusive; idle both 0.

```
clk, rst
we, re
addr[7:0]
wdata[31:0]
rdata[31:0]     combinational from the addressed register
```

Writes and consume-on-read sample **posedge**. `rdata` is the value **before** that posedge (the word being consumed is visible on the consume cycle). Tests drive `we`/`re` on **negedge** (same as the bus TB).

v1 is **poll**. No `irq` pin.

### Map

| Offset | Name | Access | Meaning |
|--------|------|--------|---------|
| 0x00 | STATUS | R | bits below |
| 0x04 | KEY_DATA | R | pending key; read consumes |
| 0x08 | SER_DATA | R/W | write = TX byte; read = RX byte, consumes |
| 0x0C | STOR_LBA | R/W | block number |
| 0x10 | STOR_IDX | R/W | word index into the 512-byte buffer, 0..127 |
| 0x14 | STOR_DATA | R/W | one LE word at `STOR_IDX`; then IDX ← (IDX+1) mod 128 |
| 0x18 | STOR_CMD | W | `1` = write buffer → storage[LBA]; `2` = read storage[LBA] → buffer |

Writes to STATUS/KEY_DATA ignored. Unknown offsets: write ignored, read 0. Reads of STOR_CMD return 0.

### STATUS bits

| Bit | Name | After reset | Meaning |
|-----|------|-------------|---------|
| 0 | KEY_READY | 0 | 1 = KEY_DATA holds an unread event |
| 1 | SER_RX_READY | 0 | 1 = SER_DATA holds an unread RX byte |
| 2 | SER_TX_BUSY | 0 | v1 always 0 (TX completes on the write) |
| 3 | STOR_BUSY | 0 | v1 always 0 (CMD completes on the write) |
| 31:4 | — | 0 | |

STATUS read does **not** consume. After reset: STATUS=`0`, all data regs `0`, storage all `0`.

## Keyboard

One pending event (depth 1).

KEY_DATA: bits `[7:0]` = **ASCII** byte; `[31:8]` = 0. Press-only. No modifiers, no release.

Read KEY_DATA while KEY_READY=1 returns that byte and clears KEY_READY. Read while KEY_READY=0 returns 0.

## Serial

8-bit data, no baud, no framing (instant).

- **TX:** write SER_DATA; byte = `wdata[7:0]`. Appears on sim host that cycle (`ser_tx` + one-cycle `ser_tx_stb`).
- **RX:** depth 1. Read SER_DATA while SER_RX_READY=1 returns `[7:0]` and clears the bit. Else 0.

## Storage

| Knob | v1 |
|------|----|
| Block | **512 bytes** (128 little-endian words) |
| Capacity | **16** blocks (LBA 0..15) |
| After reset | all bytes `0` |

Buffer is MCU-local (not CPU SRAM). Fill/drain via STOR_IDX + STOR_DATA.

STOR_CMD `1`/`2` with LBA ≥ 16 is a **no-op** (buffer unchanged). STOR_IDX > 127: DATA read 0, DATA write ignored, IDX unchanged.

## Sim host ports

Not architectural. Testbench only.

```
input         key_we
input  [7:0]  key_in        // ASCII → KEY_DATA, sets KEY_READY
input         ser_rx_we
input  [7:0]  ser_rx_in     // → SER_DATA, sets SER_RX_READY
output [7:0]  ser_tx
output        ser_tx_stb    // 1-cycle pulse on CPU TX
```

Depth 1: inject while already pending **overwrites**. CPU `we`/`re` and host injects must not share a posedge in tests.

## Physical (later)

Intended board: STM32-class MCU, UART, USB HID or equivalent keyboard, SD or SPI flash. Not implemented in v1. IRQ from this bridge is MCU-017 (later).

## Out of this document

MCU part number, USB/UART/SD PHY, firmware image, OS MMIO base, bus decode onto `hw/bus/`, 5 V USB, baud rate, HID scancodes, filesystem.
