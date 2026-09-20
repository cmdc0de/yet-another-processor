# MOSFET cell library features

Prefix: `CELL`

CMOS MOSFET cells at the 3.3 V CPU core, simulated in `lt-spice/`. Software still sees the ISA; this sequence is gates, latches, and an adder bit the Physical CPU is built from.

Not Physical CPU boards. Not the SRAM bus. Not FPGA HDL. Device part numbers and pass/fail voltages are `design.md` after this catalog.

Existing `.asc` files are the start of the library; they are not a locked catalog.

## Rails and devices

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| CELL-001 | Cell tests use 3.3 V VDD and 0 V VSS | claimed | m1 |
| CELL-002 | N-channel and P-channel MOSFET models in the library (SOT-23 parts named in design.md) | claimed | m1 |
| CELL-003 | Symbols so a test schematic instantiates a cell, not only a flattened netlist | open | |

## Combinational

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| CELL-004 | CMOS inverter: logic 0 in → 1 out; 1 in → 0 out | claimed | m1 |
| CELL-005 | 2-input NAND | claimed | m1 |
| CELL-006 | 2-input NOR | open | |
| CELL-007 | 2-input AND | open | |
| CELL-008 | 2-input OR | open | |
| CELL-009 | 2-input XOR | open | |
| CELL-010 | Transmission gate (or analog mux used as one) | open | |
| CELL-011 | 2:1 logic mux | open | |
| CELL-012 | 1-bit full adder: `sum`, `cout` | open | |

## Sequential

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| CELL-013 | 1-bit static latch: holds while gated; takes a new bit when open | open | |

## Characterization and harness

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| CELL-014 | Combinational outputs sit within named VOH/VOL of the rails (values in design.md) | claimed | m1 |
| CELL-015 | Each cell in this catalog has a test schematic under `lt-spice/` | open | |
| CELL-016 | Latch hold/load is shown in simulation (not only a static DC point) | open | |
| CELL-017 | Adder checks include 0+0+cin0 and 1+1+cin1 | open | |
| CELL-018 | Tests run from the repo (script or documented batch) without a GUI | claimed | m1 |

## Later generation (do not pull into m1)

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| CELL-019 | 5 V I/O cells / level shifters | open | later-generation |
| CELL-020 | Multi-bit layout generators | open | later-generation |
| CELL-021 | Measured (bench) delay vs simulation | open | later-generation |
