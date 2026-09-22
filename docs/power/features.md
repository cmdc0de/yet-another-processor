# Power features

Prefix: `POWER`

Board input is 5 V. A regulator drops the CPU core to 3.3 V. Bus and MCU I/O already froze 3.3 V; this sequence is the rails that feed them. Not MOSFET cells. Not Memory + bus protocol. Not MCU. Not 5 V I/O cells (`CELL-019`).

Implementation: `hw/power/`. Tests under `compiler/tests/`. v1 is **simulation** on Linux. Named regulator on a PCB is later-generation. VIN/VDD numbers, tolerance, CAD, and regulator model are `design.md` after this catalog.

## Tree and sim

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| POWER-001 | ~~Sources under `hw/power/`~~ | done | m1 |
| POWER-002 | ~~Simulation builds and runs on Linux (dev host)~~ | done | m1 |
| POWER-003 | ~~Tests fail if the chosen simulator is missing~~ | done | m1 |

## Rails

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| POWER-004 | ~~Named 5 V system input and 0 V VSS~~ | done | m1 |
| POWER-005 | ~~Regulator from that 5 V input to a named 3.3 V VDD~~ | done | m1 |
| POWER-006 | ~~With 5 V in, simulated VDD is 3.3 V within the named tolerance (`design.md`)~~ | done | m1 |

## Domain

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| POWER-007 | ~~CPU core, SRAM/bus, and MCU I/O use the 3.3 V rail (not the 5 V input)~~ | done | m1 |

## Later generation (do not pull into m1)

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| POWER-008 | Named regulator IC on a fabricated PCB | open | later-generation |
| POWER-009 | 5 V I/O or USB with level shifters | open | later-generation |
| POWER-010 | Enable / PGOOD sequence to FPGA and MCU | open | later-generation |
| POWER-011 | Measured (bench) rails vs simulation | open | later-generation |
