# Memory + bus features

Prefix: `MEMORY-BUS`

SRAM main memory and the tristate bus the CPU memory port talks to. Cycle contract is `docs/cpu/design.md` (`LAT_MEM=1`). Not the Physical CPU mem-port slice (already done). Not FPGA board bring-up. Not GPU or MCU.

Implementation: `hw/bus/` (protocol + schematic/netlist). Tests under `compiler/tests/`. Pin mapping, DQ vs wdata/rdata, and SRAM control polarity are `design.md` after this catalog.

## Protocol

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| MEMORY-BUS-001 | ~~Bus cycles at CPU clock: command this cycle, data next (`LAT_MEM=1`)~~ | done | m1 |
| MEMORY-BUS-002 | ~~CPU port maps to the bus: `addr[31:0]`, `size` ∈ {1,2,4}, `re`, `we`~~ | done | m1 |
| MEMORY-BUS-003 | ~~Bidirectional data: store drives DQ, load SRAM drives DQ, idle Hi-Z~~ | done | m2 |
| MEMORY-BUS-004 | ~~Little-endian lanes: size 1/2/4 uses the low 1/2/4 bytes~~ | done | m2 |
| MEMORY-BUS-005 | ~~SRAM control derived from `re`/`we` (`CE#`/`OE#`/`WE#` or equivalent)~~ | done | m2 |

## Tree and sim

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| MEMORY-BUS-006 | ~~Sources under `hw/bus/`~~ | done | m1 |
| MEMORY-BUS-007 | ~~Write-then-read of one aligned word returns the stored value~~ | done | m1 |
| MEMORY-BUS-008 | ~~Tests fail if the chosen simulator (`ngspice -b` and/or `iverilog`) is missing~~ | done | m1 |

## Rails

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| MEMORY-BUS-009 | ~~SRAM and bus VDD are 3.3 V~~ | done | m1 |

## Later generation (do not pull into m1)

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| MEMORY-BUS-010 | Named SRAM IC on a fabricated PCB | open | later-generation |
| MEMORY-BUS-011 | Burst / page-mode SRAM | open | later-generation |
| MEMORY-BUS-012 | Multi-master / DMA on this bus | open | later-generation |
