# MCU I/O features

Prefix: `MCU`

Microcontroller bridge for I/O other than the GPU: keyboard, serial, storage. STM32 is the candidate; the exact part is not a catalog decision. Not the GPU. Not Memory + bus. Not OS device drivers (`OS-023`). Not the 5 V / 3.3 V power sequence.

Implementation: `hw/mcu/`. Tests under `compiler/tests/`. v1 is **simulation** on Linux. Named MCU part, real PHYs, and firmware on a board are later-generation. Port map, encodings, block size, and CAD (HDL vs behavioral) are `design.md` after this catalog.

v1 is **poll** status/data. ISA-040 already exists; the bridge sourcing `irq` is later-generation, same as GPU v1.

## Tree and sim

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| MCU-001 | Sources under `hw/mcu/` | claimed | m1 |
| MCU-002 | Simulation builds and runs on Linux (dev host) | claimed | m1 |
| MCU-003 | Tests fail if the chosen simulator is missing | claimed | m1 |

## CPU port

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| MCU-004 | CPU-visible port so software can talk to the bridge | claimed | m1 |
| MCU-005 | Documented command/status map (`design.md`) | claimed | m1 |
| MCU-006 | After reset, the port shows idle: no pending input, not busy | claimed | m1 |

## Keyboard

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| MCU-007 | Software can read a host-injected key event | open | |

## Serial

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| MCU-008 | Software write of one serial byte appears on the sim host | open | |
| MCU-009 | Software can read a host-injected serial byte | open | |

## Storage

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| MCU-010 | Write then read of one storage block returns the stored bytes | open | |

## Rails

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| MCU-011 | MCU I/O VDD is 3.3 V (same as the bus) | claimed | m1 |

## Later generation (do not pull into m1)

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| MCU-012 | Named MCU part on a fabricated PCB | open | later-generation |
| MCU-013 | Real keyboard PHY (USB HID or equivalent) | open | later-generation |
| MCU-014 | Real UART PHY on a board | open | later-generation |
| MCU-015 | Real storage device (SD, SPI flash, or equivalent) | open | later-generation |
| MCU-016 | MCU firmware image for that named part | open | later-generation |
| MCU-017 | Bridge asserts CPU `irq` when a documented input is pending | open | later-generation |
